# main.py
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import local modules
from scanner.project_scanner import ProjectScanner
from scanner.ast_parser import ASTParser, PrismaParser
from scanner.dependency_mapper import DependencyMapper
from database.manager import DatabaseManager
from copilot_crew.flows import (
    DocumentationGenerationFlow, 
    RequirementPlanningFlow,
    run_function_analysis,
    run_module_analysis,
    run_impact_analysis
)
from copilot_crew.tools import set_db_manager

console = Console()

def print_help():
    help_text = """
[bold cyan]CrewAI Developer Copilot CLI[/bold cyan]

[bold yellow]Usage:[/bold yellow]
  python main.py <command> [arguments]

[bold yellow]Commands:[/bold yellow]
  [green]document[/green] <path_to_project>        Scan a codebase, build a knowledge base, and generate markdown docs.
  [green]plan[/green] "<requirement>"            Analyze a proposed feature requirement and generate implementation & test plans.
  [green]analyze-function[/green] <function>    Examine a function's parameters, return types, callers, and risk level.
  [green]analyze-module[/green] <module>        Examine a service or module, mapping its dependencies and refactor spots.
  [green]impact[/green] "<change_description>"   Trace code paths and map regression risks for a proposed code change.
"""
    console.print(help_text)

def check_api_key() -> str:
    """
    Validate GEMINI_API_KEY presence and basic format.
    """
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        console.print(
            Panel(
                "[bold red]Error: GEMINI_API_KEY is not configured.[/bold red]\n\n"
                "Create a Gemini API key in Google AI Studio and add it to your .env file:\n\n"
                "[bold]GEMINI_API_KEY=your_api_key_here[/bold]",
                title="Configuration Error",
                border_style="red",
            )
        )
        sys.exit(1)

    # Basic validation
    if len(key) < 20:
        console.print(
            Panel(
                "[bold red]Invalid GEMINI_API_KEY detected.[/bold red]\n\n"
                "The configured value appears too short to be a valid API credential.\n"
                "Verify your .env file and generate a new key if necessary.",
                title="Configuration Error",
                border_style="red",
            )
        )
        sys.exit(1)

    return key
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        console.print(Panel(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]\n\n"
            "Please set the key in your shell or add it to a [bold].env[/bold] file:\n"
            "export GEMINI_API_KEY='your-gemini-api-key'",
            title="Configuration Error",
            border_style="red"
        ))
        sys.exit(1)
    return key

