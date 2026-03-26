from tokens import Token # from tokens.py



class Scanner:
    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1

    def get_next_token(self):
        while self.pos < len(self.source):
            char = self.source[self.pos]

            # Skip Whitespace
            if char.isspace():
                if char == '\n':
                    self.line += 1
                self.pos += 1
                continue
                    
            

            # State: Identifier or Keyword
            if char.isalpha() or char == '_':
                lexeme = ""
                while self.pos < len(self.source) and (self.source[self.pos].isalnum()or self.source[self.pos] == '_'):
                    lexeme += self.source[self.pos]
                    self.pos += 1

                # Keyword check
                if lexeme in ["if", "else", "while"]:
                    return Token("KEYWORD", lexeme, self.line)
                return Token("IDENTIFIER", lexeme, self.line)
            
            # State: Number
            if char.isdigit():
                lexeme = ""
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    lexeme += self.source[self.pos]
                    self.pos += 1
                return Token("NUMBER", lexeme, self.line)
            
            # State: Strings
            if char == '"':
                lexeme = '"'
                self.pos += 1 #consume opening quote
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    lexeme += self.source[self.pos]
                    self.pos += 1
                # Consume closing quote safely
                if self.pos < len(self.source) and self.source[self.pos] == '"':
                    lexeme += '"'
                    self.pos += 1
                    return Token("STRING", lexeme, self.line)
                raise Exception(f"Lexical Error: Unterminated string literal at line {self.line}")


            # Operators
            if char in ['+', '-', '*', '/', '=', '!', '<', '>']:
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=' and char in ['=', '!']:
                    operator = char + '='
                    self.pos += 2
                    return Token("OPERATOR", operator, self.line)
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=' and char in ['<', '>']:
                    operator = char + '='
                    self.pos += 2
                    return Token("OPERATOR", operator, self.line)
                else:
                    self.pos += 1
                    return Token("OPERATOR", char, self.line)
            
            # Separators
            if char in ['(', ')', '{', '}', ';', ',',':']:
                self.pos += 1
                return Token("SEPARATOR", char, self.line)
            
            # Emit unknown symbols as scanner output instead of stopping execution.
            self.pos += 1
            return Token("Unidentified", char, self.line)
        return Token("EOF", "EOF", self.line)
            
