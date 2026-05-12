from lexer import Scanner
from tokens import Token
from parse_tree import ParseTreeNode
from grammar import LL1Grammar
from error_handler import ErrorHandler


class Parser:
    """
    Table-driven LL(1) Predictive Parser (Method B).

    Delegates to:
      - LL1Grammar      – productions, FIRST/FOLLOW, parsing table
      - ParseTreeNode   – concrete parse tree
      - ErrorHandler    – error collection and panic-mode recovery
    """

    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.current_token: Token = self.scanner.get_next_token()

        # --- grammar setup ---
        self.grammar = LL1Grammar()
        self.grammar.prepare()
        self.grammar.compute_first()
        self.grammar.compute_follow()
        conflicts = self.grammar.build_table()
        if conflicts:
            details = [
                f"M[{lhs}, {la}] has {old} and {new}"
                for lhs, la, old, new in conflicts
            ]
            raise ValueError("Grammar is not LL(1): " + "; ".join(details))

        # --- error handler ---
        self.error_handler = ErrorHandler(self.grammar)

        # Convenience alias so callers can still read parser.errors
        self.errors = self.error_handler.errors

        # --- parse tree root + explicit stack ---
        self.root = ParseTreeNode(self.grammar.start_symbol)
        self.stack: list[tuple[str, ParseTreeNode | None]] = [
            (self.grammar.ENDMARKER, None),
            (self.grammar.start_symbol, self.root),
        ]

    # ------------------------------------------------------------------
    # Token → grammar-terminal mapping
    # ------------------------------------------------------------------

    def _get_terminal_key(self, token: Token) -> str:
        if token.type == "EOF":
            return self.grammar.ENDMARKER
        if token.type == "IDENTIFIER":
            return "ID"
        if token.type == "NUMBER":
            return "NUM"
        if token.type == "STRING":
            return "STR"
        if token.type == "KEYWORD":
            return token.value
        if token.type == "SEPARATOR":
            return token.value
        if token.type == "OPERATOR":
            if token.value in ("+", "-", "="):
                return token.value
            if token.value in ("<", ">", "==", "!=", "<=", ">="):
                return "RELOP"
        return "UNKNOWN"

    # ------------------------------------------------------------------
    # Main parse loop
    # ------------------------------------------------------------------

    def parse(self) -> ParseTreeNode:
        """Execute the table-driven algorithm and return the parse tree root."""
        while self.stack:
            top_symbol, parent_node = self.stack.pop()

            # ── End-marker ──────────────────────────────────────────────
            if top_symbol == self.grammar.ENDMARKER:
                if self.current_token.type == "EOF":
                    break
                self.error_handler.record(
                    f"Line {self.current_token.line}: "
                    f"Expected EOF, got '{self.current_token.value}'"
                )
                self.current_token = self.scanner.get_next_token()
                continue

            # ── Terminal on top of stack ─────────────────────────────────
            if top_symbol in self.grammar.terminals:
                if top_symbol == self.grammar.EPSILON:
                    parent_node.symbol = "ε"
                    continue

                terminal_key = self._get_terminal_key(self.current_token)
                if top_symbol == terminal_key:
                    parent_node.lexeme = self.current_token.value
                    self.current_token = self.scanner.get_next_token()
                else:
                    self.error_handler.record(
                        f"Line {self.current_token.line}: "
                        f"Expected '{top_symbol}', got '{self.current_token.value}'"
                    )
                    # Discard one input symbol and continue.
                    if self.current_token.type != "EOF":
                        self.current_token = self.scanner.get_next_token()

            # ── Non-terminal on top of stack – consult table M ───────────
            else:
                terminal_key = self._get_terminal_key(self.current_token)
                production = self.grammar.parsing_table.get(top_symbol, {}).get(terminal_key)

                if production is not None:
                    child_nodes = [ParseTreeNode(sym) for sym in production]
                    parent_node.children.extend(child_nodes)
                    for child in reversed(child_nodes):
                        self.stack.append((child.symbol, child))
                else:
                    # Generate a helpful error message with expected tokens
                    sync_set = self.grammar.follow.get(top_symbol, set())
                    expected = sorted(sync_set) if sync_set else ["EOF"]
                    expected_str = "', '".join(expected[:3])  # Show first 3 expected tokens
                    if len(expected) > 3:
                        expected_str += f", ... ({len(expected)} total)"
                    
                    self.error_handler.record(
                        f"Line {self.current_token.line}: "
                        f"Unexpected '{self.current_token.value}' in {top_symbol} "
                        f"(expected: '{expected_str}')"
                    )
                    # Panic-mode recovery – advance scanner until sync token.
                    self.current_token = self.error_handler.synchronize(
                        top_symbol,
                        self.current_token,
                        self.scanner.get_next_token,
                    )

        return self.root