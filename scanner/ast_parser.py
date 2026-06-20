import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from tree_sitter import Language, Parser, Node
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts

# Initialize Tree-sitter languages
JS_LANGUAGE = Language(tsjs.language())
TS_LANGUAGE = Language(tsts.language_typescript())
TSX_LANGUAGE = Language(tsts.language_tsx())

class ASTParser:
    """
    Layer 2 Static Analysis AST Engine using Tree-sitter.
    Extracts routes, functions, validations, DB schemas, migrations, and data flows.
    """
    def __init__(self):
        pass

    def _get_parser(self, filepath: Path) -> Parser:
        ext = filepath.suffix.lower()
        parser = Parser()
        if ext in [".ts", ".mts", ".cts"]:
            parser.language = TS_LANGUAGE
        elif ext == ".tsx":
            parser.language = TSX_LANGUAGE
        else:
            parser.language = JS_LANGUAGE
        return parser

    def parse_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Parses a file and extracts all metadata details.
        """
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
        except Exception:
            return {"routes": [], "functions": [], "validations": [], "database_objects": [], "flows": []}

        parser = self._get_parser(filepath)
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node

        rel_path = str(filepath).replace("\\", "/")

        routes = self.extract_routes(root_node, code, rel_path)
        functions = self.extract_functions(root_node, code, rel_path)
        validations = self.extract_validations(root_node, code, rel_path)
        db_objects = self.extract_database_objects(root_node, code, rel_path)
        flows = self.trace_data_flows(root_node, code, rel_path, routes, functions)

        return {
            "routes": routes,
            "functions": functions,
            "validations": validations,
            "database_objects": db_objects,
            "flows": flows
        }

    def get_node_text(self, node: Node, code: str) -> str:
        """
        Extracts the text corresponding to a node from the code string.
        """
        try:
            return code[node.start_byte:node.end_byte]
        except Exception:
            return ""

    def find_descendants(self, node: Node, types: List[str]) -> List[Node]:
        """
        Recursively finds all descendants of specific types.
        """
        results = []
        if node.type in types:
            results.append(node)
        for child in node.children:
            results.extend(self.find_descendants(child, types))
        return results

    def extract_routes(self, root_node: Node, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract Express, Fastify, and NestJS routes.
        """
        routes = []

        # 1. NestJS Controllers and Routes (Decorators)
        # Look for class declarations
        classes = self.find_descendants(root_node, ["class_declaration"])
        for cls in classes:
            decorators = self.find_descendants(cls, ["decorator"])
            controller_prefix = ""
            is_controller = False
            
            for dec in decorators:
                dec_text = self.get_node_text(dec, code)
                if "@Controller" in dec_text:
                    is_controller = True
                    # Extract Controller path
                    match = re.search(r"@Controller\(['\"]([^'\"]+)['\"]\)", dec_text)
                    if match:
                        controller_prefix = match.group(1)
            
            if is_controller:
                # Scan methods in the controller class
                methods = self.find_descendants(cls, ["method_definition"])
                for method in methods:
                    method_decorators = self.find_descendants(method, ["decorator"])
                    for m_dec in method_decorators:
                        m_dec_text = self.get_node_text(m_dec, code)
                        http_match = re.search(r"@(Get|Post|Put|Delete|Patch)\(['\"]([^'\"]*)['\"]\)", m_dec_text)
                        if http_match:
                            http_method = http_match.group(1).upper()
                            sub_path = http_match.group(2)
                            
                            # Combine controller prefix and method path
                            full_path = "/" + "/".join(filter(None, [controller_prefix, sub_path]))
                            full_path = full_path.replace("//", "/")
                            
                            # Get method name
                            method_name_node = method.child_by_field_name("name")
                            handler_name = self.get_node_text(method_name_node, code) if method_name_node else "anonymous"
                            
                            routes.append({
                                "file_path": file_path,
                                "method": http_method,
                                "path": full_path,
                                "handler": handler_name,
                                "middlewares": [],
                                "description": f"NestJS endpoint mapping to {handler_name}()"
                            })

        # 2. Express & Fastify Call-Expression Routes (router.get, app.post, etc.)
        calls = self.find_descendants(root_node, ["call_expression"])
        express_methods = {"get", "post", "put", "delete", "patch", "use"}
        
        for call in calls:
            callee_text = self.get_node_text(call.child_by_field_name("function"), code)
            
            # Match router.get('/path', ...) or app.post(...)
            # Typically callee is a member_expression (e.g. router.get)
            match = re.search(r"(\w+)\.(get|post|put|delete|patch|use)$", callee_text)
            if match:
                var_name = match.group(1)
                method = match.group(2).upper()
                
                # We want to filter out non-routing usage of .get or .use
                if var_name in ["console", "fs", "path", "process", "res", "req", "db"]:
                    continue
                    
                arguments_node = call.child_by_field_name("arguments")
                if not arguments_node or len(arguments_node.children) < 3:  # (open_paren, arg1, close_paren)
                    continue
                
                # Check first argument (usually path string literal)
                first_arg = arguments_node.children[1]
                first_arg_text = self.get_node_text(first_arg, code)
                
                # Extract path from string literal
                path_match = re.search(r"^['\"]([^'\"]+)['\"]$", first_arg_text)
                if path_match:
                    route_path = path_match.group(1)
                    
                    # Extract middlewares and handler
                    args_list = []
                    # Skip paren and first arg
                    for child in arguments_node.children[2:-1]:
                        if child.type not in [",", "comment"]:
                            args_list.append(child)
                            
                    middlewares = []
                    handler = "anonymous"
                    
                    if len(args_list) > 0:
                        # Last argument is typically the handler
                        handler_node = args_list[-1]
                        handler = self.get_node_text(handler_node, code)
                        if len(handler) > 100:  # Truncate inline arrow functions
                            handler = handler.split("{")[0].strip() + " => { ... }"
                        
                        # Others are middlewares
                        for middleware_node in args_list[:-1]:
                            m_text = self.get_node_text(middleware_node, code)
                            middlewares.append(m_text)
                            
                    routes.append({
                        "file_path": file_path,
                        "method": method,
                        "path": route_path,
                        "handler": handler,
                        "middlewares": middlewares,
                        "description": f"Express route handling {method} {route_path}"
                    })

        return routes

    def extract_functions(self, root_node: Node, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract functions, async functions, arrow functions, and methods.
        """
        functions = []

        # 1. Standard Function Declarations
        func_decls = self.find_descendants(root_node, ["function_declaration"])
        for node in func_decls:
            name_node = node.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else "anonymous"
            
            # Detect async
            is_async = "async" in self.get_node_text(node, code).split("(")[0]
            
            # Extract parameters
            params_node = node.child_by_field_name("parameters")
            params = []
            if params_node:
                for child in params_node.children:
                    if child.type in ["identifier", "formal_parameter"]:
                        params.append(self.get_node_text(child, code))
                        
            # Line coordinates (1-indexed)
            start_line = code.count("\n", 0, node.start_byte) + 1
            end_line = code.count("\n", 0, node.end_byte) + 1
            
            functions.append({
                "file_path": file_path,
                "name": name,
                "is_async": is_async,
                "params": params,
                "return_type": "any",  # static analysis heuristic
                "class_name": "",
                "is_method": False,
                "start_line": start_line,
                "end_line": end_line,
                "description": f"Function {name}()"
            })

        # 2. Variable Declarations with Arrow Functions or Function Expressions
        # const myFunc = async (a, b) => { ... }
        var_declarators = self.find_descendants(root_node, ["variable_declarator"])
        for node in var_declarators:
            name_node = node.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else "anonymous"
            
            value_node = node.child_by_field_name("value")
            if value_node and value_node.type in ["arrow_function", "function_expression"]:
                is_async = "async" in self.get_node_text(node, code).split("=")[0]
                
                params_node = value_node.child_by_field_name("parameters")
                params = []
                if params_node:
                    for child in params_node.children:
                        if child.type in ["identifier", "formal_parameter"]:
                            params.append(self.get_node_text(child, code))
                            
                start_line = code.count("\n", 0, node.start_byte) + 1
                end_line = code.count("\n", 0, node.end_byte) + 1
                
                functions.append({
                    "file_path": file_path,
                    "name": name,
                    "is_async": is_async,
                    "params": params,
                    "return_type": "any",
                    "class_name": "",
                    "is_method": False,
                    "start_line": start_line,
                    "end_line": end_line,
                    "description": f"Variable-assigned function {name}()"
                })

        # 3. Class Method Definitions
        methods = self.find_descendants(root_node, ["method_definition"])
        for node in methods:
            name_node = node.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else "anonymous"
            
            is_async = "async" in self.get_node_text(node, code).split("(")[0]
            
            params_node = node.child_by_field_name("parameters")
            params = []
            if params_node:
                for child in params_node.children:
                    if child.type in ["identifier", "formal_parameter"]:
                        params.append(self.get_node_text(child, code))
                        
            # Traverse upwards to find parent class
            class_name = ""
            parent = node.parent
            while parent:
                if parent.type == "class_declaration":
                    cls_name_node = parent.child_by_field_name("name")
                    class_name = self.get_node_text(cls_name_node, code) if cls_name_node else "Class"
                    break
                parent = parent.parent
                
            start_line = code.count("\n", 0, node.start_byte) + 1
            end_line = code.count("\n", 0, node.end_byte) + 1
            
            functions.append({
                "file_path": file_path,
                "name": name,
                "is_async": is_async,
                "params": params,
                "return_type": "any",
                "class_name": class_name,
                "is_method": True,
                "start_line": start_line,
                "end_line": end_line,
                "description": f"Method {class_name}.{name}()"
            })

        return functions

    def extract_validations(self, root_node: Node, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract Zod, Joi, Yup, and Express Validator rules.
        """
        validations = []

        # Find variables defined
        declarations = self.find_descendants(root_node, ["variable_declarator"])
        
        for decl in declarations:
            name_node = decl.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else ""
            
            val_node = decl.child_by_field_name("value")
            if not val_node or not name:
                continue
                
            val_text = self.get_node_text(val_node, code)
            
            # 1. Zod validation mapping
            if "z.object" in val_text:
                # Capture keys and types from schema
                fields = self._parse_schema_properties(val_text, "zod")
                validations.append({
                    "file_path": file_path,
                    "type": "zod",
                    "name": name,
                    "rules": json.dumps(fields),
                    "description": f"Zod Schema: {name}"
                })
                
            # 2. Joi validation mapping
            elif "Joi.object" in val_text:
                fields = self._parse_schema_properties(val_text, "joi")
                validations.append({
                    "file_path": file_path,
                    "type": "joi",
                    "name": name,
                    "rules": json.dumps(fields),
                    "description": f"Joi Schema: {name}"
                })
                
            # 3. Yup validation mapping
            elif "yup.object" in val_text or "Yup.object" in val_text:
                fields = self._parse_schema_properties(val_text, "yup")
                validations.append({
                    "file_path": file_path,
                    "type": "yup",
                    "name": name,
                    "rules": json.dumps(fields),
                    "description": f"Yup Schema: {name}"
                })

        # 4. Express Validator Rules
        # e.g., const validateUser = [ body('username').isString().isLength({ min: 5 }) ]
        for decl in declarations:
            name_node = decl.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else ""
            val_node = decl.child_by_field_name("value")
            if val_node and name and val_node.type == "array":
                array_text = self.get_node_text(val_node, code)
                if any(x in array_text for x in ["body(", "query(", "param(", "check("]):
                    rules = self._parse_express_validator(array_text)
                    validations.append({
                        "file_path": file_path,
                        "type": "express-validator",
                        "name": name,
                        "rules": json.dumps(rules),
                        "description": f"Express Validator check list: {name}"
                    })

        return validations

    def _parse_schema_properties(self, text: str, schema_type: str) -> Dict[str, str]:
        """
        Parse validation schema properties and types using string heuristic patterns.
        """
        properties = {}
        
        # Look for pattern: fieldName: z.string() or fieldName: Joi.string()
        if schema_type == "zod":
            matches = re.findall(r"(\w+)\s*:\s*z\.(\w+)(?:\((.*?)\))?", text)
            for m in matches:
                properties[m[0]] = f"zod:{m[1]}"
        elif schema_type == "joi":
            matches = re.findall(r"(\w+)\s*:\s*Joi\.(\w+)(?:\((.*?)\))?", text)
            for m in matches:
                properties[m[0]] = f"joi:{m[1]}"
        elif schema_type == "yup":
            matches = re.findall(r"(\w+)\s*:\s*(?:yup|Yup)\.(\w+)(?:\((.*?)\))?", text)
            for m in matches:
                properties[m[0]] = f"yup:{m[1]}"
                
        return properties

    def _parse_express_validator(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse Express Validator rules.
        """
        rules = []
        # Match e.g. body('email').isEmail().withMessage('invalid')
        matches = re.findall(r"(body|query|param|check)\(['\"]([^'\"]+)['\"]\)(.*?)(?:,|$)", text)
        for m in matches:
            location = m[0]
            field = m[1]
            chain = m[2]
            
            # Simple validation list extractor
            validations = re.findall(r"\.(\w+)\(", chain)
            rules.append({
                "field": field,
                "location": location,
                "validations": validations
            })
        return rules

    def extract_database_objects(self, root_node: Node, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract models, tables, columns, relations for Sequelize, TypeORM, Mongoose, Knex/Objection.
        """
        db_objects = []

        # 1. TypeORM Entities (Classes decorated with @Entity)
        classes = self.find_descendants(root_node, ["class_declaration"])
        for cls in classes:
            decorators = self.find_descendants(cls, ["decorator"])
            is_entity = False
            entity_table = ""
            
            for dec in decorators:
                dec_text = self.get_node_text(dec, code)
                if "@Entity" in dec_text:
                    is_entity = True
                    match = re.search(r"@Entity\(['\"]([^'\"]+)['\"]\)", dec_text)
                    if match:
                        entity_table = match.group(1)
            
            if is_entity:
                cls_name_node = cls.child_by_field_name("name")
                name = self.get_node_text(cls_name_node, code) if cls_name_node else "Entity"
                if not entity_table:
                    entity_table = name.lower() + "s"  # heuristic
                    
                # Scans properties/columns
                fields = []
                relations = []
                properties = self.find_descendants(cls, ["public_field_definition", "property_definition"])
                for prop in properties:
                    prop_decorators = self.find_descendants(prop, ["decorator"])
                    prop_name_node = prop.child_by_field_name("name")
                    prop_name = self.get_node_text(prop_name_node, code) if prop_name_node else ""
                    if not prop_name:
                        continue
                        
                    is_col = False
                    col_type = "string"
                    
                    for p_dec in prop_decorators:
                        p_dec_text = self.get_node_text(p_dec, code)
                        if "@Column" in p_dec_text or "@Primary" in p_dec_text:
                            is_col = True
                            t_match = re.search(r"@Column\(\s*\{\s*type\s*:\s*['\"]([^'\"]+)['\"]", p_dec_text)
                            if t_match:
                                col_type = t_match.group(1)
                        # Relationship decorators
                        rel_match = re.search(r"@(OneToMany|ManyToOne|OneToOne|ManyToMany)", p_dec_text)
                        if rel_match:
                            rel_type = rel_match.group(1)
                            # Get related entity name
                            ent_match = re.search(r"type\s*=>\s*(\w+)", p_dec_text)
                            if not ent_match:
                                ent_match = re.search(r"@(OneToMany|ManyToOne|OneToOne|ManyToMany)\(\s*\(\)\s*=>\s*(\w+)", p_dec_text)
                            target_ent = ent_match.group(2) if ent_match else "Unknown"
                            relations.append({
                                "field": prop_name,
                                "type": rel_type,
                                "target": target_ent
                            })
                            
                    if is_col:
                        fields.append({
                            "name": prop_name,
                            "type": col_type
                        })
                        
                db_objects.append({
                    "file_path": file_path,
                    "type": "TypeORM:Entity",
                    "name": name,
                    "schema_definition": json.dumps({
                        "table": entity_table,
                        "fields": fields,
                        "relations": relations
                    }),
                    "description": f"TypeORM Entity mapping to table: {entity_table}"
                })

        # 2. Mongoose Schemas (new Schema({...}) or mongoose.model(...))
        declarations = self.find_descendants(root_node, ["variable_declarator"])
        for decl in declarations:
            name_node = decl.child_by_field_name("name")
            name = self.get_node_text(name_node, code) if name_node else ""
            val_node = decl.child_by_field_name("value")
            if not val_node or not name:
                continue
                
            val_text = self.get_node_text(val_node, code)
            
            # Detect Schema
            if "new Schema(" in val_text or "new mongoose.Schema(" in val_text:
                fields = self._parse_mongoose_fields(val_text)
                db_objects.append({
                    "file_path": file_path,
                    "type": "Mongoose:Schema",
                    "name": name,
                    "schema_definition": json.dumps({
                        "fields": fields,
                        "relations": []
                    }),
                    "description": f"Mongoose Schema: {name}"
                })
                
            # Detect Model export / declaration
            # mongoose.model('User', UserSchema)
            elif "mongoose.model(" in val_text or "model(" in val_text:
                model_match = re.search(r"(?:mongoose\.)?model\(['\"]([^'\"]+)['\"]\s*,\s*(\w+)\)", val_text)
                if model_match:
                    model_name = model_match.group(1)
                    schema_var = model_match.group(2)
                    db_objects.append({
                        "file_path": file_path,
                        "type": "Mongoose:Model",
                        "name": model_name,
                        "schema_definition": json.dumps({
                            "schema_variable": schema_var
                        }),
                        "description": f"Mongoose Model: {model_name} linked to schema {schema_var}"
                    })

        # 3. Sequelize Models
        # sequelize.define('User', { ... })
        calls = self.find_descendants(root_node, ["call_expression"])
        for call in calls:
            callee_text = self.get_node_text(call.child_by_field_name("function"), code)
            if "sequelize.define" in callee_text:
                args = call.child_by_field_name("arguments")
                if args and len(args.children) >= 5: # open, name, comma, fields_obj, close
                    name_node = args.children[1]
                    fields_node = args.children[3]
                    
                    name_text = self.get_node_text(name_node, code).replace("'", "").replace('"', '')
                    fields_text = self.get_node_text(fields_node, code)
                    
                    fields = self._parse_sequelize_fields(fields_text)
                    
                    db_objects.append({
                        "file_path": file_path,
                        "type": "Sequelize:Model",
                        "name": name_text,
                        "schema_definition": json.dumps({
                            "table": name_text.lower() + "s", # sequelize convention
                            "fields": fields,
                            "relations": []
                        }),
                        "description": f"Sequelize Model: {name_text}"
                    })
                    
            # Class extending Sequelize Model init
            # User.init({ ... }, { sequelize, modelName: 'User' })
            elif ".init" in callee_text:
                args = call.child_by_field_name("arguments")
                if args and len(args.children) >= 5:
                    fields_node = args.children[1]
                    config_node = args.children[3]
                    
                    fields_text = self.get_node_text(fields_node, code)
                    config_text = self.get_node_text(config_node, code)
                    
                    model_name_match = re.search(r"modelName\s*:\s*['\"]([^'\"]+)['\"]", config_text)
                    model_name = model_name_match.group(1) if model_name_match else callee_text.split(".")[0]
                    
                    fields = self._parse_sequelize_fields(fields_text)
                    
                    db_objects.append({
                        "file_path": file_path,
                        "type": "Sequelize:Model",
                        "name": model_name,
                        "schema_definition": json.dumps({
                            "table": model_name.lower() + "s",
                            "fields": fields,
                            "relations": []
                        }),
                        "description": f"Sequelize Model Class: {model_name}"
                    })

        return db_objects

    def _parse_mongoose_fields(self, text: str) -> List[Dict[str, str]]:
        """
        Parses fields from Mongoose schema definition string.
        """
        fields = []
        # Heuristic search for e.g. name: { type: String, required: true } or name: String
        matches = re.findall(r"(\w+)\s*:\s*\{\s*type\s*:\s*(\w+)", text)
        for m in matches:
            fields.append({
                "name": m[0],
                "type": m[1]
            })
            
        # Single type declarations e.g. name: String
        single_matches = re.findall(r"(\w+)\s*:\s*(String|Number|Boolean|Date|Buffer|ObjectID|Array)(?:\s*,|\s*\})", text, re.IGNORECASE)
        for m in single_matches:
            if m[0] not in [f["name"] for f in fields]:
                fields.append({
                    "name": m[0],
                    "type": m[1]
                })
                
        return fields

    def _parse_sequelize_fields(self, text: str) -> List[Dict[str, str]]:
        """
        Parses fields from Sequelize schema definition string.
        """
        fields = []
        # Matches e.g. username: DataTypes.STRING or type: DataTypes.STRING
        # Scan property blocks: name: { type: DataTypes.STRING, allowNull: false }
        prop_blocks = re.findall(r"(\w+)\s*:\s*\{\s*type\s*:\s*(?:DataTypes\.)?(\w+)", text)
        for m in prop_blocks:
            fields.append({
                "name": m[0],
                "type": m[1]
            })
            
        # Matches single declarations name: DataTypes.STRING
        single_props = re.findall(r"(\w+)\s*:\s*(?:DataTypes\.)?(\w+)\s*(?:,|$)", text)
        for m in single_props:
            if m[0] not in [f["name"] for f in fields] and m[1] not in ["INTEGER", "STRING", "BOOLEAN", "DATE", "UUID", "TEXT", "FLOAT", "DECIMAL"]:
                # Filter out obvious mistakes
                continue
            if m[0] not in [f["name"] for f in fields]:
                fields.append({
                    "name": m[0],
                    "type": m[1]
                })
        return fields

    def trace_data_flows(self, root_node: Node, code: str, file_path: str, routes: List[Dict[str, Any]], functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Traces route handlers calling internal functions/services to map flows.
        """
        flows = []
        
        # If there are no routes, no business route flows to trace in this file.
        if not routes:
            return flows
            
        # Look for calls in the file
        calls = self.find_descendants(root_node, ["call_expression"])
        
        for route in routes:
            # If the handler is an inline function, we can check the calls inside it.
            # Or if it's named, we search the file for the function definition.
            handler_name = route["handler"]
            
            # Simple flow builder
            flow_steps = [{"type": "route", "name": f"{route['method']} {route['path']}"}]
            
            # Look for calls inside the code corresponding to this route handler or in the file.
            # Check if code has controller / service call patterns, e.g. InvoiceService.create
            for call in calls:
                callee_text = self.get_node_text(call.child_by_field_name("function"), code)
                # Look for calls like `Service.method(` or `Controller.method(`
                match = re.search(r"(\w+(?:Service|Controller|Repository|Model))\.(\w+)", callee_text)
                if match:
                    step_name = f"{match.group(1)}.{match.group(2)}"
                    step_type = "service"
                    if "Controller" in match.group(1):
                        step_type = "controller"
                    elif "Repository" in match.group(1):
                        step_type = "repository"
                    elif "Model" in match.group(1):
                        step_type = "model"
                        
                    step_def = {"type": step_type, "name": step_name}
                    if step_def not in flow_steps:
                        flow_steps.append(step_def)
            
            if len(flow_steps) > 1:
                flows.append({
                    "file_path": file_path,
                    "flow_name": f"API Request Flow for {route['method']} {route['path']}",
                    "steps": json.dumps(flow_steps),
                    "description": f"Traces request parameters flow through validation schemas to service action calls."
                })
                
        return flows


class PrismaParser:
    """
    Parses schema.prisma files directly without Tree-sitter.
    """
    def __init__(self):
        pass
        
    def parse(self, filepath: Path) -> List[Dict[str, Any]]:
        db_objects = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return db_objects

        rel_path = str(filepath).replace("\\", "/")
        
        # Matches model blocks: model User { ... }
        models = re.findall(r"model\s+(\w+)\s*\{([^}]+)\}", content)
        for m_name, m_body in models:
            fields = []
            relations = []
            
            # Scan lines in model body
            for line in m_body.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                    
                # Matches: fieldName FieldType [@decorators]
                parts = line.split()
                if len(parts) >= 2:
                    f_name = parts[0]
                    f_type = parts[1]
                    
                    # Check relations
                    if "@relation(" in line:
                        # e.g., author User @relation(fields: [authorId], references: [id])
                        rel_match = re.search(r"fields\s*:\s*\[([^\]]+)\].*references\s*:\s*\[([^\]]+)\]", line)
                        relations.append({
                            "field": f_name,
                            "type": "Prisma:Relation",
                            "target": f_type.replace("[]", ""),
                            "details": rel_match.group(0) if rel_match else ""
                        })
                    else:
                        fields.append({
                            "name": f_name,
                            "type": f_type
                        })
                        
            db_objects.append({
                "file_path": rel_path,
                "type": "Prisma:Model",
                "name": m_name,
                "schema_definition": json.dumps({
                    "table": m_name.lower(),
                    "fields": fields,
                    "relations": relations
                }),
                "description": f"Prisma Database Model: {m_name}"
            })
            
        return db_objects
