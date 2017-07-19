
from .tagged_object import TaggedObject


class Statement(TaggedObject):
    """
    The base class of all AIL statements.
    """

    def __init__(self, idx, **kwargs):
        super(Statement, self).__init__(**kwargs)

        self.idx = idx

    def __repr__(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def replace(self, old_expr, new_expr):
        raise NotImplementedError()


class Assignment(Statement):
    """
    Assignment statement: expr_a = expr_b
    """
    def __init__(self, idx, dst, src, **kwargs):
        super(Assignment, self).__init__(idx, **kwargs)

        self.dst = dst
        self.src = src

    def __repr__(self):
        return "Assignment (%s, %s)" % (self.dst, self.src)

    def __str__(self):
        return "%s = %s" % (str(self.dst), str(self.src))

    def replace(self, old_expr, new_expr):

        r_dst, replaced_dst = self.dst.replace(old_expr, new_expr)
        r_src, replaced_src = self.src.replace(old_expr, new_expr)

        if r_dst or r_src:
            return True, Assignment(self.idx, replaced_dst, replaced_src, **self.tags)
        else:
            return False, self


class Store(Statement):
    def __init__(self, idx, addr, data, size, variable=None, **kwargs):
        super(Store, self).__init__(idx, **kwargs)

        self.addr = addr
        self.data = data
        self.size = size
        self.variable = variable

    def __repr__(self):
        return "Store (%s, %s[%d])" % (self.address, str(self.data), self.size)

    def __str__(self):
        if self.variable is None:
            return "STORE(addr=%s, data=%s, size=%s)" % (self.addr, str(self.data), self.size)
        else:
            return "%s = %s<%d>" % (self.variable.name, str(self.data), self.size)

    def replace(self, old_expr, new_expr):
        r_addr, replaced_addr = self.addr.replace(old_expr, new_expr)
        r_data, replaced_data = self.data.replace(old_expr, new_expr)

        if r_addr or r_data:
            return True, Store(self.idx, replaced_addr, replaced_data, self.size, self.variable, **self.tags)
        else:
            return False, self


class Jump(Statement):
    def __init__(self, idx, target, **kwargs):
        super(Jump, self).__init__(idx, **kwargs)

        self.target = target

    def __str__(self):
        return "Goto(%s)" % self.target

    def replace(self, old_expr, new_expr):
        r, replaced_target = self.target.replace(old_expr, new_expr)

        if r:
            return True, Jump(self.idx, replaced_target, **self.tags)
        else:
            return False, self


class ConditionalJump(Statement):
    def __init__(self, idx, condition, true_target, false_target, **kwargs):
        super(ConditionalJump, self).__init__(idx, **kwargs)

        self.condition = condition
        self.true_target = true_target
        self.false_target = false_target

    def __str__(self):
        return "if (%s) { Goto %s } else { Goto %s }" % (
            self.condition,
            self.true_target,
            self.false_target,
        )

    def replace(self, old_expr, new_expr):
        r_cond, replaced_cond = self.condition.replace(old_expr, new_expr)
        r_true, replaced_true = self.true_target.replace(old_expr, new_expr)
        r_false, replaced_false = self.false_target.replace(old_expr, new_expr)

        r = r_cond or r_true or r_false

        if r:
            return True, ConditionalJump(self.idx, replaced_cond, replaced_true, replaced_false, **self.tags)
        else:
            return False, self


class Call(Statement):
    def __init__(self, idx, target, calling_convention=None, declaration=None, args=None, **kwargs):
        super(Call, self).__init__(idx, **kwargs)

        self.target = target
        self.calling_convention = calling_convention
        self.declaration = declaration
        self.args = args

    def __str__(self):

        cc = "Unknown CC" if self.calling_convention is None else "%s" % self.calling_convention
        if self.args is None:
            s = ("%s" % cc) if self.declaration is None else "%s: %s" % (self.calling_convention, self.calling_convention.arg_locs())
        else:
            s = ("%s" % cc) if self.declaration is None else "%s: %s" % (self.calling_convention, self.args)

        return "Call(%s, %s)" % (
            self.target,
            s
        )

    def replace(self, old_expr, new_expr):
        r0, replaced_target = self.target.replace(old_expr, new_expr)

        r = r0

        new_args = None
        if self.args:
            new_args = [ ]
            for arg in self.args:
                r_arg, replaced_arg = arg.replace(old_expr, new_expr)
                r |= r_arg
                new_args.append(replaced_arg)

        if r:
            return True, Call(self.idx, replaced_target,
                              calling_convention=self.calling_convention,
                              declaration=self.declaration,
                              args=new_args,
                              **self.tags
                              )
        else:
            return False, self


class DirtyStatement(Statement):
    """
    Wrapper around the original statement, which is usually not convertible (temporarily).
    """
    def __init__(self, idx, dirty_stmt, **kwargs):
        super(DirtyStatement, self).__init__(idx, **kwargs)
        self.dirty_stmt = dirty_stmt

    def __repr__(self):
        return "DirtyStatement (%s)" % (type(self.dirty_stmt))

    def __str__(self):
        return "[D] %s" % (str(self.dirty_stmt))
