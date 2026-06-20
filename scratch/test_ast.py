# scratch/test_ast.py
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjs

JS_LANGUAGE = Language(tsjs.language())
parser = Parser(JS_LANGUAGE)

filepath = Path("tests/dummy-project/src/index.js")
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

tree = parser.parse(bytes(code, "utf8"))
print("Root node type:", tree.root_node.type)

def print_tree(node, depth=0):
    text = code[node.start_byte:node.end_byte].split("\n")[0][:40]
    print("  " * depth + f"- {node.type} ({node.start_byte}-{node.end_byte}): {text}")
    for child in node.children:
        print_tree(child, depth + 1)

print_tree(tree.root_node)
