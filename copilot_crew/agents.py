# copilot_crew/agents.py
import os
from typing import Optional
from crewai import Agent, LLM
from copilot_crew.tools import (
    get_project_metadata,
    query_routes,
    query_functions,
    query_validations,
    query_dependencies,
    query_database_objects,
    query_database_migrations,
    query_business_flows,
    get_file_content
)

class CopilotAgents:
    """
    Defines the 9 CrewAI Agents for the Developer Copilot.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            # We will use a fallback or raise, but raising is safer.
            # However, during class loading, let's keep it lazy so we don't break imports
            pass
            
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=self.api_key,
            temperature=0.2
        )

    def architecture_agent(self) -> Agent:
        return Agent(
            role="Lead System Architect",
            goal="Analyze codebase structures, frameworks, and request lifecycles to produce structural system documentation.",
            backstory="You are an expert software architect with a background in designing large-scale Node.js/TypeScript codebases. You map out folders, structural layouts, and framework structures easily from code facts.",
            tools=[get_project_metadata, query_dependencies, query_routes, query_business_flows],
            llm=self.llm,
            verbose=True
        )

    def route_agent(self) -> Agent:
        return Agent(
            role="API Design Expert",
            goal="Document routes, endpoints, middlewares, controller bindings, and request lifecycles.",
            backstory="You specialize in REST API design and endpoint structures. You document route controllers, parameters, and active middlewares to make endpoints easy to understand for developers.",
            tools=[query_routes, query_functions, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def validation_agent(self) -> Agent:
        return Agent(
            role="Input Security and Validation Auditor",
            goal="Generate complete validation matrices, map schema shapes to route request inputs, and identify missing validations.",
            backstory="You are a security-conscious engineer obsessed with input sanitation. You verify that all API inputs are properly validated using Zod, Joi, or Yup, and identify areas susceptible to injections or type bypasses.",
            tools=[query_validations, query_routes, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def dependency_agent(self) -> Agent:
        return Agent(
            role="Dependency Management Analyst",
            goal="Analyze dependencies and module relationships, trace caller/callee paths, and flag structural coupling or circular imports.",
            backstory="You are a dependency tree expert. You know how modules couple together and you help developers refactor code by showing them module networks and pointing out modules that are too tightly coupled.",
            tools=[query_dependencies, get_project_metadata],
            llm=self.llm,
            verbose=True
        )

    def business_logic_agent(self) -> Agent:
        return Agent(
            role="Business Rules Analyst",
            goal="Explain function actions, workflows, complex business rules, and side effects within modules.",
            backstory="You are a business systems translator. You read source code functions and explain their actions, conditional logic, side effects, and calculations in clear business terms.",
            tools=[query_functions, query_business_flows, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def database_agent(self) -> Agent:
        return Agent(
            role="Database Administrator and Data Modeler",
            goal="Explain database tables, model fields, entities, relationships, database-level validation, and traces schema migrations.",
            backstory="You are a database architect. You map relationships between collections or tables, describe database-level constraints, trace schema migrations, and explain how data flows into and out of the database.",
            tools=[query_database_objects, query_database_migrations, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def impact_analysis_agent(self) -> Agent:
        return Agent(
            role="Risk Assessment and Impact Analyst",
            goal="Analyze proposed requirements or logic updates and identify all affected files, APIs, database components, and business logic. Assess risk scores.",
            backstory="You are a quality gatekeeper. You analyze proposed updates, map out potential ripple effects across the application graph, identify regression surfaces, and score implementation risks.",
            tools=[query_dependencies, query_routes, query_database_objects, query_business_flows, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def test_planning_agent(self) -> Agent:
        return Agent(
            role="Lead QA Engineer",
            goal="Generate comprehensive regression test suites, unit tests, integration test scripts, database migration tests, and deployment/rollback checklists.",
            backstory="You are a QA automation expert. You design robust test scenarios matching database, route, and function signatures. You generate test plans that assure absolute codebase reliability.",
            tools=[query_functions, query_routes, query_validations, get_file_content],
            llm=self.llm,
            verbose=True
        )

    def documentation_agent(self) -> Agent:
        return Agent(
            role="Technical Writer",
            goal="Consolidate the outputs of other analysis agents into formatted, professional final reports.",
            backstory="You are a seasoned technical writer with experience writing clean developer documentation, system descriptions, and summaries. You verify styling and organize reports logically.",
            tools=[get_project_metadata],
            llm=self.llm,
            verbose=True
        )
