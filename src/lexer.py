class Scanner:
    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1

    def get_next_token(self):
        while self.pos < len(self.source):
            char = self.source[self.pos]

            # Skip Whitespace
            if char.issspace():
                if char == '\n':
                    self.pos += 1
                    continue
            

            # State: Identifier or Keyword
            if char.isalpha() or char == '_':
                lexeme = ""
                while self.pos < len(self.source) and (self.source[self.pos].isalnum()or self.source[self.pos] == '_'):
                    lexeme += self.source[self.pos]
                    self.pos += 1

                # Keyword check
                if lexeme in ["if", "else", "while", "return"]:
                    return("KEYWORD", lexeme, self.line)
                return ("IDENTIFIER", lexeme, self.line)
            
            # State: Number
            if char.isdigit():
                lexeme = ""
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    lexeme += self.source[self.pos]
                    self.pos += 1
                return ("NUMBER", lexeme, self.line)
            
            # Operators
            if char in ['+', '-', '*', '/', '!=', '=', '==']:
                self.pos += 1
                return ("OPERATOR", char, self.line)
            
            # Separators
            if char in ['(', ')', '{', '}', ';', ',',':']:
                self.pos += 1
                return ("SEPARATOR", char, self.line)
            
            # Error handling for unrecognized characters
            raise Exception(f"Lexical Error: Illegal character '{char}' at line  {self.line}")
        return ("EOF", None, self.line)
            
