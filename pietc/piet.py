import numpy as np
from collections import deque
from pietc.eval import Sequence, LambdaSequence, Parameter, Conditional, Atom
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
    def __init__ (self, value):
        super().__init__(name='push')
        self.value = value

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.value)

def notify_stack_change (seq, stack_delta):
    if isinstance(seq, LambdaSequence):
        seq.stack_offset += stack_delta
        debuginfo('{} ({} -> {})',
                  seq, seq.stack_offset - stack_delta,
                  seq.stack_offset,
                  prefix='broadcast')

def condition_op (seq, *args):
    test_sexpr, if_sexpr, else_sexpr = args if len(args) == 3 else (*args, None)
    cond = Conditional(if_sexpr, else_sexpr, seq.env)
    push_op(cond.test_seq, test_sexpr)
    # a jump call pops a value off of the stack.
    notify_stack_change(seq, -1)
    # this operation returns a value since it does not push onto the stack.
    return cond

def push_op (seq, *args):
    """
    Place a set of arguments onto the top of the stack.
    """
    for arg in args:
        if isinstance(arg, int):
            seq.append(Push(arg))
            notify_stack_change(seq, 1)
        elif isinstance(arg, (Sequence, Conditional)):
            # the sequence will handle broadcasting stack changes
            seq.append(Push(arg))
        elif isinstance(arg, Parameter):
            # depth = param depth + stack depth
            depth = arg.param_depth
            if depth != 0:
                push_op(seq, depth, -1)
                roll_op(seq)
                # param depth -= 1, stack depth += 1
            duplicate_op(seq)
            # stack depth += 1
            if depth != 0:
                push_op(seq, depth + 1, 1)
                roll_op(seq)
                # param depth += 1, stack depth -= 1

def pop_op (seq, *args):
    seq.append(Command('pop'))
    notify_stack_change(seq, -1)

def duplicate_op (seq, *args):
    seq.append(Command('duplicate'))
    notify_stack_change(seq, 1)

def roll_op (seq, *args):
    seq.append(Command('roll'))
    notify_stack_change(seq, -2)

def add_op (seq, *args):
    for _ in range(len(args) - 1):
        seq.append(Command('add'))
        notify_stack_change(seq, -1)

def subtract_op (seq, *args):
    for _ in range(len(args) - 1):
        seq.append(Command('subtract'))
        notify_stack_change(seq, -1)

def multiply_op (seq, *args):
    for _ in range(len(args) - 1):
        seq.append(Command('multiply'))
        notify_stack_change(seq, -1)

def divide_op (seq, *args):
    for _ in range(len(args) - 1):
        seq.append(Command('divide'))
        notify_stack_change(seq, -1)

def modulo_op (seq, *args):
    seq.append(Command('mod'))
    notify_stack_change(seq, -1)

def greater_op (seq, *args):
    seq.append(Command('greater'))
    notify_stack_change(seq, -1)

def not_op (seq, *args):
    seq.append(Command('not'))

def equal_op (seq, *args):
    subtract_op(seq, *args)
    not_op(seq, *args)

def not_equal_op (seq, *args):
    subtract_op(seq, *args)

def less_op (seq, *args):
    push_op(seq, 1, 1)
    roll_op(seq, *args)
    greater_op(seq, *args)

def greater_or_equal_op (seq, *args):
    less_op(seq, *args)
    not_op(seq, *args)

def less_or_equal_op (seq, *args):
    greater_op(seq, *args)
    not_op(seq, *args)

def or_op (seq, *args):
    add_op(seq, *args)

def and_op (seq, *args):
    multiply_op(seq, *args)
