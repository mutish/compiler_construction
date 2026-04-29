class ParseTreeNode:
    """A simple n-ary tree node to represent the parse tree."""

    def __init__(self, symbol):
        self.symbol = symbol
        self.lexeme = None
        self.children = []

    def print_tree(self, prefix="", is_last=True, is_root=True):
        lexeme_str = f"('{self.lexeme}')" if self.lexeme else ""
        node_display = f"{self.symbol}{lexeme_str}"

    
        if is_root:
            print(node_display)
            new_prefix = prefix
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node_display}")
            new_prefix = prefix + ("    " if is_last else "│   ")

        visible = [c for c in self.children if c.symbol != "ε"]
        child_count = len(visible)
        for i, child in enumerate(visible):
            child_is_last = (i == child_count - 1)
            child.print_tree(new_prefix, child_is_last, is_root=False)