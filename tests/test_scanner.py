# tests/test_scanner.py
import pytest
from pathlib import Path
from scanner.project_scanner import ProjectScanner
from scanner.ast_parser import ASTParser

def test_project_scanner():
    dummy_dir = Path(__file__).resolve().parent / "dummy-project"
    scanner = ProjectScanner(str(dummy_dir))
    metadata = scanner.scan()

    assert metadata["project_name"] == "dummy-express-app"
    assert "Express" in metadata["frameworks"]
    assert any("Sequelize" in db for db in metadata["database_technologies"])
    assert "migrations" in metadata["migration_directories"]

def test_ast_parser_routes():
    dummy_dir = Path(__file__).resolve().parent / "dummy-project"
    index_file = dummy_dir / "src" / "index.js"
    
    parser = ASTParser()
    parsed = parser.parse_file(index_file)
    
    routes = parsed["routes"]
    # Check the routes we expect
    methods = [r["method"] for r in routes]
    paths = [r["path"] for r in routes]
    
    assert "POST" in methods
    assert "PUT" in methods
    assert "GET" in methods
    assert "/api/users" in paths
    assert "/api/users/:id" in paths

def test_ast_parser_validations():
    dummy_dir = Path(__file__).resolve().parent / "dummy-project"
    index_file = dummy_dir / "src" / "index.js"
    
    parser = ASTParser()
    parsed = parser.parse_file(index_file)
    
    validations = parsed["validations"]
    val_names = [v["name"] for v in validations]
    
    assert "CreateUserSchema" in val_names
    assert "UpdateProfileSchema" in val_names
    assert validations[0]["type"] == "zod"

def test_ast_parser_database_objects():
    dummy_dir = Path(__file__).resolve().parent / "dummy-project"
    model_file = dummy_dir / "src" / "models" / "User.js"
    
    parser = ASTParser()
    parsed = parser.parse_file(model_file)
    
    db_objects = parsed["database_objects"]
    assert len(db_objects) > 0
    assert db_objects[0]["name"] == "User"
    assert db_objects[0]["type"] == "Sequelize:Model"
