# Developer Guide — CrewAI Developer Copilot

Welcome to the CrewAI Developer Copilot development guide. This document explains the codebase design and how you can extend the scanner or agents.

---

## Codebase Architecture Layout

* **`main.py`**: The CLI router. Orchestrates the flow of scanning the project path, running SQLite persistence, and invoking CrewAI flows.
* **`scanner/project_scanner.py`**: Layer 1 directory walker and framework/database detector. Extends here if you want to support more frameworks.
* **`scanner/ast_parser.py`**: Layer 2 Tree-sitter scanner. Traverses the AST for Javascript/TypeScript source files. Add new AST traversals here (e.g. adding support for Koa routers or Objection.js models).
* **`scanner/dependency_mapper.py`**: Subprocess wrapper that maps file imports using `madge` and `dependency-cruiser`.
* **`database/schema.py` & `database/manager.py`**: Layer 3 SQLite storage structures. Add database tables or new metadata queries here.
* **`copilot_crew/tools.py`**: Custom Pydantic tools exposed to CrewAI agents. Query methods here fetch facts from `database/manager.py`.
* **`copilot_crew/agents.py`**: Defines agent characteristics (role, backstory, goals, tools). Modify agent prompts or change LLM hyperparameters here.
* **`copilot_crew/tasks.py`**: Defines agent instruction sets, task descriptions, and output targets.
* **`copilot_crew/flows.py`**: Orchestrates Crews using stateful CrewAI Flows.

---

## Extending the System

### 1. Adding support for a new validation library (e.g. Vest)
Update `scanner/ast_parser.py`:
1. Search for Vest imports or schema shapes inside `extract_validations()`.
2. Parse validation fields and write them to the `validations` table in the database.

### 2. Creating a new CrewAI Agent (e.g. Security Auditor)
1. Add a new agent definition in `copilot_crew/agents.py`:
   ```python
   def security_auditor_agent(self) -> Agent:
       return Agent(
           role="Security Auditor",
           goal="Identify potential security flaws, authentication escapes, and OWASP top-10 issues.",
           backstory="You are a whitehat security expert...",
           tools=[query_routes, query_validations, get_file_content],
           llm=self.llm
       )
   ```
2. Create a task for it in `copilot_crew/tasks.py`.
3. Add the agent and task to the Crews in `copilot_crew/flows.py`.

### 3. Adding a new CLI command (e.g. audit-security)
1. Register the command in `main.py`:
   ```python
   elif command == "audit-security":
       api_key = check_api_key()
       # Kickoff crew here...
   ```
2. Document the usage in the CLI help instructions block.
