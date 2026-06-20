# database/manager.py
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from database.schema import setup_database

class DatabaseManager:
    """
    Layer 3 local SQLite Metadata Storage Manager.
    Handles connections, schema setup, data insertion, and queries.
    """
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = Path(db_path).resolve()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        setup_database(self.conn)

    def close(self):
        self.conn.close()

    def get_cursor(self):
        return self.conn.cursor()

    # --- Persistence methods ---

    def add_project(self, path: str, name: str, framework: str, db_technologies: List[str]) -> int:
        cursor = self.conn.cursor()
        db_tech_str = ",".join(db_technologies)
        
        # Check if project exists
        cursor.execute("SELECT id FROM projects WHERE path = ?", (path,))
        row = cursor.fetchone()
        if row:
            # Delete old scan metadata for this project (Cascade deletes children)
            project_id = row[0]
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            self.conn.commit()
            
        cursor.execute(
            "INSERT INTO projects (path, name, framework, db_technologies) VALUES (?, ?, ?, ?)",
            (path, name, framework, db_tech_str)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_file(self, project_id: int, path: str, module_name: Optional[str], size: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO files (project_id, path, module_name, size) VALUES (?, ?, ?, ?)",
            (project_id, path, module_name, size)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_route(self, project_id: int, file_path: str, method: str, path: str, handler: str, middlewares: List[str], description: str) -> int:
        cursor = self.conn.cursor()
        middlewares_json = json.dumps(middlewares)
        cursor.execute(
            "INSERT INTO routes (project_id, file_path, method, path, handler, middlewares, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (project_id, file_path, method, path, handler, middlewares_json, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_function(self, project_id: int, file_path: str, name: str, is_async: bool, params: List[str], return_type: str, class_name: Optional[str], is_method: bool, start_line: int, end_line: int, description: str) -> int:
        cursor = self.conn.cursor()
        params_json = json.dumps(params)
        cursor.execute(
            "INSERT INTO functions (project_id, file_path, name, is_async, params, return_type, class_name, is_method, start_line, end_line, description) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (project_id, file_path, name, is_async, params_json, return_type, class_name, is_method, start_line, end_line, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_validation(self, project_id: int, file_path: str, type_val: str, name: str, rules: str, description: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO validations (project_id, file_path, type, name, rules, description) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, file_path, type_val, name, rules, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_dependency(self, project_id: int, source_file: str, target_file: str, dependency_type: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO dependencies (project_id, source_file, target_file, dependency_type) VALUES (?, ?, ?, ?)",
            (project_id, source_file, target_file, dependency_type)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_database_object(self, project_id: int, file_path: str, type_db: str, name: str, schema_def: str, description: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO database_objects (project_id, file_path, type, name, schema_definition, description) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, file_path, type_db, name, schema_def, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_migration(self, project_id: int, file_path: str, name: str, mig_type: str, up_script: str, down_script: str, description: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO database_migrations (project_id, file_path, name, migration_type, up_script, down_script, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (project_id, file_path, name, mig_type, up_script, down_script, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_business_flow(self, project_id: int, flow_name: str, steps: str, description: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO business_flows (project_id, flow_name, steps, description) VALUES (?, ?, ?, ?)",
            (project_id, flow_name, steps, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    # --- Query methods ---

    def query_project(self, project_id: int) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else {}

    def query_routes(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM routes WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_functions(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM functions WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_validations(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM validations WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_dependencies(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM dependencies WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_database_objects(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM database_objects WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_migrations(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM database_migrations WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_business_flows(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM business_flows WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def query_files(self, project_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
