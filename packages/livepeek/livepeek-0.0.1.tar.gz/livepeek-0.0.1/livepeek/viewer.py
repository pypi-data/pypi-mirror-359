from rich.tree import Tree
from rich.console import Console
from rich.syntax import Syntax

def display_json(data):
    console = Console()
    tree = Tree("[bold blue]JSON")

    def add_branch(branch, value):
        if isinstance(value, dict):
            for k, v in value.items():
                sub = branch.add(f"[green]{k}")
                add_branch(sub, v)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                sub = branch.add(f"[yellow][{i}]")
                add_branch(sub, item)
        else:
            branch.add(f"[white]{repr(value)}")

    add_branch(tree, data)
    console.print(tree)
