class LL1Grammar:
    """
    Owns grammar productions and all LL(1) analysis artifacts:
      - direct left-recursion elimination
      - left factoring
      - FIRST / FOLLOW set computation
      - parsing-table construction
    """

    EPSILON = "epsilon"
    ENDMARKER = "EOF"

    def __init__(self):
        self.start_symbol = "<program>"
        # Grammar already written in right-recursive, left-factored shape.
        self.productions = {
            "<program>":          [["<stmt_list>"]],
            "<stmt_list>":        [["<stmt>", "<stmt_list_prime>"]],
            "<stmt_list_prime>":  [["<stmt>", "<stmt_list_prime>"], [self.EPSILON]],
            "<stmt>":             [["<assignment>"], ["<if_stmt>"], ["<while_stmt>"]],
            "<assignment>":       [["ID", "=", "<expr>"]],
            # Without INDENT/DEDENT tokens, control-flow bodies are one statement.
            "<if_stmt>":          [["if", "<cond>", ":", "<stmt>", "else", ":", "<stmt>"]],
            "<while_stmt>":       [["while", "<cond>", ":", "<stmt>"]],
            "<cond>":             [["<expr>", "RELOP", "<expr>"]],
            "<expr>":             [["<term>", "<expr_prime>"]],
            "<expr_prime>":       [["+", "<expr>"], ["-", "<expr>"], [self.EPSILON]],
            "<term>":             [["ID"], ["NUM"], ["STR"]],
        }

        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {s: set() for s in self.nonterminals}
        self.follow = {s: set() for s in self.nonterminals}
        self.parsing_table = {s: {} for s in self.nonterminals}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Grammar normalisation: left-recursion elimination + left factoring
    # ------------------------------------------------------------------

    def _eliminate_direct_left_recursion(self):
        """Applies the standard A → Aα | β rewrite when needed."""
        new_productions = {}
        for nonterminal, bodies in self.productions.items():
            recursive, non_recursive = [], []
            for body in bodies:
                (recursive if body and body[0] == nonterminal else non_recursive).append(body)

            if not recursive:
                new_productions[nonterminal] = bodies
                continue

            helper = f"{nonterminal}_tail"
            new_non_recursive = [
                [helper] if body == [self.EPSILON] else body + [helper]
                for body in non_recursive
            ]
            helper_bodies = [alpha + [helper] for alpha in recursive] + [[self.EPSILON]]

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
                # Group alternatives by their leading symbol.
                prefix_groups = {}
                for body in bodies:
                    first_symbol = body[0] if body else self.EPSILON
                    prefix_groups.setdefault(first_symbol, []).append(body)

                # Find the first ambiguous prefix (if any).
                factor_symbol, factor_group = None, None
                for symbol, grouped in prefix_groups.items():
                    if symbol != self.EPSILON and len(grouped) > 1:
                        factor_symbol, factor_group = symbol, grouped
                        break

                if factor_group is None:
                    updated[nonterminal] = bodies
                    continue

                changed = True
                counter[nonterminal] = counter.get(nonterminal, 0) + 1
                helper = f"{nonterminal}_factored_{counter[nonterminal]}"

                suffixes = []
                remaining = [body for body in bodies if body not in factor_group]
                for body in factor_group:
                    suffix = body[1:] if len(body) > 1 else [self.EPSILON]
                    suffixes.append(suffix)

                remaining.append([factor_symbol, helper])
                updated[nonterminal] = remaining
                updated[helper] = suffixes

            self.productions = updated
            self.nonterminals = set(self.productions.keys())

    # ------------------------------------------------------------------
    # Public: prepare the grammar, then compute sets + table
    # ------------------------------------------------------------------

    def prepare(self):
        """Normalise the grammar (left-recursion + left-factoring)."""
        self._eliminate_direct_left_recursion()
        self._left_factor()
        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {s: set() for s in self.nonterminals}
        self.follow = {s: set() for s in self.nonterminals}
        self.parsing_table = {s: {} for s in self.nonterminals}

    # ------------------------------------------------------------------
    # FIRST sets
    # ------------------------------------------------------------------

    def _first_of_sequence(self, sequence):
        """Return FIRST(X1 X2 … Xn) for a list of grammar symbols."""
        if not sequence:
            return {self.EPSILON}

        result = set()
        for symbol in sequence:
            if symbol == self.EPSILON:
                result.add(self.EPSILON)
                break
            symbol_first = self.first[symbol] if symbol in self.nonterminals else {symbol}
            result |= symbol_first - {self.EPSILON}
            if self.EPSILON not in symbol_first:
                return result          # this symbol is not nullable – stop

        result.add(self.EPSILON)       # every symbol in the sequence was nullable
        return result

    def compute_first(self):
        """Iteratively compute FIRST sets until a fixed point is reached."""
        changed = True
        while changed:
            changed = False
            for nonterminal, bodies in self.productions.items():
                for body in bodies:
                    before = len(self.first[nonterminal])
                    self.first[nonterminal] |= self._first_of_sequence(body)
                    if len(self.first[nonterminal]) != before:
                        changed = True

    # ------------------------------------------------------------------
    # FOLLOW sets
    # ------------------------------------------------------------------

    def compute_follow(self):
        """Iteratively compute FOLLOW sets until a fixed point is reached."""
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
                        self.follow[symbol] |= beta_first - {self.EPSILON}
                        if self.EPSILON in beta_first or not beta:
                            self.follow[symbol] |= self.follow[lhs]
                        if len(self.follow[symbol]) != before:
                            changed = True

    # ------------------------------------------------------------------
    # LL(1) parsing table
    # ------------------------------------------------------------------

    def build_table(self):
        """
        Fill M[A, a] entries.
        Returns a list of conflicts (empty → grammar is LL(1)).
        """
        conflicts = []
        for lhs, bodies in self.productions.items():
            for body in bodies:
                first_body = self._first_of_sequence(body)
                lookaheads = first_body - {self.EPSILON}
                if self.EPSILON in first_body:
                    lookaheads |= self.follow[lhs]

                for terminal in lookaheads:
                    existing = self.parsing_table[lhs].get(terminal)
                    if existing is not None and existing != body:
                        conflicts.append((lhs, terminal, existing, body))
                    else:
                        self.parsing_table[lhs][terminal] = body

        return conflicts