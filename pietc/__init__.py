import pietc.piet as piet
from pietc.eval import Sequence, Environment

DEFAULT_ENV = Environment({
    '+' : piet.add_op,
    '-' : piet.subtract_op,
    '*' : piet.multiply_op,
    '/' : piet.divide_op,
    '>' : piet.greater_op,
    '<' : piet.less_op,
    '>=' : piet.greater_or_equal_op,
    '<=' : piet.less_or_equal_op,
    'if' : piet.condition_op,
    'modulo' : piet.modulo_op,
    'eq' : piet.equal_op,
    'neq' : piet.not_equal_op,
    'not' : piet.not_op,
    'or' : piet.or_op,
    'and' : piet.and_op,
})

class Program (Sequence):
    def __init__ (self):
        super().__init__([], DEFAULT_ENV)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, list(self))
