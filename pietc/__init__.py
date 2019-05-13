import pietc.piet as piet
from functools import partial

DEFAULT_ENV = {
    '+' : partial(piet.associative_binary_op, op=piet.add_op),
    '-' : partial(piet.associative_binary_op, op=piet.subtract_op),
    '*' : partial(piet.associative_binary_op, op=piet.multiply_op),
    '/' : partial(piet.associative_binary_op, op=piet.divide_op),
    'modulo' : partial(piet.strict_binary_op, op=piet.modulo_op),
    'eq?' : partial(piet.strict_binary_op, op=piet.equal_op),
    '>' : partial(piet.strict_binary_op, op=piet.greater_op),
    '<' : partial(piet.strict_binary_op, op=piet.less_op),
    '>=' : partial(piet.strict_binary_op, op=piet.greater_or_equal_op),
    '<=' : partial(piet.strict_binary_op, op=piet.less_or_equal_op),
    'not' : partial(piet.unary_op, op=piet.not_op),
    'or' : partial(piet.associative_binary_op, op=piet.or_op),
    'and' : partial(piet.associative_binary_op, op=piet.and_op),
}
