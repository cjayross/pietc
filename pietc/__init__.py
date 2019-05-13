import pietc.piet as piet
Operation = piet.Operation

DEFAULT_ENV = {
    '+' : Operation(piet.associative_binary_op, piet.add_op),
    '-' : Operation(piet.associative_binary_op, piet.subtract_op),
    '*' : Operation(piet.associative_binary_op, piet.multiply_op),
    '/' : Operation(piet.associative_binary_op, piet.divide_op),
    'modulo' : Operation(piet.strict_binary_op, piet.modulo_op),
    'eq?' : Operation(piet.strict_binary_op, piet.equal_op),
    '>' : Operation(piet.strict_binary_op, piet.greater_op),
    '<' : Operation(piet.strict_binary_op, piet.less_op),
    '>=' : Operation(piet.strict_binary_op, piet.greater_or_equal_op),
    '<=' : Operation(piet.strict_binary_op, piet.less_or_equal_op),
    'not' : Operation(piet.unary_op, piet.not_op),
    'or' : Operation(piet.associative_binary_op, piet.or_op),
    'and' : Operation(piet.associative_binary_op, piet.and_op),
}