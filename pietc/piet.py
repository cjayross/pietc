import numpy as np
from pietc.eval import Sequence, LambdaSequence, IfElseSequence

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

active_lambdas = []

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

class Jump (object):
    def __init__ (self, dest):
        self.dest = dest

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.dest)

class Operation (object):
    def __init__ (self, optype, op):
        self.optype = optype
        self.op = op

    def __call__ (self, seq, args):
        return self.optype(seq, args, op=self.op)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.op.__name__)

class Parameter (object):
    """
    Define a lambda argument so that it can be identified across
    separate lambda calls.

    Note that the parameter's value is not stored since identifying
    this parameter's location in the stack is sufficient.
    """
    def __init__ (self, symbol, lamda_seq):
        self.lamda_seq = lamda_seq
        self.symbol = symbol

    @property
    def param_depth (self):
        return self.lamda_seq.param_depth(self)

    @property
    def value (self):
        return self.lamda_seq.local_env[self]

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.symbol)

    def __call__ (self, seq, args):
        idx = self.lamda_seq.param_offset[self]
        function = self.lamda_seq.args[idx]
        return function(seq, args)

def broadcast_stack_change (stack_delta):
    for seq in active_lambdas:
        seq.stack_offset += stack_delta

def unary_op (seq, args, op):
    if len(args) != 1:
        raise RuntimeError('%s: invalid number of arguments' % op.__name__)
    op(seq, *args)

def binary_op (seq, args, op):
    if len(args) < 2:
        raise RuntimeError('%s: insufficient number of arguments' % op.__name__)
    op(seq, *args[0:2])
    broadcast_stack_change(1)

def strict_binary_op (seq, args, op):
    if len(args) > 2:
        raise RuntimeError('%s: too many arguments' % op.__name__)
    binary_op(seq, args, op)

def associative_binary_op (seq, args, op):
    binary_op(seq, args, op)
    for arg in args[2:]:
        op(seq, arg)

def jump_op (seq, dest):
    if isinstance(dest, LambdaSequence):
        active_lambdas.append(dest)
        push_op(seq, *dest.args)
        seq.append(Jump(dest))
        stack_size = len(dest.params)
        for _ in range(stack_size):
            if dest.stack_offset != 0:
                seq.append(Push(dest.stack_offset, -1))
                seq.append(Command('roll'))
            seq.append(Command('pop'))
        if stack_size != 0:
            broadcast_stack_change(-stack_size)
        active_lambdas.remove(dest)
    else:
        seq.append(Jump(dest))

def push_op (seq, *args):
    """
    Place a set of arguments onto the top of the stack.
    """
    for arg in args:
        if isinstance(arg, (int, float)):
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
        elif issubclass(arg.__class__, Sequence):
            jump_op(seq, arg)
        else:
            seq.append(Push(0))
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

def modulo_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('mod'))

def equal_op (seq, *args):
    push_op(seq, *args)
    seq.append(Command('subtract'))
    seq.append(Command('not'))

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
    # NOTE: should the result of this op be normalized?
    add_op(seq, *args)

def and_op (seq, *args):
    # NOTE: should the result of this op be normalized?
    multiply_op(seq, *args)
