from ast_nodes import *

class ASTBuilder:
    """
    Traverses a concrete parse tree and builds a clean AST;
    ignores structural artifacts like stmt_list_prime and expr_prime
    """

    def build(self, node):
        "Main dispatcher that routes a parse tree node to the right builder method"
        if not node:
            return None
        
        if node.symbol == "<program>":
            return self.build_program(node)
        elif node.symbol == "<stmt>":
            # stmt has only 1 child ie: statement, if_stmt or while_stmt
            return self.build(node.children[0])
        elif node.symbol == "<assignment>":
            return self.build_assignment(node)
        elif node.symbol == "<if_stmt>":
            return self.build_if_stmt(node)
        elif node.symbol == "<while_stmt>":
            return self.build_while_stmt(node)
        
        raise Exception(f"ASTBuilder: Unhandled node symbol: {node.symbol}")
    
    def build_program(self,node):
        # program -> stmt_list
        stmts = self.build_stmt_list(node.children[0])
        return Program(stmts)
    
    def build_stmt_list(self, node):
        """Flattens <stmt_list> and <stmt_list_prime>"""
        stmts = []
        current = node

        #traverse down the right recursive tree
        while current and current.symbol in ("<stmt_list>", "<stmt_list_prime>"):
            if not current.children or current.children[0].symbol in ("ε", "epsilon"):
                break

            #1st child ALWAYS a stmt
            stmt_node = current.children[0]
            stmts.append(self.build(stmt_node))

            if len(current.children) > 1:
                current = current.children[1] #move to stmt_list_prime
            else:
                break

        return stmts
    
    def build_assignment(self, node):
        # assignment -> ID "=" expr
        target = Identifier(node.children[0].lexeme)
        expr = self.build_expr(node.children[2])
        return Assign(target, expr)
    
    def build_stmt(self, node):
        """Route a statement node to the appropriate builder"""
        return self.build(node)
    
    def build_if_stmt(self, node):
        # <if_stmt> -> "if" <cond> ":" <stmt> "else" ":" <stmt>
        cond = self.build_cond(node.children[1])
        true_block = self.build_stmt(node.children[3])
        false_block = self.build_stmt(node.children[6])
        return IfStmt(cond, true_block, false_block)
    
    def build_while_stmt(self, node):
        # <while_stmt> -> "while" <cond> ":" <stmt>
        cond = self.build_cond(node.children[1])
        body = self.build_stmt(node.children[3])
        return WhileStmt(cond, body)
        
    def build_cond(self, node):
        # <cond> -> <expr> <relop> <expr>
        left = self.build_expr(node.children[0])
        op = node.children[1].lexeme
        right = self.build_expr(node.children[2])
        return Condition(op, left, right)
    
    def build_expr(self, node):
        # <expr> -> <term> <expr_prime>
        left = self.build_term(node.children[0])
        expr_prime = node.children[1]
        return self.build_expr_prime(expr_prime, left)
        

    def build_expr_prime(self, node, left):
        # <expr_prime> -> "+" <expr> | "-" <expr> | epsilon
        # When expr_prime has an operator, node.children[1] is <expr>, not <term>
        if not node.children or node.children[0].symbol in ("ε", "epsilon"):
            return left  # no math op, return term
        
        op = node.children[0].lexeme
        # node.children[1] is an <expr>, which recursively builds properly
        right = self.build_expr(node.children[1])
        return BinOp(op, left, right)

    def build_term(self, node):
        # <term> -> ID | NUM | STR
        child = node.children[0]
        if child.symbol == "ID":
            return Identifier(child.lexeme)
        elif child.symbol == "NUM":
            return Number(int(child.lexeme))
        elif child.symbol == "STR":
            return StringLiteral(child.lexeme)

        raise Exception(f"ASTBuilder: Undefined term type: {child.symbol}")