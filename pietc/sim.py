from functools import wraps
from collections import deque
from pietc import DEFAULT_ENV
from pietc.parse import parser
from pietc.eval import evaluate, Environment, Sequence, LambdaSequence, LambdaError
from pietc.piet import Command, Push, Parameter, active_lambdas, broadcast_stack_change

stack = deque()
stack_offset_buffer = deque()

def printout (func):
    def wraps (*args, **kwargs):
        res = func(*args, **kwargs)
        print('{}: {}'.format(func.__name__, list(stack)))
        return res
    return wraps

def save_stack_offsets ():
    for lamda in active_lambdas:
        stack_offset_buffer.append(lamda.stack_offset)

def restore_stack_offsets ():
    for lamda in active_lambdas:
        lamda.stack_offset = stack_offset_buffer.popleft()

def jump_sim (seq):
    if isinstance(seq, LambdaSequence):
        active_lambdas.append(seq)
        if seq.args:
            push_sim(*seq.args)
        if seq.stack_offset < 0:
            raise LambdaError('insufficient arguments for lambda')
    print('jump: {}'.format(seq))
    save_stack_offsets()
    res = evaluate(*seq.eval_args)
    restore_stack_offsets()
    new = list(seq) if res is None else [*list(seq), res]
    simulate(new)
    print('return: {}'.format(seq))
    if isinstance(seq, LambdaSequence):
        active_lambdas.pop()
        stack_size = len(seq.params)
        for _ in range(stack_size):
            if seq.stack_offset != 0:
                push_sim(seq.stack_offset, -1)
                roll_sim()
            pop_sim()

@printout
def pop_sim ():
    stack.pop()
    broadcast_stack_change(-1)

@printout
def push_sim (*args):
    for arg in args:
        if isinstance(arg, (int, float)):
            stack.append(arg)
            broadcast_stack_change(1)
        elif isinstance(arg, Sequence):
            jump_sim(arg)
        elif isinstance(arg, Parameter):
            depth = arg.param_depth
            if depth != 0:
                push_sim(depth, -1)
                roll_sim()
            duplicate_sim()
            if depth != 0:
                push_sim(depth + 1, 1)
                roll_sim()
        else:
            push_sim(0)

@printout
def roll_sim ():
    global stack
    count = stack.pop()
    depth = stack.pop()
    split = len(stack) - depth - 1
    front = list(stack)[:split]
    back = deque(stack, maxlen=depth+1)
    back.rotate(count)
    stack = deque(front + list(back))
    broadcast_stack_change(-2)

@printout
def duplicate_sim ():
    stack.append(stack[-1])
    broadcast_stack_change(1)

@printout
def add_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y + x)
    broadcast_stack_change(-1)

@printout
def subtract_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y - x)
    broadcast_stack_change(-1)

@printout
def multiply_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y * x)
    broadcast_stack_change(-1)

@printout
def divide_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y // x)
    broadcast_stack_change(-1)

@printout
def modulo_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y % x)
    broadcast_stack_change(-1)

@printout
def greater_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(int(y > x))
    broadcast_stack_change(-1)

@printout
def not_sim ():
    x = stack.pop()
    stack.append(int(not x))

def simulate (seq):
    for stmt in seq:
        if isinstance(stmt, Push):
            if stmt.args:
                push_sim(*stmt.args)
        elif isinstance(stmt, Command):
            if stmt.name == 'roll':
                roll_sim()
            elif stmt.name == 'duplicate':
                duplicate_sim()
            elif stmt.name == 'add':
                add_sim()
            elif stmt.name == 'subtract':
                subtract_sim()
            elif stmt.name == 'multiply':
                multiply_sim()
            elif stmt.name == 'divide':
                divide_sim()
            elif stmt.name == 'mod':
                modulo_sim()
            elif stmt.name == 'greater':
                greater_sim()
            elif stmt.name == 'not':
                not_sim()
        elif isinstance(stmt, Sequence):
            jump_sim(stmt)

if __name__ == '__main__':
    with open('test.pl') as File:
        code = parser.parse(File.read())
        global_env = Environment(DEFAULT_ENV)
        program = []
        for sexpr in code:
            res = evaluate(sexpr, global_env, program)
            if issubclass(res.__class__, Sequence):
                program.append(res)
        simulate(program)
