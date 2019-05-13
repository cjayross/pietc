from functools import partial

class Environment (dict):
    def __init__ (self, base_dict={}, parent_env=None):
        self.update(base_dict)
        self.parent = parent_env

    def reference_environment (self, key):
        try:
            if key in self:
                return self
            else:
                return self.parent.reference_environment(key)
        except (KeyError, AttributeError):
            raise KeyError('undefined symbol: %s' % str(key))

    def lookup (self, key):
        return self.reference_environment(key)[key]

    def bind (self, key, value):
        self.update({key : value})

class Sequence (list):
    def __init__ (self, sexpr, env):
        self.sexpr = sexpr
        self.env = env
        self.eval_args = (self.sexpr, self.env, self)

    def __call__ (self, seq, args):
        function = evaluate(*self.eval_args)
        return function(seq, args)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.sexpr)

    def __str__ (self):
        return str(self.__repr__())

class LambdaSequence (Sequence):
    def __init__ (self, lamda, parent_seq, args):
        self.lamda = lamda
        self.parent_seq = parent_seq
        self.args = args
        self.params = tuple(map(partial(Parameter, lamda_seq=self),
                                self.lamda.params))
        self.local_env = Environment(dict(zip(self.lamda.params, self.params)),
                                     parent_env=self.lamda.env)
        self.param_offset = dict(map(reversed, enumerate(self.params)))
        self.stack_offset = 0
        super().__init__(self.lamda.sexpr, self.local_env)

    def param_depth (self, param):
        return self.stack_offset + self.param_offset[param]

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.sexpr,
                                   list(zip(self.lamda.params, self.args)))

class Parameter (object):
    def __init__ (self, symbol, lamda_seq):
        self.lamda_seq = lamda_seq
        self.symbol = symbol

    @property
    def param_depth (self):
        return self.lamda_seq.param_depth(self)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.symbol)

    def __call__ (self, seq, args):
        idx = self.lamda_seq.param_offset[self]
        function = self.lamda_seq.args[idx]
        return function(seq, args)

class Lambda (object):
    def __init__ (self, params, sexpr, env):
        self.params = params
        self.sexpr = sexpr
        self.env = env

    def __call__ (self, seq, args):
        if len(args) != len(self.params):
            raise RuntimeError('lambda: invalid number of parameters')
        # print('lambda call: {}({}, {})'.format(self.__class__.__name__,
        #                                        self.sexpr, args))
        return LambdaSequence(self, seq, args)

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.params, self.sexpr)

    def __str__ (self):
        return str(self.__repr__())

def procedure_call (proc, args, env, arg_count=None):
    if arg_count and len(args) != arg_count:
        raise RuntimeError('%s: invalid number of arguments' % str(proc))
    return proc(env, *args)

def quote_proc (env, *args):
    return args[0]

def if_proc (env, *args):
    return None

def define_proc (env, *args):
    sym, sexpr = args
    env.bind(sym, Sequence(sexpr, env))

def lambda_proc (env, *args):
    params, sexpr = args
    return Lambda(params, sexpr, env)

def evaluate (sexpr, env, seq):
    # print('evaluating: {}'.format(sexpr))
    if not isinstance(sexpr, list):
        if isinstance(sexpr, str):
            return env.lookup(sexpr)
        else:
            return sexpr
    # procedures are functions that manipulate program flow and the environment.
    procedure, *args = sexpr
    if isinstance(procedure, str):
        if procedure == 'quote':
            return procedure_call(quote_proc, args, env, arg_count=1)
        elif procedure == 'if':
            return procedure_call(if_proc, args, env, arg_count=3)
        elif procedure == 'define':
            return procedure_call(define_proc, args, env, arg_count=2)
        elif procedure == 'lambda':
            return procedure_call(lambda_proc, args, env, arg_count=2)
    # operators are functions that manipulate a sequence and call piet commands.
    operator, *operand = map(partial(evaluate, env=env, seq=seq), tuple(sexpr))
    # print('executing: {}({})'.format(operator, operand))
    return operator(seq, operand)
