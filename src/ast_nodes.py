class ASTNode:
    """Base class for all AST nodes."""
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements 

class Assign(ASTNode):
    def __init__(self,target, value):
        self.target = target #identifier node
        self.value = value # expression node <Binary operator, number>

class IfStmt(ASTNode):
    def __init__(self, condition, true_block, false_block):
        self.condition = condition
        self.true_block = true_block 
        self.false_block = false_block 

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition 
        self.body = body

class Condition(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class BinOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value