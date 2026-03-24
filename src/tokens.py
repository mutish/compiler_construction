KEYWORDS = ["if", "else", "while"]
OPERATORS = ['+', '-', '*', '/', '!=', '=', '==', '<', '>', '<=', '>=']
SEPARATORS = ['(', ')', '{', '}', ';', ',', ':']
class Token:

    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"<{self.type}, \"{self.value}\", line {self.line}>"
       