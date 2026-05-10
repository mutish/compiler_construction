class Quadruple:
    """
    Represents a single three-address instruction in the form:
        (op, arg1, arg2, result)

    Examples
    --------
    Arithmetic :  ('+',  't1', 't2', 't3')   →  t3 = t1 + t2
    Assignment :  ('=',  'x',  None,  't1')  →  t1 = x
    Comparison :  ('<',  't1', 't2', 't3')   →  t3 = t1 < t2
    Jump       :  ('goto', None, None, 'L1') →  goto L1
    Cond jump  :  ('if_false', 't1', None, 'L2') →  if_false t1 goto L2
    Label      :  ('label', None, None, 'L1') →  L1:
    """

    def __init__(self, op, arg1, arg2, result):
        self.op     = op      # operator / instruction mnemonic
        self.arg1   = arg1    # first operand  (or None)
        self.arg2   = arg2    # second operand (or None)
        self.result = result  # destination / target label (or None)

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"Quadruple(op={self.op!r}, arg1={self.arg1!r}, "
            f"arg2={self.arg2!r}, result={self.result!r})"
        )

    def __str__(self):
        """Human-readable three-address form used when printing the ICG output."""
        op = self.op

        # ── label ──────────────────────────────────────────────────────
        if op == "label":
            return f"{self.result}:"

        # ── unconditional jump ─────────────────────────────────────────
        if op == "goto":
            return f"    goto {self.result}"

        # ── conditional jumps ──────────────────────────────────────────
        if op in ("if_true", "if_false"):
            return f"    {op} {self.arg1} goto {self.result}"

        # ── simple copy / assignment  (arg2 is None) ───────────────────
        if self.arg2 is None:
            return f"    {self.result} = {self.arg1}"

        # ── binary operation ───────────────────────────────────────────
        return f"    {self.result} = {self.arg1} {op} {self.arg2}"
