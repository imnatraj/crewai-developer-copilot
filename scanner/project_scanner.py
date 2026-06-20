import os
import json
from pathlib import Path
from typing import Dict, Any, List

class ProjectScanner:
    """
    Layer 1 Project Scanner.
    Traverses directories, reads package.json, detects frameworks,
    database technologies, ORMs, and folder structures.
    """
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists() or not self.project_path.is_dir():
            raise ValueError(f"Project path does not exist or is not a directory: {project_path}")
            
    def scan(self) -> Dict[str, Any]:
        """
        Runs the project scan and returns metadata.
        """
        package_json_path = self.find_package_json()
        pkg_data = {}
        if package_json_path:
            pkg_data = self.parse_package_json(package_json_path)
            
        frameworks = self.detect_frameworks(pkg_data)
        db_tech = self.detect_databases(pkg_data)
        structure = self.scan_directories()
        
        metadata = {
            "project_name": pkg_data.get("name", self.project_path.name),
            "version": pkg_data.get("version", "1.0.0"),
            "project_path": str(self.project_path),
            "has_package_json": package_json_path is not None,
            "package_json_details": {
                "dependencies": pkg_data.get("dependencies", {}),
                "devDependencies": pkg_data.get("devDependencies", {}),
                "scripts": pkg_data.get("scripts", {}),
                "main": pkg_data.get("main", "")
            },
            "frameworks": frameworks,
            "database_technologies": db_tech,
            "file_summary": structure["file_summary"],
            "migration_directories": structure["migration_directories"],
            "config_files": structure["config_files"],
            "all_files": structure["all_files"]
        }
        
        return metadata

    def find_package_json(self) -> Path | None:
        """
        Search for package.json in the project root.
        """
        target = self.project_path / "package.json"
        if target.exists():
            return target
        # Fallback recursive search (depth up to 3)
        for path in self.project_path.glob("**/package.json"):
            if "node_modules" not in path.parts:
                return path
        return None

    def parse_package_json(self, path: Path) -> Dict[str, Any]:
        """
        Parse package.json file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # Return empty if parsing failed
            return {}

    def detect_frameworks(self, pkg_data: Dict[str, Any]) -> List[str]:
        """
        Detect web frameworks from package dependencies.
        """
        deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
        frameworks = []
        
        indicators = {
            "express": "Express",
            "fastify": "Fastify",
            "@nestjs/core": "NestJS",
            "koa": "Koa",
            "@hapi/hapi": "Hapi",
            "next": "Next.js",
            "nuxt": "Nuxt.js",
            "sails": "Sails.js",
            "feathers": "FeathersJS"
        }
        
        for dep, name in indicators.items():
            if dep in deps:
                frameworks.append(name)
                
        if not frameworks:
            frameworks.append("Vanilla Node.js")
            
        return frameworks

    def detect_databases(self, pkg_data: Dict[str, Any]) -> List[str]:
        """
        Detect database technologies & ORMs.
        """
        deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
        dbs = []
        
        # ORM/ODMs
        orms = {
            "prisma": "Prisma",
            "sequelize": "Sequelize",
            "typeorm": "TypeORM",
            "mongoose": "Mongoose",
            "knex": "Knex.js",
            "objection": "Objection.js",
            "mikro-orm": "MikroORM"
        }
        # Databases drivers
        drivers = {
            "pg": "PostgreSQL",
            "mysql2": "MySQL",
            "sqlite3": "SQLite",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "ioredis": "Redis"
        }
        
        for dep, name in orms.items():
            if dep in deps:
                dbs.append(f"ORM:{name}")
        for dep, name in drivers.items():
            if dep in deps:
                dbs.append(f"DB:{name}")
                
        return list(set(dbs))

    def scan_directories(self) -> Dict[str, Any]:
        """
        Walk project folder, count file extensions, find migration directories and config files.
        """
        js_count = 0
        ts_count = 0
        json_count = 0
        other_count = 0
        migration_directories = []
        config_files = []
        all_files = []
        
        exclude_dirs = {
            "node_modules", ".git", "dist", "build", "coverage", 
            ".serverless", ".next", ".nuxt", "docs"
        }
        
        # Standard configuration file names
        config_names = {
            "tsconfig.json", "tsconfig.build.json", ".eslintrc", ".eslintrc.js",
            ".eslintrc.json", "prettier.config.js", ".prettierrc", "nodemon.json",
            "webpack.config.js", "vite.config.ts", "vite.config.js", "babel.config.js",
            ".env", ".env.example", ".env.development", ".env.production", "ormconfig.json"
        }
        
        # Migration folder names
        migration_indicators = {"migrations", "migration", "prisma/migrations", "db/migrations", "src/migrations"}
        
        for root, dirs, files in os.walk(self.project_path):
            # Prune directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            rel_root = os.path.relpath(root, self.project_path)
            
            # Check for migration folders
            if rel_root != ".":
                normalized_rel = rel_root.replace("\\", "/")
                # Check if path contains migration indicators
                if any(ind in normalized_rel.split("/") for ind in migration_indicators):
                    migration_directories.append(normalized_rel)
                    
            for file in files:
                filepath = Path(root) / file
                rel_file_path = str(filepath.relative_to(self.project_path)).replace("\\", "/")
                all_files.append(rel_file_path)
                
                # Check config files
                if file in config_names:
                    config_files.append(rel_file_path)
                    
                # File extension classification
                ext = filepath.suffix.lower()
                if ext in [".js", ".jsx", ".mjs", ".cjs"]:
                    js_count += 1
                elif ext in [".ts", ".tsx", ".mts", ".cts"]:
                    ts_count += 1
                elif ext == ".json":
                    json_count += 1
                else:
                    other_count += 1
                    
        return {
            "file_summary": {
                "javascript_files": js_count,
                "typescript_files": ts_count,
                "json_files": json_count,
                "other_files": other_count,
                "total_files": js_count + ts_count + json_count + other_count
            },
            "migration_directories": list(set(migration_directories)),
            "config_files": config_files,
            "all_files": all_files
        }
