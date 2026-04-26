from lexer import Scanner
from tokens import Token


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

        #print all children recursively
        child_count = len(self.children)
        for i, child in enumerate(self.children):
            child_is_last = (i == child_count - 1)
            child.print_tree(new_prefix, child_is_last, is_root=False)


class LL1Grammar:
    """Owns grammar preparation and LL(1) analysis artifacts."""

    EPSILON = "epsilon"
    ENDMARKER = "EOF"

    def __init__(self):
        self.start_symbol = "<program>"
        # Grammar is already written in a right-recursive, left-factored shape.
        self.productions = {
            "<program>": [["<stmt_list>"]],
            "<stmt_list>": [["<stmt>", "<stmt_list_prime>"]],
            "<stmt_list_prime>": [["<stmt>", "<stmt_list_prime>"], [self.EPSILON]],
            "<stmt>": [["<assignment>"], ["<if_stmt>"], ["<while_stmt>"]],
            "<assignment>": [["ID", "=", "<expr>"]],
            # Without INDENT/DEDENT tokens, control-flow bodies are one statement.
            "<if_stmt>": [["if", "<cond>", ":", "<stmt>", "else", ":", "<stmt>"]],
            "<while_stmt>": [["while", "<cond>", ":", "<stmt>"]],
            "<cond>": [["<expr>", "RELOP", "<expr>"]],
            "<expr>": [["<term>", "<expr_prime>"]],
            "<expr_prime>": [["+", "<expr>"], ["-", "<expr>"], [self.EPSILON]],
            "<term>": [["ID"], ["NUM"], ["STR"]],
        }

        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {symbol: set() for symbol in self.nonterminals}
        self.follow = {symbol: set() for symbol in self.nonterminals}
        self.parsing_table = {symbol: {} for symbol in self.nonterminals}

    def _collect_terminals(self):
        terminals = set()
        for bodies in self.productions.values():
            for body in bodies:
                for symbol in body:
                    if symbol not in self.productions and symbol != self.EPSILON:
                        terminals.add(symbol)
        terminals.add(self.ENDMARKER)
        terminals.add(self.EPSILON)
        return terminals

    def _eliminate_direct_left_recursion(self):
        """Applies the standard A->Aalpha|beta rewrite when needed."""
        new_productions = {}
        for nonterminal, bodies in self.productions.items():
            recursive = []
            non_recursive = []
            for body in bodies:
                if body and body[0] == nonterminal:
                    recursive.append(body[1:])
                else:
                    non_recursive.append(body)

            if not recursive:
                new_productions[nonterminal] = bodies
                continue

            helper = f"{nonterminal}_tail"
            new_non_recursive = []
            for body in non_recursive:
                if body == [self.EPSILON]:
                    new_non_recursive.append([helper])
                else:
                    new_non_recursive.append(body + [helper])

            helper_bodies = [alpha + [helper] for alpha in recursive]
            helper_bodies.append([self.EPSILON])

            new_productions[nonterminal] = new_non_recursive
            new_productions[helper] = helper_bodies

        self.productions = new_productions

    def _left_factor(self):
        """Performs one-symbol left factoring repeatedly until stable."""
        counter = {}
        changed = True
        while changed:
            changed = False
            updated = {}
            for nonterminal, bodies in self.productions.items():
                prefix_groups = {}
                for body in bodies:
                    first_symbol = body[0] if body else self.EPSILON
                    prefix_groups.setdefault(first_symbol, []).append(body)

                factor_symbol = None
                factor_group = None
                for symbol, grouped in prefix_groups.items():
                    if symbol != self.EPSILON and len(grouped) > 1:
                        factor_symbol = symbol
                        factor_group = grouped
                        break

                if factor_group is None:
                    updated[nonterminal] = bodies
                    continue

                changed = True
                if nonterminal not in counter:
                    counter[nonterminal] = 0
                counter[nonterminal] += 1
                helper = f"{nonterminal}_factored_{counter[nonterminal]}"
                suffixes = []
                remaining = []

                for body in bodies:
                    if body in factor_group:
                        suffix = body[1:] if len(body) > 1 else [self.EPSILON]
                        suffixes.append(suffix)
                    else:
                        remaining.append(body)

                remaining.append([factor_symbol, helper])
                updated[nonterminal] = remaining
                updated[helper] = suffixes

            self.productions = updated
            self.nonterminals = set(self.productions.keys())

    def prepare(self):
        self._eliminate_direct_left_recursion()
        self._left_factor()
        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {symbol: set() for symbol in self.nonterminals}
        self.follow = {symbol: set() for symbol in self.nonterminals}
        self.parsing_table = {symbol: {} for symbol in self.nonterminals}

    def _first_of_sequence(self, sequence):
        if not sequence:
            return {self.EPSILON}

        sequence_first = set()
        all_nullable = True
        for symbol in sequence:
            if symbol == self.EPSILON:
                sequence_first.add(self.EPSILON)
                break

            if symbol in self.nonterminals:
                symbol_first = self.first[symbol]
            else:
                symbol_first = {symbol}

            sequence_first |= (symbol_first - {self.EPSILON})

            if self.EPSILON not in symbol_first:
                all_nullable = False
                break

        if all_nullable:
            sequence_first.add(self.EPSILON)

        return sequence_first

    def compute_first(self):
        changed = True
        while changed:
            changed = False
            for nonterminal, bodies in self.productions.items():
                for body in bodies:
                    derived = self._first_of_sequence(body)
                    before = len(self.first[nonterminal])
                    self.first[nonterminal] |= derived
                    if len(self.first[nonterminal]) != before:
                        changed = True

    def compute_follow(self):
        self.follow[self.start_symbol].add(self.ENDMARKER)
        changed = True
        while changed:
            changed = False
            for lhs, bodies in self.productions.items():
                for body in bodies:
                    for index, symbol in enumerate(body):
                        if symbol not in self.nonterminals:
                            continue

                        beta = body[index + 1:]
                        beta_first = self._first_of_sequence(beta)

                        before = len(self.follow[symbol])
                        self.follow[symbol] |= (beta_first - {self.EPSILON})
                        if self.EPSILON in beta_first or not beta:
                            self.follow[symbol] |= self.follow[lhs]

                        if len(self.follow[symbol]) != before:
                            changed = True

    def build_table(self):
        conflicts = []
        for lhs, bodies in self.productions.items():
            for body in bodies:
                first_body = self._first_of_sequence(body)
                lookaheads = set(first_body - {self.EPSILON})
                if self.EPSILON in first_body:
                    lookaheads |= self.follow[lhs]

                for terminal in lookaheads:
                    existing = self.parsing_table[lhs].get(terminal)
                    if existing is not None and existing != body:
                        conflicts.append((lhs, terminal, existing, body))
                    else:
                        self.parsing_table[lhs][terminal] = body

        return conflicts

