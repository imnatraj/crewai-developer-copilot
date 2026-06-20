# database/schema.py
import sqlite3

CREATE_PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    framework TEXT NOT NULL,
    db_technologies TEXT NOT NULL,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_FILES_TABLE = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    module_name TEXT,
    size INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_ROUTES_TABLE = """
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    handler TEXT NOT NULL,
    middlewares TEXT, -- JSON array of middleware strings
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_FUNCTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    name TEXT NOT NULL,
    is_async BOOLEAN,
    params TEXT, -- JSON array of parameter strings
    return_type TEXT,
    class_name TEXT,
    is_method BOOLEAN,
    start_line INTEGER,
    end_line INTEGER,
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_VALIDATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    type TEXT NOT NULL, -- zod, joi, yup, express-validator, custom
    name TEXT NOT NULL,
    rules TEXT, -- JSON dictionary of rules
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_DEPENDENCIES_TABLE = """
CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_file TEXT NOT NULL,
    target_file TEXT NOT NULL,
    dependency_type TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_DATABASE_OBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS database_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    type TEXT NOT NULL, -- sequelize, mongoose, typeorm, prisma
    name TEXT NOT NULL,
    schema_definition TEXT, -- JSON representation of fields/columns and relationships
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_DATABASE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS database_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    name TEXT NOT NULL,
    migration_type TEXT NOT NULL, -- SQL, JS, TS
    up_script TEXT,
    down_script TEXT,
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

CREATE_BUSINESS_FLOWS_TABLE = """
CREATE TABLE IF NOT EXISTS business_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    flow_name TEXT NOT NULL,
    steps TEXT NOT NULL, -- JSON list of flow steps
    description TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

def setup_database(conn: sqlite3.Connection):
    """
    Creates all SQLite tables if they do not exist.
    """
    cursor = conn.cursor()
    cursor.execute(CREATE_PROJECTS_TABLE)
    cursor.execute(CREATE_FILES_TABLE)
    cursor.execute(CREATE_ROUTES_TABLE)
    cursor.execute(CREATE_FUNCTIONS_TABLE)
    cursor.execute(CREATE_VALIDATIONS_TABLE)
    cursor.execute(CREATE_DEPENDENCIES_TABLE)
    cursor.execute(CREATE_DATABASE_OBJECTS_TABLE)
    cursor.execute(CREATE_DATABASE_MIGRATIONS_TABLE)
    cursor.execute(CREATE_BUSINESS_FLOWS_TABLE)
    conn.commit()
