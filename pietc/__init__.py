import pietc.piet as piet
from pietc.eval import Sequence, Environment
Operation = piet.Operation

DEFAULT_ENV = Environment({
    'if' : Operation(None, piet.condition_op),
    '+' : Operation(piet.associative_binary_op, piet.add_op),
    '-' : Operation(piet.associative_binary_op, piet.subtract_op),
    '*' : Operation(piet.associative_binary_op, piet.multiply_op),
    '/' : Operation(piet.associative_binary_op, piet.divide_op),
    'negate' : Operation(piet.unary_op, piet.negate_op),
    'modulo' : Operation(piet.strict_binary_op, piet.modulo_op),
    'eq' : Operation(piet.strict_binary_op, piet.equal_op),
    'neq' : Operation(piet.strict_binary_op, piet.not_equal_op),
    '>' : Operation(piet.strict_binary_op, piet.greater_op),
    '<' : Operation(piet.strict_binary_op, piet.less_op),
    '>=' : Operation(piet.strict_binary_op, piet.greater_or_equal_op),
    '<=' : Operation(piet.strict_binary_op, piet.less_or_equal_op),
    'not' : Operation(piet.unary_op, piet.not_op),
    'or' : Operation(piet.associative_binary_op, piet.or_op),
    'and' : Operation(piet.associative_binary_op, piet.and_op),
})

class Program (Sequence):
    def __init__ (self):
        super().__init__([], DEFAULT_ENV)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, list(self))
