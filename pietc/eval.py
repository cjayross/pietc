from functools import partial
from pietc.debug import debuginfo

class LambdaError (RuntimeError):
    pass

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

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__,
                               list(zip(self.keys(), self.values())))

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
        idx = self.lamda_seq.params.index(self)
        return self.lamda_seq.args[idx]

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.symbol)

    def __call__ (self, seq, args):
        idx = self.lamda_seq.param_offset[self]
        function = self.lamda_seq.args[idx]
        return function(seq, args)

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

    def peek_sexpr (self):
        if not self.sexpr:
            return None
        if not isinstance(self.sexpr, list):
            return get_atom(self.env, self.sexpr)
        procedure, *args = self.sexpr
        if isinstance(procedure, str) and procedure in LOOKUPPROC \
           and procedure != 'define':
            return LOOKUPPROC[procedure](self.env, args)
        return self

    def evaluate (self):
        return evaluate(self.sexpr, self.env, self)

    def __call__ (self, seq, args):
        function = self.evaluate()
        debuginfo('{}({})', function, args, prefix='sequence call')
        return function(seq, args)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.sexpr)

class LambdaSequence (Sequence):
    """
    Represent a Sequence that manages a set of arguments to be
    defined within a local scope.
    """
    def __init__ (self, lamda, args):
        self.lamda = lamda
        self.args = args
        self.params = tuple(map(partial(Parameter, lamda_seq=self),
                                self.lamda.params))
        self.local_env = Environment(dict(zip(self.lamda.params, self.params)),
                                     parent_env=self.lamda.env)
        self.param_offset = dict(map(reversed, enumerate(self.params)))
        # a negative offset implies that the args have not yet been pushed.
        self.stack_offset = -len(self.params)
        super().__init__(self.lamda.sexpr, self.local_env)

    def param_depth (self, param):
        return self.stack_offset + self.param_offset[param]

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.sexpr,
                                   list(zip(self.lamda.params, self.args)))

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
        debuginfo('{}({}, {})', self.__class__.__name__,
                  self.sexpr, list(zip(self.params, args)),
                  prefix='lambda call')
        return LambdaSequence(self, args)

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.sexpr, self.params)

def get_atom (env, atom):
    if isinstance(atom, str):
        return env.lookup(atom)
    return atom

def procedure_call (env, args, proc, arg_count=None):
    "Generic function for invoking a procedure."
    if arg_count and len(args) != arg_count:
        raise RuntimeError('{}: invalid number of arguments'
                           .format(proc.__name__))
    return proc(env, *args)

def quote_proc (env, *args):
    "Return the first argument without evaluating it."
    return args[0]

def define_proc (env, *args):
    "Bind a symbol to an s-expression."
    sym, sexpr = args
    env.bind(sym, Sequence(sexpr, env).peek_sexpr())

def lambda_proc (env, *args):
    "Store an s-expression as a Lambda."
    params, sexpr = args
    return Lambda(params, sexpr, env)

LOOKUPPROC = {
    'define' : partial(procedure_call, proc=define_proc, arg_count=2),
    'quote' : partial(procedure_call, proc=quote_proc, arg_count=1),
    'lambda' : partial(procedure_call, proc=lambda_proc, arg_count=2),
}

def evaluate (sexpr, env, seq):
    "Recursive function for evaluating an s-expression within a given scope."
    debuginfo('{}', sexpr, prefix='evaluating')
    if not isinstance(sexpr, list):
        return get_atom(env, sexpr)
    # procedures are functions that manipulate program flow and the environment.
    procedure, *args = sexpr
    if isinstance(procedure, str) and procedure in LOOKUPPROC:
        return LOOKUPPROC[procedure](env, args)
    # operators are functions that manipulate the sequence and calls piet commands.
    operator, *operand = map(partial(evaluate, env=env, seq=seq), tuple(sexpr))
    debuginfo('{}({})', operator, operand, prefix='executing')
    return operator(seq, operand)
