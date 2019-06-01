import numpy as np
from collections import deque
from pietc.eval import Parameter, Sequence, LambdaSequence
from pietc.debug import debuginfo

COMMAND_DIFFERENTIALS = {
    'push' : (0,1),
    'pop' : (0,2),
    'add' : (1,0),
    'subtract' : (1,1),
    'multiply' : (1,2),
    'divide' : (2,0),
    'mod' : (2,1),
    'not' : (2,2),
    'greater' : (3,0),
    'pointer' : (3,1),
    'switch' : (3,2),
    'duplicate' : (4,0),
    'roll' : (4,1),
    'in_int' : (4,2),
    'in' : (5,0),
    'out_int' : (5,1),
    'out' : (5,2),
}

active_lambdas = deque()

class Command (object):
    def __init__ (self, name):
        self.name = name
        self.has_args = False
        try:
            self.shift = np.asarray(COMMAND_DIFFERENTIALS[self.name])
        except KeyError:
            raise RuntimeError('invalid command: %s' % self.name)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.name)

class Push (Command):
    def __init__ (self, *values):
        if not values:
            raise RuntimeError('push: insufficient number of arguments')
        super().__init__(name='push')
        self.args = values
        self.has_args = True

    def __repr__ (self):
        return '{}{}'.format(self.__class__.__name__, self.args)

class Operation (object):
    def __init__ (self, optype, op):
        self.optype = optype
        self.op = op

    def __call__ (self, seq, args):
        return self.optype(seq, args, op=self.op) \
            if self.optype else self.op(seq, args)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.op.__name__)

class Conditional (object):
    """
    Represent an abstracted choice between two s-expressions.

    The handling of conditional expressions is done manually since
    conditionals are not allowed to be evaluated until simulated or drawn.
    """
    def __init__ (self, if_sexpr, else_sexpr, env):
        self.test_seq = Sequence(None, env)
        self.if_sexpr = if_sexpr
        self.else_sexpr = else_sexpr
        self.seq = None
        self.env = env

    @property
    def has_choice (self):
        return self.seq is not None

    @property
    def choice (self):
        return self.seq.sexpr

    @choice.setter
    def choice (self, value):
        sexpr = self.if_sexpr if value else self.else_sexpr
        self.seq = Sequence(sexpr, self.env)

    def __call__ (self, seq, args):
        if not self.has_choice:
            debuginfo('{}({})', self, args, prefix='conditional call')
            return ConditionalLambda(self, args)
        function = self.seq.evaluate()
        debuginfo('{}({})', function, args, prefix='conditional call')
        return function(seq, args)

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.if_sexpr, self.else_sexpr)

class ConditionalLambda (Conditional, Sequence):
    """
    Represent a Conditional with stored arguments.
    """
    def __init__ (self, conditional, args):
        self.conditional = conditional
        self.args = args

    @property
    def choice (self):
        return self.conditional.choice

    @choice.setter
    def choice (self, value):
        self.conditional.choice = value

    def evaluate (self):
        if self.has_choice:
            return self.choice(self, self.args)

    def __getattr__ (self, attr):
        if hasattr(self.conditional, attr):
            return getattr(self.conditional, attr)
        return Sequence.__getattribute__(self, attr)

    def __repr__ (self):
        return '{}([{}, {}], {})'.format(self.__class__.__name__,
                                         self.conditional.if_sexpr,
                                         self.conditional.else_sexpr,
                                         self.args)

def broadcast_stack_change (stack_delta):
    for seq in active_lambdas:
        seq.stack_offset += stack_delta
        debuginfo('{} ({} -> {})',
                  seq, seq.stack_offset-stack_delta,
                  seq.stack_offset,
                  prefix='broadcast')

def unary_op (seq, args, op):
    if len(args) != 1:
        raise RuntimeError('%s: invalid number of arguments' % op.__name__)
    op(seq, *args)

def binary_op (seq, args, op):
    if len(args) < 2:
        raise RuntimeError('%s: insufficient number of arguments' % op.__name__)
    op(seq, *args[0:2])
    broadcast_stack_change(-1)

def strict_binary_op (seq, args, op):
    if len(args) > 2:
        raise RuntimeError('%s: too many arguments' % op.__name__)
    binary_op(seq, args, op)

def associative_binary_op (seq, args, op):
    binary_op(seq, args, op)
    for arg in args[2:]:
        op(seq, arg)

def condition_op (seq, args):
    test_sexpr, if_sexpr, else_sexpr = args if len(args) == 3 else (*args, None)
    cond = Conditional(if_sexpr, else_sexpr, seq.env)
    push_op(cond.test_seq, test_sexpr)
    # a jump call pops a value off of the stack.
    broadcast_stack_change(-1)
    # this operation returns a value since it does not push onto the stack.
    return cond

def push_op (seq, *args):
    """
    Place a set of arguments onto the top of the stack.
    """
    for arg in args:
        if isinstance(arg, int):
            seq.append(Push(arg))
            broadcast_stack_change(1)
        elif isinstance(arg, (Sequence, Conditional)):
            seq.append(Push(arg))
        elif isinstance(arg, Parameter):
            # depth = param depth + stack depth
            depth = arg.param_depth
            if depth != 0:
                seq.append(Push(depth, -1))
                seq.append(Command('roll'))
                # param depth -= 1, stack depth += 1
            seq.append(Command('duplicate'))
            # stack depth += 1
            if depth != 0:
                seq.append(Push(depth + 1, 1))
                seq.append(Command('roll'))
                # param depth += 1, stack depth -= 1
            broadcast_stack_change(1)
        else:
            # evaluate calls that return None are assumed to push a value.
            broadcast_stack_change(1)

def add_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('add'))

def subtract_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('subtract'))

def multiply_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('multiply'))

def divide_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('divide'))

def negate_op (seq, *args):
    push_op(seq, 0, *args)
    seq.append(Command('subtract'))

def modulo_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('mod'))

def equal_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('subtract'))
    seq.append(Command('not'))

def not_equal_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('subtract'))

def greater_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('greater'))

def less_op (seq, *args):
    push_op(seq, *args)
    seq.append(Push(1, 1))
    seq.append(Command('roll'))
    seq.append(Command('greater'))

def greater_or_equal_op (seq, *args):
    less_op(seq, *args)
    seq.append(Command('not'))

def less_or_equal_op (seq, *args):
    greater_op(seq, *args)
    seq.append(Command('not'))

def not_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('not'))

def or_op (seq, *args):
    add_op(seq, *args)

def and_op (seq, *args):
    multiply_op(seq, *args)
