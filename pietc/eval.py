from functools import partial

class Environment (dict):
    """
    Represent the program's environment within a given scope.

    This is a dictionary subclass to manage what symbols have
    a corresponding definition.
    The environment within a scope can be extended when a
    procedure invokes a call to `bind` by which a symbol
    (such as an argument to a lambda function) can be mapped
    to an object (such as a Parameter type) or value.
    """
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
    """
    Store an s-expression to be evaluated later.

    Sequences are used to provide a reference to code that may
    be referenced more than once. This means that Sequences are
    likely to become subprograms that can be jumped to during
    program execution.

    Furthermore, it is important to note that Sequences are a
    list subclass so that a sequence of `piet` commands can
    be stored to be drawn as a subprogram later.
    """
    def __init__ (self, sexpr, env):
        self.sexpr = sexpr
        # later, it should be considered whether it would be better
        # to store a deepcopy of the environment so that the scope
        # for this sequence remains static past this point.
        self.env = env
        self.eval_args = (self.sexpr, self.env, self)

    def expand (self):
        res = evaluate(*self.eval_args)
        return [*list(self), res] if res is not None else list(self)

    def __call__ (self, seq, args):
        function = evaluate(*self.eval_args)
        # print('sequence call: {}({})'.format(function, args))
        return function(seq, args)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.sexpr)

    def __str__ (self):
        return str(self.__repr__())

class LambdaSequence (Sequence):
    """
    Represent a Sequence that manages a set of arguments to be
    defined within a local scope.
    """
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

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.symbol)

    def __call__ (self, seq, args):
        idx = self.lamda_seq.param_offset[self]
        function = self.lamda_seq.args[idx]
        return function(seq, args)

class Lambda (object):
    """
    Define an s-expression that requires a local scope before
    it can evaluated.
    """
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
    "Generic function for invoking a procedure."
    if arg_count and len(args) != arg_count:
        raise RuntimeError('%s: invalid number of arguments' % str(proc))
    return proc(env, *args)

def quote_proc (env, *args):
    "Return the first argument without evaluating it."
    return args[0]

def define_proc (env, *args):
    "Bind a symbol to an s-expression."
    sym, sexpr = args
    env.bind(sym, Sequence(sexpr, env))

def if_proc (env, *args):
    "TODO: Store an s-expression that can be skipped."
    return None

def lambda_proc (env, *args):
    "Store an s-expression as a Lambda."
    params, sexpr = args
    return Lambda(params, sexpr, env)

def evaluate (sexpr, env, seq):
    "Recursive function for evaluating an s-expression within a given scope."
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
    # operators are functions that manipulate the sequence and calls piet commands.
    operator, *operand = map(partial(evaluate, env=env, seq=seq), tuple(sexpr))
    print('executing: {}({})'.format(operator, operand))
    return operator(seq, operand)
