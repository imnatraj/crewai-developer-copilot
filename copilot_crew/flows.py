# copilot_crew/flows.py
import os
import json
from pathlib import Path
from typing import Dict, Any, List
from crewai.flow.flow import Flow, listen, start
from crewai import Crew, Process
from copilot_crew.agents import CopilotAgents
from copilot_crew.tasks import CopilotTasks
from database.manager import DatabaseManager
import time
import random

# Try to import the server error class from google genai if available
try:
    from google.genai.errors import ServerError as GenaiServerError
except Exception:
    GenaiServerError = Exception

class DocumentationGenerationFlow(Flow):
    """
    Stateful CrewAI Flow for generating codebase documentation.
    """
    def __init__(self, api_key: str, project_path: str, docs_dir: str):
        super().__init__()
        self.api_key = api_key
        self.project_path = project_path
        self.docs_dir = Path(docs_dir).resolve()
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.agents = CopilotAgents(api_key=api_key)
        self.tasks = CopilotTasks()

    @start()
    def generate_architecture_and_routes(self):
        print("[Flow] Step 1: Generating architecture and routes documentation...")
        arch_agent = self.agents.architecture_agent()
        route_agent = self.agents.route_agent()
        
        arch_task = self.tasks.architecture_task(arch_agent, str(self.docs_dir / "architecture.md"))
        route_task = self.tasks.route_task(route_agent, str(self.docs_dir / "routes.md"))
        
        crew = Crew(
            agents=[arch_agent, route_agent],
            tasks=[arch_task, route_task],
            process=Process.sequential
        )
        crew.kickoff()

    @listen(generate_architecture_and_routes)
    def generate_dependencies_and_database(self):
        print("[Flow] Step 2: Generating module dependencies and database documentation...")
        dep_agent = self.agents.dependency_agent()
        db_agent = self.agents.database_agent()
        
        dep_task = self.tasks.dependency_task(dep_agent, str(self.docs_dir / "dependencies.md"))
        db_task = self.tasks.database_task(db_agent, str(self.docs_dir / "database.md"))
        
        crew = Crew(
            agents=[dep_agent, db_agent],
            tasks=[dep_task, db_task],
            process=Process.sequential
        )
        crew.kickoff()

    @listen(generate_dependencies_and_database)
    def generate_validations_and_business_rules(self):
        print("[Flow] Step 3: Generating schemas and business rules documentation...")
        val_agent = self.agents.validation_agent()
        biz_agent = self.agents.business_logic_agent()
        
        val_task = self.tasks.validation_task(val_agent, str(self.docs_dir / "validations.md"))
        biz_task = self.tasks.business_rules_task(biz_agent, str(self.docs_dir / "business-rules.md"))
        
        # Generate functions.md programmatically from absolute SQLite facts
        self.generate_functions_markdown()
        
        crew = Crew(
            agents=[val_agent, biz_agent],
            tasks=[val_task, biz_task],
            process=Process.sequential
        )
        crew.kickoff()

    @listen(generate_validations_and_business_rules)
    def generate_project_summary(self):
        print("[Flow] Step 4: Finalizing documentation with project summary...")
        doc_agent = self.agents.documentation_agent()
        summary_task = self.tasks.documentation_summary_task(
            doc_agent, 
            str(self.docs_dir), 
            str(self.docs_dir / "project-summary.md")
        )
        
        crew = Crew(
            agents=[doc_agent],
            tasks=[summary_task],
            process=Process.sequential
        )
        crew.kickoff()
        print("[Flow] Documentation Generation Flow Complete!")

    def generate_functions_markdown(self):
        """
        Helper method to export the list of functions programmatically as a FACT sheet.
        """
        db = DatabaseManager("metadata.db")
        cursor = db.get_cursor()
        cursor.execute("SELECT id FROM projects ORDER BY scanned_at DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return
        pid = row[0]
        funcs = db.query_functions(pid)
        
        markdown_lines = [
            "# Project Functions Fact Sheet",
            "",
            "This document is dynamically generated from deterministic AST parsing. It lists all functions, parameters, line coordinates, and types in the codebase.",
            "",
            "| File Path | Function Name | Class | Async | Parameters | Start Line | End Line |",
            "| --- | --- | --- | --- | --- | --- | --- |"
        ]
        
        for f in funcs:
            params_str = f.get("params", "[]")
            try:
                params_list = json.loads(params_str)
                params_display = ", ".join(params_list)
            except Exception:
                params_display = params_str
                
            class_display = f.get("class_name") or "-"
            is_async = "Yes" if f.get("is_async") else "No"
            
            markdown_lines.append(
                f"| {f.get('file_path')} | `{f.get('name')}` | {class_display} | {is_async} | `{params_display}` | {f.get('start_line')} | {f.get('end_line')} |"
            )
            
        funcs_file = self.docs_dir / "functions.md"
        with open(funcs_file, "w", encoding="utf-8") as file:
            file.write("\n".join(markdown_lines))
        db.close()


class RequirementPlanningFlow(Flow):
    """
    Stateful CrewAI Flow for requirement analysis and testing blueprint generation.
    """
    def __init__(self, api_key: str, requirement: str):
        super().__init__()
        self.api_key = api_key
        self.requirement = requirement
        self.agents = CopilotAgents(api_key=api_key)
        self.tasks = CopilotTasks()
        self.result = {}

    @start()
    def analyze_requirement(self):
        print(f"[Flow] Step 1: Assessing impacts and design recommendations for '{self.requirement}'...")
        impact_agent = self.agents.impact_analysis_agent()
        analysis_task = self.tasks.requirement_analysis_task(impact_agent, self.requirement)
        
        crew = Crew(
            agents=[impact_agent],
            tasks=[analysis_task],
            process=Process.sequential
        )
        res = crew.kickoff()
        # Save output in state
        self.state["analysis_report"] = res.raw

    @listen(analyze_requirement)
    def plan_regression_tests(self):
        print("[Flow] Step 2: Creating automated testing guidelines and checklists...")
        test_agent = self.agents.test_planning_agent()
        test_task = self.tasks.requirement_test_planning_task(test_agent, self.requirement)
        
        crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            process=Process.sequential
        )
        res = crew.kickoff()
        self.state["test_plan_report"] = res.raw
        print("[Flow] Requirement Planning Flow Complete!")


