# scratch/test_fields.py
from tree_sitter import Language, Parser, Node
import tree_sitter_javascript as tsjs

JS_LANGUAGE = Language(tsjs.language())
parser = Parser(JS_LANGUAGE)

code = "class A { myMethod(a) {} }; const f = (x, y) => {};"
tree = parser.parse(bytes(code, "utf8"))

def find_nodes(node, types):
    res = []
    if node.type in types:
        res.append(node)
    for child in node.children:
        res.extend(find_nodes(child, types))
    return res

methods = find_nodes(tree.root_node, ["method_definition"])
if methods:
    m = methods[0]
    print("Method type:", m.type)
    print("  - name:", m.child_by_field_name("name"))
    print("  - parameters:", m.child_by_field_name("parameters"))
    print("  - body:", m.child_by_field_name("body"))

arrows = find_nodes(tree.root_node, ["arrow_function"])
if arrows:
    a = arrows[0]
    print("Arrow type:", a.type)
    print("  - name:", a.child_by_field_name("name"))
    print("  - parameters:", a.child_by_field_name("parameters"))
    print("  - body:", a.child_by_field_name("body"))
