class ErrorHandler:
    """
    Centralises all parser error concerns:
      - collecting error / warning messages
      - panic-mode synchronisation on non-terminals
    """

    def __init__(self, grammar):
        """
        Parameters
        ----------
        grammar : LL1Grammar
            The prepared grammar object (needs .follow and .ENDMARKER).
        """
        self.grammar = grammar
        self.errors: list[str] = []

    # ------------------------------------------------------------------
    # Error accumulation
    # ------------------------------------------------------------------

    def record(self, message: str):
        """Append a diagnostic message to the error list."""
        self.errors.append(message)

    def has_errors(self) -> bool:
        return bool(self.errors)

    # ------------------------------------------------------------------
    # Panic-mode recovery
    # ------------------------------------------------------------------

    def synchronize(self, nonterminal: str, current_token, advance_fn):
        """
        Skip input tokens until a token in FOLLOW(nonterminal) or EOF is seen,
        then return so the caller can pop the non-terminal from the stack.

        Parameters
        ----------
        nonterminal : str
            The non-terminal currently on top of the parser stack.
        current_token : Token
            The token currently being examined by the parser.
        advance_fn : callable
            Zero-argument callable that returns the next Token from the scanner.

        Returns
        -------
        Token
            The (possibly advanced) current token after synchronisation.
        """
        sync_set = self.grammar.follow.get(nonterminal, set())
        lookahead_fn = lambda tok: self._terminal_key(tok)

        # Already in the sync set – nothing to skip.
        if lookahead_fn(current_token) in sync_set:
            return current_token

        while current_token.type != "EOF":
            current_token = advance_fn()
            if lookahead_fn(current_token) in sync_set:
                return current_token

        return current_token   # reached EOF

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _terminal_key(token) -> str:
        """Mirror of Parser._get_terminal_key — kept here to avoid circular imports."""
        if token.type == "EOF":
            return "EOF"
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