# --- SINGLE OPERATION DELEGATES ---

def run_function_analysis(api_key: str, function_name: str) -> str:
    """
    Runs function analysis mode.
    """
    agents = CopilotAgents(api_key=api_key)
    tasks = CopilotTasks()
    
    biz_agent = agents.business_logic_agent()
    task = tasks.function_analysis_task(biz_agent, function_name)
    
    crew = Crew(
        agents=[biz_agent],
        tasks=[task],
        process=Process.sequential
    )
    # retry loop for transient server errors (e.g., 503 due to high demand)
    attempts = 0
    max_attempts = 5
    backoff = 1.0
    while True:
        try:
            result = crew.kickoff()
            return result.raw
        except GenaiServerError as e:
            attempts += 1
            if attempts >= max_attempts:
                raise
            wait = backoff + random.random()
            print(f"[Flow] Transient server error from LLM (attempt {attempts}/{max_attempts}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
            backoff = min(backoff * 2, 16.0)
        except Exception as e:
            # If it's not the GenAI ServerError, re-raise
            raise

def run_module_analysis(api_key: str, module_name: str) -> str:
    """
    Runs module analysis mode.
    """
    agents = CopilotAgents(api_key=api_key)
    tasks = CopilotTasks()
    
    dep_agent = agents.dependency_agent()
    task = tasks.module_analysis_task(dep_agent, module_name)
    
    crew = Crew(
        agents=[dep_agent],
        tasks=[task],
        process=Process.sequential
    )
    attempts = 0
    max_attempts = 5
    backoff = 1.0
    while True:
        try:
            result = crew.kickoff()
            return result.raw
        except GenaiServerError as e:
            attempts += 1
            if attempts >= max_attempts:
                raise
            wait = backoff + random.random()
            print(f"[Flow] Transient server error from LLM (attempt {attempts}/{max_attempts}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
            backoff = min(backoff * 2, 16.0)
        except Exception:
            raise

def run_impact_analysis(api_key: str, change_description: str) -> str:
    """
    Runs change impact analysis mode.
    """
    agents = CopilotAgents(api_key=api_key)
    tasks = CopilotTasks()
    
    impact_agent = agents.impact_analysis_agent()
    task = tasks.impact_analysis_task(impact_agent, change_description)
    
    crew = Crew(
        agents=[impact_agent],
        tasks=[task],
        process=Process.sequential
    )
    attempts = 0
    max_attempts = 5
    backoff = 1.0
    while True:
        try:
            result = crew.kickoff()
            return result.raw
        except GenaiServerError as e:
            attempts += 1
            if attempts >= max_attempts:
                raise
            wait = backoff + random.random()
            print(f"[Flow] Transient server error from LLM (attempt {attempts}/{max_attempts}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
            backoff = min(backoff * 2, 16.0)
        except Exception:
            raise
