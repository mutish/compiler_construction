from quadruple import Quadruple
from ast_nodes import *
from ast_builder import ASTBuilder


class ICGenerator:
    """
    Intermediate Code Generator.

    Walks a typed AST (produced by ASTBuilder) and emits a flat list of
    Quadruples that represent three-address code (TAC).

    Counters
    --------
    _temp_count  : int  – incremented each time a new temporary is needed.
                          Temporaries are named  t1, t2, t3, …
    _label_count : int  – incremented each time a new label is needed.
                          Labels are named  L1, L2, L3, …

    Public interface
    ----------------
    generate(ast_node)  – top-level entry point; returns the completed
                          quadruple list after walking the entire AST.
    emit(op, a1, a2, result) – append one Quadruple to self.quads.
    new_temp()          – allocate and return the next temporary name.
    new_label()         – allocate and return the next label name.
    print_quads()       – pretty-print the generated code.
    """

    def __init__(self):
        self._temp_count  = 0   # last used temp index  (0 = none issued yet)
        self._label_count = 0   # last used label index
        self.quads: list[Quadruple] = []   # the generated instruction stream

    # ------------------------------------------------------------------
    # Counter helpers
    # ------------------------------------------------------------------

    def new_temp(self) -> str:
        """Return the next unique temporary variable name (e.g. 't1')."""
        self._temp_count += 1
        return f"t{self._temp_count}"

    def new_label(self) -> str:
        """Return the next unique label name (e.g. 'L1')."""
        self._label_count += 1
        return f"L{self._label_count}"

    # ------------------------------------------------------------------
    # Emission helper
    # ------------------------------------------------------------------

    def emit(self, op, arg1, arg2, result) -> Quadruple:
        """Create a Quadruple, append it to self.quads, and return it."""
        quad = Quadruple(op, arg1, arg2, result)
        self.quads.append(quad)
        return quad

    # ------------------------------------------------------------------
    # Main dispatcher
    # ------------------------------------------------------------------

    def generate(self, ast_node):
        """
        Route an AST node to the appropriate generation method.

        For expression / condition nodes this returns the name of the
        temporary (or literal string) that holds the computed value.
        For statement nodes it returns None.
        """
        if ast_node is None:
            return None

        # ── Statements ─────────────────────────────────────────────────
        if isinstance(ast_node, Program):
            return self._gen_program(ast_node)

        if isinstance(ast_node, Assign):
            return self._gen_assign(ast_node)

        if isinstance(ast_node, IfStmt):
            return self._gen_if(ast_node)

        if isinstance(ast_node, WhileStmt):
            return self._gen_while(ast_node)

        # ── Expressions ────────────────────────────────────────────────
        if isinstance(ast_node, BinOp):
            return self._gen_binop(ast_node)

        if isinstance(ast_node, Condition):
            return self._gen_condition(ast_node)

        if isinstance(ast_node, Identifier):
            return ast_node.name          # already a plain name – no quad needed

        if isinstance(ast_node, Number):
            return str(ast_node.value)    # inline literal

        if isinstance(ast_node, StringLiteral):
            return ast_node.value         # keep the quoted string as-is

        raise NotImplementedError(
            f"ICGenerator.generate: unhandled node type '{type(ast_node).__name__}'"
        )

    # ------------------------------------------------------------------
    # Statement generators
    # ------------------------------------------------------------------

    def _gen_program(self, node: Program):
        """Generate code for every statement in the program."""
        for stmt in node.statements:
            self.generate(stmt)

    def _gen_assign(self, node: Assign):
        """
        assignment -> ID = expr
        Evaluate the right-hand side then copy the result into the target.
        """
        rhs = self.generate(node.value)           # evaluate expr → temp or literal
        self.emit("=", rhs, None, node.target.name)

    def _gen_if(self, node: IfStmt):
        """
        if <cond>: <true_block> else: <false_block>

        Generated TAC pattern:
            <evaluate condition into t_cond>
            if_false t_cond goto L_false
            <true block>
            goto L_end
        L_false:
            <false block>
        L_end:
        """
        l_false = self.new_label()
        l_end   = self.new_label()

        cond_temp = self.generate(node.condition)
        self.emit("if_false", cond_temp, None, l_false)

        self.generate(node.true_block)
        self.emit("goto", None, None, l_end)

        self.emit("label", None, None, l_false)
        self.generate(node.false_block)

        self.emit("label", None, None, l_end)

    def _gen_while(self, node: WhileStmt):
        """
        while <cond>: <body>

        Generated TAC pattern:
        L_start:
            <evaluate condition into t_cond>
            if_false t_cond goto L_end
            <body>
            goto L_start
        L_end:
        """
        l_start = self.new_label()
        l_end   = self.new_label()

        self.emit("label", None, None, l_start)

        cond_temp = self.generate(node.condition)
        self.emit("if_false", cond_temp, None, l_end)

        self.generate(node.body)
        self.emit("goto", None, None, l_start)

        self.emit("label", None, None, l_end)

    # ------------------------------------------------------------------
    # Expression generators  (each returns the name holding the result)
    # ------------------------------------------------------------------

    def _gen_binop(self, node: BinOp) -> str:
        """
        BinOp(op, left, right)  →  t = left op right
        Returns the temporary that holds the result.
        """
        left  = self.generate(node.left)
        right = self.generate(node.right)
        temp  = self.new_temp()
        self.emit(node.op, left, right, temp)
        return temp

    def _gen_condition(self, node: Condition) -> str:
        """
        Condition(op, left, right)  →  t = left relop right
        Returns the temporary that holds the boolean result (0 or 1).
        """
        left  = self.generate(node.left)
        right = self.generate(node.right)
        temp  = self.new_temp()
        self.emit(node.op, left, right, temp)
        return temp

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def print_quads(self):
        """Print all generated quadruples in human-readable TAC form."""
        print("\n---- Intermediate Code (Three-Address Code) ----")
        for i, quad in enumerate(self.quads):
            print(f"{i:>3}: {quad}")
