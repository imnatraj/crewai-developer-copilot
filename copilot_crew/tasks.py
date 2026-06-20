# copilot_crew/tasks.py
from typing import Optional
from crewai import Task, Agent

class CopilotTasks:
    """
    Defines the CrewAI Tasks for various Copilot execution modes.
    """
    def __init__(self):
        pass

    # --- DOCUMENTATION MODE TASKS ---

    def architecture_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Analyze the project metadata, framework patterns, and directory structures from the SQLite metadata.\n"
                "Explain the system's structural pattern (MVC, DDD, Clean Architecture, etc.) and directory layouts.\n"
                "Document the request lifecycle (how requests flow from entrypoint to database) and framework configuration.\n"
                "Highlight key architecture patterns used in the codebase.\n"
                "Distinguish clearly between FACT (facts found in the SQLite metadata) and INFERENCE (general AI patterns or assumptions)."
            ),
            expected_output="A structured markdown report describing the project's overall architectural design.",
            output_file=output_path,
            agent=agent
        )

    def route_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Retrieve all API routes and endpoint details from the SQLite routes metadata.\n"
                "Create a structured API documentation containing all controllers, request types (methods), path variables, and registered middlewares.\n"
                "For each endpoint, detail what handler function is called and where it is located.\n"
                "Verify the exact code parameters of the handler using file contents where necessary.\n"
                "Distinguish clearly between FACT (what is registered in routes table) and INFERENCE (API logic assumptions)."
            ),
            expected_output="A comprehensive API and routing documentation in markdown.",
            output_file=output_path,
            agent=agent
        )

    def validation_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Fetch validation structures from the SQLite validations table.\n"
                "Generate a validation matrix linking route schemas (Zod, Joi, Yup, Express-Validator) to endpoint paths.\n"
                "Map validation shapes (fields and rules like min length, email format) to fields.\n"
                "Audit the endpoints to detect missing validations (e.g. routes without associated schemas) and list them as security flags.\n"
                "Distinguish clearly between FACT (explicit validation declarations) and INFERENCE."
            ),
            expected_output="A detailed validation analysis matrix and audit report in markdown.",
            output_file=output_path,
            agent=agent
        )

    def dependency_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Read the module dependency pairs from the SQLite dependencies metadata.\n"
                "Map out modules, callers, and consumer counts. Identify modules that have high incoming references (consumers) vs high outgoing references.\n"
                "Detect tightly coupled components, circular dependency loops, and complex import networks.\n"
                "List all modules that should be prioritized for refactoring.\n"
                "Distinguish clearly between FACT (mapped graph dependencies) and INFERENCE (coupling risk analysis)."
            ),
            expected_output="A detailed module dependency and coupling analysis report in markdown.",
            output_file=output_path,
            agent=agent
        )

    def business_rules_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Fetch function records and route business flows from SQLite.\n"
                "Analyze the business rules, conditional logic, side effects, and calculations.\n"
                "Explain the core business workflows and calculations in clean, readable developer explanations.\n"
                "Trace key side-effects (e.g., mail dispatch, external webhooks, caches).\n"
                "Distinguish clearly between FACT (code statements) and INFERENCE (logic reasoning)."
            ),
            expected_output="A comprehensive business rules and workflows guide in markdown.",
            output_file=output_path,
            agent=agent
        )

    def database_task(self, agent: Agent, output_path: str) -> Task:
        return Task(
            description=(
                "Fetch database objects, model definitions, schemas, and migrations from SQLite.\n"
                "Document all database tables or collections, fields, and types.\n"
                "Map model relationships (e.g., One-to-Many, foreign keys) and schema-level validation constraints.\n"
                "Summarize database migrations history and database writes (data-flow paths).\n"
                "Distinguish clearly between FACT (ORM models and migration files) and INFERENCE."
            ),
            expected_output="A complete database model, relationships, and data-flow document in markdown.",
            output_file=output_path,
            agent=agent
        )

    def documentation_summary_task(self, agent: Agent, docs_dir: str, output_path: str) -> Task:
        return Task(
            description=(
                f"Gather the generated reports from the docs directory ({docs_dir}).\n"
                "Create a consolidated, high-level project summary and developer onboarding guide.\n"
                "Organize findings, verify structural consistency, and write a summary.md containing:\n"
                "- Executive Project Summary\n"
                "- System Architecture & Tech Stack overview\n"
                "- Primary Database Models and Relationships\n"
                "- Core API Routes & Validations overview\n"
                "- Key Business Logic & Side Effects\n"
                "- Refactoring and Coupling warnings\n"
                "Do NOT make up any information. Compile and style facts from other reports."
            ),
            expected_output="A consolidated project summary and developer onboarding document in markdown.",
            output_file=output_path,
            agent=agent
        )

    # --- REQUIREMENT PLANNING MODE TASKS ---

    def requirement_analysis_task(self, agent: Agent, requirement: str) -> Task:
        return Task(
            description=(
                f"Analyze the following user requirement: '{requirement}' against the codebase metadata.\n"
                "Assess the change impacts and output:\n"
                "1. Requirement Classification & Affected Domain\n"
                "2. Affected files, endpoints (APIs), services, validations, and database objects\n"
                "3. Traced affected workflows and request pipelines\n"
                "4. Implementation Complexity (Low, Medium, High)\n"
                "5. Risk Score and Confidence Score (1-10)\n"
                "6. Recommended step-by-step approach\n"
                "Ensure every item lists whether it is a FACT (found in codebase SQLite mappings) or INFERENCE."
            ),
            expected_output="A detailed requirement analysis and risk scoring plan in markdown.",
            agent=agent
        )

    def requirement_test_planning_task(self, agent: Agent, requirement: str) -> Task:
        return Task(
            description=(
                f"Design a comprehensive test plan for the requirement: '{requirement}'.\n"
                "You must output:\n"
                "1. Recommended unit tests (files, target functions, parameters to test)\n"
                "2. Recommended integration tests (endpoints, validation triggers, database transaction tests)\n"
                "3. Regression Risks & Test Plan (areas to re-verify so we don't break old functionality)\n"
                "4. Deployment Checklist\n"
                "5. Rollback Checklist\n"
                "Ensure test cases correspond to facts found in the SQLite database."
            ),
            expected_output="A detailed test plan, regression checklist, and deployment checklist in markdown.",
            agent=agent
        )

    # --- FUNCTION ANALYSIS MODE TASKS ---

    def function_analysis_task(self, agent: Agent, function_name: str) -> Task:
        return Task(
            description=(
                f"Locate the function named '{function_name}' in the SQLite metadata.\n"
                "Analyze and report the following:\n"
                "- Function Purpose\n"
                "- File Location & Line boundaries\n"
                "- Parameters and Return values\n"
                "- Direct dependencies (other functions/modules it imports/calls)\n"
                "- Callers (functions/routes that import/call this function)\n"
                "- Side effects and validations associated with this function\n"
                "- Database interactions (queries, updates) inside it\n"
                "- Risk level (Low/Medium/High) and related Business rules\n"
                "Clearly distinguish FACT from INFERENCE."
            ),
            expected_output="A complete function profile report in markdown.",
            agent=agent
        )

    # --- MODULE ANALYSIS MODE TASKS ---

    def module_analysis_task(self, agent: Agent, module_name: str) -> Task:
        return Task(
            description=(
                f"Locate the module named '{module_name}' in the SQLite metadata (matches file name or class name).\n"
                "Analyze and report:\n"
                "- Module Purpose and context in application\n"
                "- Direct dependencies (modules it imports)\n"
                "- Consumers (modules importing this module)\n"
                "- Workflows and external integrations\n"
                "- Risk Analysis (coupling score, circular dependencies)\n"
                "- Recommended refactoring or clean-up opportunities\n"
                "Clearly distinguish FACT from INFERENCE."
            ),
            expected_output="A complete module profile report in markdown.",
            agent=agent
        )

    # --- IMPACT ANALYSIS MODE TASKS ---

    def impact_analysis_task(self, agent: Agent, change_description: str) -> Task:
        return Task(
            description=(
                f"Analyze the impact of modifying: '{change_description}' across the codebase.\n"
                "Trace module dependency trees, routes, function callers, and database queries in SQLite to report:\n"
                "- Affected Files, Functions, and API Endpoints\n"
                "- Affected Database Objects & relationships\n"
                "- Affected Business Flows\n"
                "- Potential regressions and ripple effects\n"
                "- Risk Level & Complexity Score\n"
                "- Recommended Test Coverage & rollback strategies\n"
                "Clearly distinguish FACT from INFERENCE."
            ),
            expected_output="An impact analysis and regression map report in markdown.",
            agent=agent
        )
