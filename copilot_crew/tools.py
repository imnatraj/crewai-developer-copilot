# copilot_crew/tools.py
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from crewai.tools import tool
from database.manager import DatabaseManager

# Global DB manager instance that tools will resolve
_db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        # Default local database file name
        _db_manager = DatabaseManager("metadata.db")
    return _db_manager

def get_latest_project_id(db: DatabaseManager) -> int:
    """
    Helper to get the most recently scanned project ID.
    """
    cursor = db.get_cursor()
    cursor.execute("SELECT id FROM projects ORDER BY scanned_at DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        return row[0]
    raise ValueError("No projects found in the metadata database. Run a scan/documentation command first.")

@tool("Get Project Metadata")
def get_project_metadata() -> str:
    """
    Retrieves high-level metadata about the scanned project (framework, name, versions, database technologies, file summary).
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        project = db.query_project(pid)
        return json.dumps(project, indent=2)
    except Exception as e:
        return f"Error retrieving project metadata: {str(e)}"

@tool("Query Project Routes")
def query_routes() -> str:
    """
    Retrieves all web API routes, endpoints, methods, and handlers found in the project.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        routes = db.query_routes(pid)
        # Parse middleware list if stored as json string
        for r in routes:
            if isinstance(r.get("middlewares"), str):
                try:
                    r["middlewares"] = json.loads(r["middlewares"])
                except Exception:
                    pass
        return json.dumps(routes, indent=2)
    except Exception as e:
        return f"Error retrieving routes: {str(e)}"

@tool("Query Project Functions")
def query_functions() -> str:
    """
    Retrieves list of all classes, methods, and helper functions found in the codebase.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        funcs = db.query_functions(pid)
        for f in funcs:
            if isinstance(f.get("params"), str):
                try:
                    f["params"] = json.loads(f["params"])
                except Exception:
                    pass
        return json.dumps(funcs, indent=2)
    except Exception as e:
        return f"Error retrieving functions: {str(e)}"

@tool("Query Project Validations")
def query_validations() -> str:
    """
    Retrieves all input validators (Zod schemas, Joi configurations, Yup validation layers).
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        vals = db.query_validations(pid)
        for v in vals:
            if isinstance(v.get("rules"), str):
                try:
                    v["rules"] = json.loads(v["rules"])
                except Exception:
                    pass
        return json.dumps(vals, indent=2)
    except Exception as e:
        return f"Error retrieving validations: {str(e)}"

@tool("Query Project Dependencies")
def query_dependencies() -> str:
    """
    Retrieves the inter-module dependency mappings and links captured by madge and dependency-cruiser.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        deps = db.query_dependencies(pid)
        return json.dumps(deps, indent=2)
    except Exception as e:
        return f"Error retrieving dependencies: {str(e)}"

@tool("Query Database Schema and Models")
def query_database_objects() -> str:
    """
    Retrieves all database tables, columns, ORM definitions, Mongoose schemas, and TypeORM entities.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        objs = db.query_database_objects(pid)
        for o in objs:
            if isinstance(o.get("schema_definition"), str):
                try:
                    o["schema_definition"] = json.loads(o["schema_definition"])
                except Exception:
                    pass
        return json.dumps(objs, indent=2)
    except Exception as e:
        return f"Error retrieving database objects: {str(e)}"

@tool("Query Database Migrations")
def query_database_migrations() -> str:
    """
    Retrieves the folder list and history metadata of database schema migrations.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        migs = db.query_migrations(pid)
        return json.dumps(migs, indent=2)
    except Exception as e:
        return f"Error retrieving migrations: {str(e)}"

@tool("Query Project Business Flows")
def query_business_flows() -> str:
    """
    Retrieves route execution sequences (e.g. Route -> Validation -> Controller -> Service -> Model).
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        flows = db.query_business_flows(pid)
        for f in flows:
            if isinstance(f.get("steps"), str):
                try:
                    f["steps"] = json.loads(f["steps"])
                except Exception:
                    pass
        return json.dumps(flows, indent=2)
    except Exception as e:
        return f"Error retrieving business flows: {str(e)}"

@tool("Get Raw File Content")
def get_file_content(filepath: str) -> str:
    """
    Reads and returns the complete text content of a specific source code file from the codebase.
    """
    try:
        db = get_db_manager()
        pid = get_latest_project_id(db)
        project = db.query_project(pid)
        proj_path = Path(project["path"])
        
        target = (proj_path / filepath).resolve()
        if not target.exists():
            # If path is already absolute
            target = Path(filepath).resolve()
            
        if not str(target).startswith(str(proj_path)):
            return f"Security Error: Cannot read files outside of project root directory {proj_path}"
            
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file content: {str(e)}"
