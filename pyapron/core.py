from lib import libapron, libpolka
import ctypes

# Texpr1 operators
AP_TEXPR_ADD = 0
AP_TEXPR_SUB = 1
AP_TEXPR_MUL = 2
AP_TEXPR_DIV = 3

# Operators names
op_name = {
    AP_TEXPR_ADD: '+',
    AP_TEXPR_SUB: '-',
    AP_TEXPR_MUL: '*',
    AP_TEXPR_DIV: '/'
}

# Rounding type
AP_RTYPE_INT = 1

# Rounding direction
AP_RDIR_NEAREST = 0

# Allocate apron manager
ap_man = libpolka.pk_manager_alloc(ctypes.c_int(1))
assert(ap_man != 0)

# Create apron texpr1 binary expression
def texpr1_bin(op, e1, e2):
    rtype = AP_RTYPE_INT
    rdir = AP_RDIR_NEAREST

    # copy e1.ap_expr
    lhs = libapron.ap_texpr1_copy(e1.ap_expr)
    assert(lhs != 0)
    
    # copy e2.ap_expr
    rhs = libapron.ap_texpr1_copy(e2.ap_expr)
    assert(rhs != 0)

    # compute least common environment
    dimchange1 = ctypes.c_char_p(0)
    dimchange2 = ctypes.c_char_p(0)
    lce = libapron.ap_environment_lce(e1.ap_env,
                                      e2.ap_env,
                                      ctypes.byref(dimchange1),
                                      ctypes.byref(dimchange2))
    assert(lce != 0)

    # change environment of lhs
    lhs = libapron.ap_texpr1_extend_environment(lhs, lce)
    assert(lhs != 0)

    # change environment rhs
    rhs = libapron.ap_texpr1_extend_environment(rhs, lce)
    assert(rhs != 0)

    # create binary texpr1
    ap_expr = libapron.ap_texpr1_binop(op,
                                       lhs,
                                       rhs,
                                       rtype,
                                       rdir)
    assert(ap_expr != 0)
    return (ap_expr, lce)


# Expressions abstract class
class Expr():
    def __add__(self, other):
        if isinstance(other, int):
            return BinaryExpr(AP_TEXPR_ADD, self, IntExpr(other))
        else:
            assert(isinstance(other, Expr))
            return BinaryExpr(AP_TEXPR_ADD, self, other)

    def __radd__(self, other):
        assert(isinstance(other, int))
        return BinaryExpr(AP_TEXPR_ADD, IntExpr(other), self)

    def __sub__(self, other):
        if isinstance(other, int):
            return BinaryExpr(AP_TEXPR_SUB, self, IntExpr(other))
        else:
            assert(isinstance(other, Expr))
            return BinaryExpr(AP_TEXPR_SUB, self, other)

    def __rsub__(self, other):
        assert(isinstance(other, int))
        return BinaryExpr(AP_TEXPR_SUB, IntExpr(other), self)

    def __mul__(self, other):
        if isinstance(other, int):
            return BinaryExpr(AP_TEXPR_MUL, self, IntExpr(other))
        else:
            assert(isinstance(other, Expr))
            return BinaryExpr(AP_TEXPR_MUL, self, other)

    def __rmul__(self, other):
        assert(isinstance(other, int))
        return BinaryExpr(AP_TEXPR_MUL, IntExpr(other), self)

    def __div__(self, other):
        if isinstance(other, int):
            return BinaryExpr(AP_TEXPR_DIV, self, IntExpr(other))
        else:
            assert(isinstance(other, Expr))
            return BinaryExpr(AP_TEXPR_DIV, self, other)

    def __rdiv__(self, other):
        assert(isinstance(other, int))
        return BinaryExpr(AP_TEXPR_DIV, IntExpr(other), self)


# BinaryExpr
class BinaryExpr(Expr):
    def __init__(self, op, e1, e2):
        self.ap_expr, self.ap_env = texpr1_bin(op, e1, e2)
        self.op = op
        self.lhs = e1
        self.rhs = e2


# IntExpr
class IntExpr(Expr):
    def __init__(self, x):
        ap_env = libapron.ap_environment_alloc_empty()
        assert(ap_env != 0)
        ap_expr = libapron.ap_texpr1_cst_scalar_int(ap_env,
                                                    ctypes.c_long(x))
        assert(ap_expr != 0)
        self.value = x
        self.ap_expr = ap_expr
        self.ap_env = ap_env

    def __str__(self):
        return str(self.value)


# Variable
class Var(Expr):
    def __init__(self, name):
        self.name = name

        # create apron variable
        ap_var = ctypes.c_char_p(name)

        # create apron environment
        ap_env = libapron.ap_environment_alloc(ctypes.byref(ap_var), 
                                               ctypes.c_size_t(1), 
                                               ctypes.c_char_p(0), 
                                               ctypes.c_size_t(0))
        assert(ap_env != 0)

        # create apron tree expression
        ap_expr = libapron.ap_texpr1_var(ap_env, ap_var)
        assert(ap_expr != 0)

        self.ap_var = ap_var
        self.ap_env = ap_env
        self.ap_expr = ap_expr

    def __str__(self):
        return self.name


class Constraint():
    def __init__(self, const_type, lhs, rhs):
        pass