def run_scan(project_path: str, db_manager: DatabaseManager) -> int:
    """
    Executes Layer 1 and Layer 2 scanning, persisting facts to SQLite (Layer 3).
    """
    scanner = ProjectScanner(project_path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        
        # Step 1: Scan project layout & package.json
        progress.add_task(description="Scanning project directory and configs...", total=None)
        metadata = scanner.scan()
        
        # Step 2: Persist Project
        project_id = db_manager.add_project(
            path=metadata["project_path"],
            name=metadata["project_name"],
            framework=" / ".join(metadata["frameworks"]),
            db_technologies=metadata["database_technologies"]
        )
        
        # Save files list
        for file_rel in metadata["all_files"]:
            full_path = Path(project_path) / file_rel
            size = full_path.stat().st_size if full_path.exists() else 0
            db_manager.add_file(project_id, file_rel, Path(file_rel).stem, size)

        # Step 3: Run Node module dependency analysis
        progress.add_task(description="Extracting package dependencies (madge/depcruise)...", total=None)
        dep_mapper = DependencyMapper()
        deps = dep_mapper.get_dependencies(project_path)
        for dep in deps:
            db_manager.add_dependency(project_id, dep["source"], dep["target"], dep["type"])

        # Step 4: Parse AST
        progress.add_task(description="Parsing JS/TS source code AST (tree-sitter)...", total=None)
        ast_parser = ASTParser()
        prisma_parser = PrismaParser()
        
        for file_rel in metadata["all_files"]:
            full_path = Path(project_path) / file_rel
            ext = full_path.suffix.lower()
            if ext in [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]:
                parsed = ast_parser.parse_file(full_path)
                
                # Persist parsed entities
                for r in parsed["routes"]:
                    db_manager.add_route(project_id, file_rel, r["method"], r["path"], r["handler"], r["middlewares"], r["description"])
                for f in parsed["functions"]:
                    db_manager.add_function(project_id, file_rel, f["name"], f["is_async"], f["params"], f["return_type"], f["class_name"], f["is_method"], f["start_line"], f["end_line"], f["description"])
                for v in parsed["validations"]:
                    db_manager.add_validation(project_id, file_rel, v["type"], v["name"], v["rules"], v["description"])
                for o in parsed["database_objects"]:
                    db_manager.add_database_object(project_id, file_rel, o["type"], o["name"], o["schema_definition"], o["description"])
                for fl in parsed["flows"]:
                    db_manager.add_business_flow(project_id, fl["flow_name"], fl["steps"], fl["description"])
                    
            elif ext == ".prisma":
                parsed_prisma = prisma_parser.parse(full_path)
                for o in parsed_prisma:
                    db_manager.add_database_object(project_id, file_rel, o["type"], o["name"], o["schema_definition"], o["description"])

        # Step 5: Scan migration directories
        progress.add_task(description="Scanning database migrations history...", total=None)
        for mig_dir in metadata["migration_directories"]:
            dir_path = Path(project_path) / mig_dir
            if dir_path.exists() and dir_path.is_dir():
                for m_file in os.listdir(dir_path):
                    m_path = dir_path / m_file
                    if m_path.is_file() and m_path.suffix.lower() in [".sql", ".js", ".ts"]:
                        m_rel = str(m_path.relative_to(project_path)).replace("\\", "/")
                        content = ""
                        try:
                            with open(m_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                        except Exception:
                            pass
                        db_manager.add_migration(project_id, m_rel, m_file, m_path.suffix.lower().replace(".", ""), content, "", f"Migration file {m_file}")

    return project_id

def display_scan_summary(db_manager: DatabaseManager, project_id: int):
    project = db_manager.query_project(project_id)
    routes = db_manager.query_routes(project_id)
    funcs = db_manager.query_functions(project_id)
    vals = db_manager.query_validations(project_id)
    objs = db_manager.query_database_objects(project_id)
    files = db_manager.query_files(project_id)
    migs = db_manager.query_migrations(project_id)

    console.print(Panel(
        f"[bold green]Scanning Completed Successfully![/bold green]\n\n"
        f"[bold]Project Name:[/bold] {project['name']}\n"
        f"[bold]Path:[/bold] {project['path']}\n"
        f"[bold]Web Framework:[/bold] {project['framework']}\n"
        f"[bold]Database technologies detected:[/bold] {project['db_technologies'] or 'None'}",
        title="Scanner Output Summary",
        border_style="green"
    ))

    table = Table(title="Knowledge Base Extracted Facts")
    table.add_column("Fact Type", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    
    table.add_row("Scanned Files", str(len(files)))
    table.add_row("API Endpoints (Routes)", str(len(routes)))
    table.add_row("Functions & Methods", str(len(funcs)))
    table.add_row("Input Validations (Zod/Joi/Yup)", str(len(vals)))
    table.add_row("DB Schema Tables/Models", str(len(objs)))
    table.add_row("Database Migrations", str(len(migs)))
    
    console.print(table)

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]

    if command == "document":
        if len(sys.argv) < 3:
            console.print("[bold red]Error: Path to project is required.[/bold red]\nUsage: python main.py document /path/to/project")
            sys.exit(1)
            
        proj_path = sys.argv[2]
        if not os.path.isdir(proj_path):
            console.print(f"[bold red]Error: {proj_path} is not a valid directory.[/bold red]")
            sys.exit(1)
            
        # Store metadata.db inside the target project directory so each project keeps its own facts
        project_db_path = Path(proj_path) / "metadata.db"
        db_manager = DatabaseManager(str(project_db_path))
        # Ensure tools and agents use the same DB instance
        set_db_manager(db_manager)
        
        console.print(f"\n[bold yellow]Starting analysis for codebase at {proj_path}...[/bold yellow]\n")
        project_id = run_scan(proj_path, db_manager)
        display_scan_summary(db_manager, project_id)
        
        api_key = check_api_key()
        
        # Start CrewAI Flows
        docs_dir = Path(proj_path) / "docs"
        console.print(f"\n[bold yellow]Initializing CrewAI Flow. Saving markdown documents to {docs_dir}...[/bold yellow]\n")
        
        flow = DocumentationGenerationFlow(
            api_key=api_key,
            project_path=proj_path,
            docs_dir=str(docs_dir)
        )
        flow.kickoff()
        
        console.print("\n[bold green]✔ All analysis reports created inside your project's docs/ directory.[/bold green]\n")
        db_manager.close()

    elif command == "plan":
        if len(sys.argv) < 3:
            console.print("[bold red]Error: Requirement statement is required.[/bold red]\nUsage: python main.py plan \"requirement string\"")
            sys.exit(1)
            
        requirement = sys.argv[2]
        api_key = check_api_key()
        
        # Verify a project exists in the database
        db_manager = DatabaseManager("metadata.db")
        try:
            get_latest_project_id = db_manager.get_cursor()
            get_latest_project_id.execute("SELECT id FROM projects LIMIT 1")
            if not get_latest_project_id.fetchone():
                console.print("[bold red]Error: No project metadata found in database. Run 'document' command first to scan your codebase.[/bold red]")
                sys.exit(1)
        except Exception:
            console.print("[bold red]Error: Knowledge base database not initialized. Run 'document' command first.[/bold red]")
            sys.exit(1)
        finally:
            db_manager.close()
            
        console.print(f"\n[bold yellow]Running requirement planning for requirement: '{requirement}'...[/bold yellow]\n")
        
        flow = RequirementPlanningFlow(api_key=api_key, requirement=requirement)
        flow.kickoff()
        
        console.print(Panel(flow.state.get("analysis_report", ""), title="Requirement Assessment (Layer 4 Architecture & Impact)", border_style="cyan"))
        console.print(Panel(flow.state.get("test_plan_report", ""), title="Test Blueprints & QA Checklists", border_style="green"))

    elif command == "analyze-function":
        # Accept: python main.py analyze-function <function_name> [--path <project_path>]
        if len(sys.argv) < 3:
            console.print("[bold red]Error: Function name is required.[/bold red]\nUsage: python main.py analyze-function <function_name> [--path <project_path>]")
            sys.exit(1)

        args = sys.argv[2:]
        func_name = args[0]

        # Optional path flag
        proj_path = None
        if "--path" in args:
            try:
                idx = args.index("--path")
                proj_path = args[idx + 1]
            except Exception:
                console.print("[bold red]Error: --path requires a value.[/bold red]")
                sys.exit(1)
        elif "-p" in args:
            try:
                idx = args.index("-p")
                proj_path = args[idx + 1]
            except Exception:
                console.print("[bold red]Error: -p requires a value.[/bold red]")
                sys.exit(1)

        api_key = check_api_key()

        # If a project path was provided, use its metadata DB for tools
        if proj_path:
            project_db_path = Path(proj_path) / "metadata.db"
            if not project_db_path.exists():
                console.print(f"[bold red]Error: No metadata database found at {project_db_path}. Run 'document' on that project first.[/bold red]")
                sys.exit(1)
            db_manager = DatabaseManager(str(project_db_path))
            set_db_manager(db_manager)

        console.print(f"\n[bold yellow]Running static function profile analysis for '{func_name}'...[/bold yellow]\n")
        report = run_function_analysis(api_key, func_name)
        console.print(Panel(report, title=f"Function Profile: {func_name}", border_style="cyan"))

    elif command == "analyze-module":
        # Accept: python main.py analyze-module <module_name> [--path <project_path>]
        if len(sys.argv) < 3:
            console.print("[bold red]Error: Module name is required.[/bold red]\nUsage: python main.py analyze-module <module_name> [--path <project_path>]")
            sys.exit(1)

        args = sys.argv[2:]
        mod_name = args[0]
        proj_path = None
        if "--path" in args:
            try:
                idx = args.index("--path")
                proj_path = args[idx + 1]
            except Exception:
                console.print("[bold red]Error: --path requires a value.[/bold red]")
                sys.exit(1)

        api_key = check_api_key()
        if proj_path:
            project_db_path = Path(proj_path) / "metadata.db"
            if not project_db_path.exists():
                console.print(f"[bold red]Error: No metadata database found at {project_db_path}. Run 'document' on that project first.[/bold red]")
                sys.exit(1)
            db_manager = DatabaseManager(str(project_db_path))
            set_db_manager(db_manager)

        console.print(f"\n[bold yellow]Running module relationship analysis for '{mod_name}'...[/bold yellow]\n")
        report = run_module_analysis(api_key, mod_name)
        console.print(Panel(report, title=f"Module Profile: {mod_name}", border_style="cyan"))

    elif command == "impact":
        # Accept: python main.py impact "<description>" [--path <project_path>]
        if len(sys.argv) < 3:
            console.print("[bold red]Error: Change description is required.[/bold red]\nUsage: python main.py impact \"description of change\" [--path <project_path>]")
            sys.exit(1)

        args = sys.argv[2:]
        desc = args[0]
        proj_path = None
        if "--path" in args:
            try:
                idx = args.index("--path")
                proj_path = args[idx + 1]
            except Exception:
                console.print("[bold red]Error: --path requires a value.[/bold red]")
                sys.exit(1)

        api_key = check_api_key()
        if proj_path:
            project_db_path = Path(proj_path) / "metadata.db"
            if not project_db_path.exists():
                console.print(f"[bold red]Error: No metadata database found at {project_db_path}. Run 'document' on that project first.[/bold red]")
                sys.exit(1)
            db_manager = DatabaseManager(str(project_db_path))
            set_db_manager(db_manager)

        console.print(f"\n[bold yellow]Assessing ripple impact for proposed modification: '{desc}'...[/bold yellow]\n")
        report = run_impact_analysis(api_key, desc)
        console.print(Panel(report, title="Ripple Change Impact Matrix", border_style="red"))

    else:
        console.print(f"[bold red]Unknown command: {command}[/bold red]")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
