from pietc import DEFAULT_ENV
from pietc.parse import parser
from pietc.eval import Environment, Sequence, evaluate

with open('test.pl') as File:
    code = parser.parse(File.read())
    global_env = Environment(DEFAULT_ENV)
    program = []
    for sexpr in code:
        res = evaluate(sexpr, global_env, program)
        if issubclass(res.__class__, Sequence):
            program.append(res.expand())
    print(program)