class Parser:
    """
    Table-driven LL(1) Predictive Parser (Method B).
    Validates syntax using an explicit stack and an LL(1) parsing table.
    """
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.current_token = self.scanner.get_next_token()
        self.root = ParseTreeNode("<program>")
        self.errors = []

        self.grammar = LL1Grammar()
        self.grammar.prepare()
        self.grammar.compute_first()
        self.grammar.compute_follow()
        conflicts = self.grammar.build_table()
        if conflicts:
            details = []
            for lhs, lookahead, old_body, new_body in conflicts:
                details.append(
                    f"M[{lhs}, {lookahead}] has {old_body} and {new_body}"
                )
            raise ValueError("Grammar is not LL(1): " + "; ".join(details))

        # The explicit stack stores (grammar_symbol, parse_tree_node).
        self.stack = [(self.grammar.ENDMARKER, None), (self.grammar.start_symbol, self.root)]

    def _get_terminal_key(self, token: Token) -> str:
        """Maps lexer tokens to grammar terminal symbols."""
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
            if token.value == "=":
                return "="
            if token.value in ["+", "-"]:
                return token.value
            if token.value in ["<", ">", "==", "!=", "<=", ">="]:
                return "RELOP"
        return "UNKNOWN"

    def _synchronize_nonterminal(self, nonterminal):
        """Panic-mode: skip tokens until FOLLOW(nonterminal) or EOF, then pop nonterminal."""
        sync_set = self.grammar.follow.get(nonterminal, set())
        lookahead = self._get_terminal_key(self.current_token)

        if lookahead in sync_set:
            return

        while self.current_token.type != "EOF":
            lookahead = self._get_terminal_key(self.current_token)
            if lookahead in sync_set:
                return
            self.current_token = self.scanner.get_next_token()

    def _record_error(self, message):
        self.errors.append(message)

    def parse(self):
        """Executes the table-driven parsing algorithm and returns the Parse Tree."""
        while self.stack:
            top_symbol, parent_node = self.stack.pop()

            if top_symbol == self.grammar.ENDMARKER:
                if self.current_token.type == "EOF":
                    break
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: Expected EOF, got {self.current_token.value}"
                    )
                    self.current_token = self.scanner.get_next_token()
                    continue

            # 1. Handle Terminals on top of the stack
            if top_symbol in self.grammar.terminals:
                if top_symbol == self.grammar.EPSILON:
                    parent_node.symbol = "ε"
                    continue

                terminal_key = self._get_terminal_key(self.current_token)
                if top_symbol == terminal_key:
                    parent_node.lexeme = self.current_token.value
                    self.current_token = self.scanner.get_next_token()
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: Expected '{top_symbol}', got '{self.current_token.value}'"
                    )
                    # Terminal mismatch recovery: discard one input symbol.
                    if self.current_token.type != "EOF":
                        self.current_token = self.scanner.get_next_token()

            # 2. Handle Non-Terminals on top of the stack (Consult Table M)
            else:
                terminal_key = self._get_terminal_key(self.current_token)
                production = self.grammar.parsing_table.get(top_symbol, {}).get(terminal_key)

                if production is not None:
                    # Create children nodes for the parse tree in forward order
                    child_nodes = [ParseTreeNode(sym) for sym in production]
                    parent_node.children.extend(child_nodes)

                    # Push children onto the stack in REVERSE order
                    for child in reversed(child_nodes):
                        self.stack.append((child.symbol, child))
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: No rule for {top_symbol} with lookahead '{self.current_token.value}'"
                    )
                    self._synchronize_nonterminal(top_symbol)

        return self.root