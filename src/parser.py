from lexer import Scanner
from tokens import Token


class Parser:
    """
    Top-down recursive descent parser.
    Validates syntax by consuming tokens from the scanner.
    """

    def __init__(self, scanner: Scanner):
        """
        Initialize the parser with a scanner instance.
        
        Args:
            scanner: A Scanner instance that provides tokens via get_next_token()
        """
        self.scanner = scanner
        self.current_token = None
        self._advance()  # Load the first token

    def _advance(self):
        """
        Private helper to fetch the next token from the scanner.
        Called internally to move to the next token.
        """
        self.current_token = self.scanner.get_next_token()

    def match(self, expected_type: str, expected_value=None) -> bool:
        """
        Validate if current token matches expected type/value WITHOUT consuming it.
        This is a lookahead/prediction method used by the parser to decide
        which grammar rule to apply.
        
        Args:
            expected_type: The token type to match (e.g., "KEYWORD", "IDENTIFIER")
            expected_value: Optional specific value (e.g., "if", "+")
            
        Returns:
            True if current token matches, False otherwise
        """
        if self.current_token.type != expected_type:
            return False
        if expected_value is not None and self.current_token.value != expected_value:
            return False
        return True

    def consume(self, expected_type: str, expected_value=None) -> Token:
        """
        Validate AND consume the current token if it matches expectations.
        Raises a syntax error if the token doesn't match.
        This is the core method for consuming tokens in the grammar rules.
        
        Args:
            expected_type: The expected token type
            expected_value: Optional expected specific value
            
        Returns:
            The consumed Token
            
        Raises:
            SyntaxError: If current token doesn't match expectations
        """
        if not self.match(expected_type, expected_value):
            expected = f"{expected_type}"
            if expected_value:
                expected += f" '{expected_value}'"
            raise SyntaxError(
                f"Line {self.current_token.line}: Expected {expected}, "
                f"got {self.current_token.type} '{self.current_token.value}'"
            )
        
        consumed = self.current_token
        self._advance()  # Move to next token
        return consumed

    def expect(self, expected_type: str, expected_value=None) -> Token:
        """
        Alias for consume() - validates and consumes the token.
        Used when we definitely expect a specific token in the grammar.
        """
        return self.consume(expected_type, expected_value)

    def check(self, expected_type: str, expected_value=None) -> bool:
        """
        Alias for match() - checks without consuming.
        Useful for optional elements or choosing between alternatives.
        """
        return self.match(expected_type, expected_value)

    def is_at_end(self) -> bool:
        """
        Check if we've reached the end of input (EOF token).
        """
        return self.current_token.type == "EOF"
