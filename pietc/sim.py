from functools import wraps
from collections import deque
from pietc import Program
from pietc.parse import parser
from pietc.eval import Environment, Sequence, MacroSequence, \
    LambdaSequence, Lambda, Parameter, Conditional, ConditionalLambda, \
    Atom, LambdaError, evaluate
from pietc.piet import Command, Push
from pietc.debug import debuginfo

stack = deque()

def printout (func):
    def wraps (*args, **kwargs):
        res = func(*args, **kwargs)
        print('{}: {}'.format(func.__name__, list(stack)))
        return res
    return wraps

def get_condition (cond):
    while isinstance(cond, Conditional):
        res = cond.choice if cond.has_choice else condition_sim(cond)
        if isinstance(cond, MacroSequence):
            break
        print('jump: {} -> {}'.format(cond, res))
        cond = res
    return cond

def jump_sim (seq):
    seq.expand()
    if len(seq) != 0:
        if isinstance(seq, MacroSequence):
            print('jump: {}'.format(seq))
        simulate(list(seq))
        if isinstance(seq, MacroSequence):
            print('return: {}'.format(seq))

@printout
def condition_sim (cond):
    simulate(expand(cond.test_seq))
    cond.choice = stack.pop()
    return cond if isinstance(cond, ConditionalLambda) else cond.choice

@printout
def pop_sim ():
    res = stack.pop()
    return res

def push_sim (*args):
    for arg in args:
        if isinstance(arg, Conditional):
            arg = get_condition(arg)
        if isinstance(arg, int):
            stack.append(arg)
            print('push_sim: {}'.format(list(stack)))
        elif isinstance(arg, Sequence):
            jump_sim(arg)
        elif isinstance(arg, Parameter):
            # depth = param depth + stack depth
            depth = arg.param_depth
            if depth != 0:
                push_sim(depth, -1)
                roll_sim()
                # param depth -= 1, stack depth += 1
            duplicate_sim()
            # stack depth += 1
            if depth != 0:
                push_sim(depth + 1, 1)
                roll_sim()
                # param depth += 1, stack depth -= 1

@printout
def roll_sim ():
    global stack
    count = stack.pop()
    depth = stack.pop()
    split = len(stack) - depth - 1
    if split < 0:
        raise RuntimeWarning('call to roll ignored')
    front = list(stack)[:split]
    back = deque(stack, maxlen=depth+1)
    back.rotate(count)
    stack = deque(front + list(back))

@printout
def duplicate_sim ():
    stack.append(stack[-1])

@printout
def add_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y + x)

@printout
def subtract_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y - x)

@printout
def multiply_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y * x)

@printout
def divide_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y // x)

@printout
def modulo_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(y % x)

@printout
def greater_sim ():
    x, y = stack.pop(), stack.pop()
    stack.append(int(y > x))

@printout
def not_sim ():
    x = stack.pop()
    stack.append(int(not x))

LOOKUPSIM = {
    'pop' : pop_sim,
    'roll' : roll_sim,
    'duplicate' : duplicate_sim,
    'add' : add_sim,
    'subtract' : subtract_sim,
    'multiply' : multiply_sim,
    'divide' : divide_sim,
    'mod' : modulo_sim,
    'greater' : greater_sim,
    'not' : not_sim,
}

def simulate (seq):
    debuginfo('{}', seq, prefix='simulating')
    for stmt in seq:
        if isinstance(stmt, Conditional):
            stmt = get_condition(stmt)
        if isinstance(stmt, Push):
            push_sim(stmt.value)
        elif isinstance(stmt, Command):
            LOOKUPSIM[stmt.name]()
        elif isinstance(stmt, Sequence):
            jump_sim(stmt)
        else:
            push_sim(stmt)

if __name__ == '__main__':
    with open('test.pl') as File:
        code = parser.parse(File.read())
    program = Program()
    global_env = program.env
    for sexpr in code:
        evaluate(sexpr, global_env, program)
        # res = evaluate(sexpr, global_env, program)
        # if isinstance(res, (Sequence, Conditional)):
        #     program.append(res)
    simulate(program)
