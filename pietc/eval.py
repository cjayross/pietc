from functools import partial
from pietc.debug import debuginfo, debugcontext

class LambdaError (RuntimeError):
    pass

class Environment (dict):
    """
    Dictionary object representing the environment within a scope.

    Parameters
    ==========

    base_dict : dict
        Dictionary that maps string identifiers to values.
    parent_env : Environment
        The environment to defer to when a symbol is not matched.

    This is a dictionary subclass to manage what symbols have a corresponding
    definition. The environment within a scope can be extended when a procedure
    invokes a call to `bind` by which a symbol (such as an argument to a lambda
    function) can be mapped to an object (such as a Parameter type) or value.

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

class Sequence (list):
    """
    Store an s-expression to be evaluated later.

    A Sequence type represents an abstraction of a single s-expression, meaning
    that they store all the appropriate variables required by a call to
    `evaluate`.

    This provides the ability to store and identify s-expressions in the
    program without modifying the parent sequence belonging to it which is
    essential for handling sequences that depend on context, such as Lambdas
    (since the argument stack for Lambdas are buried during runtime, their
    depth depends on the execution of other sequences).

    Examples
    ========

    >>> from pietc import DEFAULT_ENV
    >>> from pietc.eval import Sequence
    >>> global_env = DEFAULT_ENV
    >>> sexpr = ['define', 'twice', ['lambda', ['x'], ['*', 2, 'x']]]
    >>> seq = Sequence(sexpr, global_env)

    Evaluate the Sequence. In this case, all that is done is a modification of
    the environment `global_env` which isn't representable in piet.

    >>> seq.expand()
    >>> list(seq)
    []
    >>> global_env.lookup('twice')
    Lambda(['x'], ['*', 2, 'x'])

    Evaluate a Sequence that produces piet commands.

    >>> sexpr = ['twice', 10]
    >>> seq = Sequence(sexpr, global_env)
    >>> seq.expand()
    LambdaSequence([('x', 10)], ['*', 2, 'x'])
    >>> res = _

    Since this expression is a call to a Lambda, the sequence pushes the
    arguments onto the stack then jumps to a LambdaSequence. Afterward, the
    values pushed as arguments are popped.

    >>> list(seq)
    [Push(10),
     LambdaSequence([('x', 10)], ['*', 2, 'x'])
     Push(1),
     Push(-1),
     Command(roll),
     Command(pop)]

    Once the LambdaSequence is reached, we can evaluate it similarly.

    >>> res.expand(); list(res)
    [Push(2),
     Push(1),
     Push(-1),
     Command(roll),
     Command(duplicate),
     Push(2),
     Push(1),
     Command(roll),
     Command(multiply)]

    """
    def __init__ (self, sexpr, env):
        self.sexpr = sexpr
        # later, it should be considered whether it would be better
        # to store a deepcopy of the environment so that the scope
        # for this sequence remains static past this point.
        self.env = env
        self.expanded = False
        self.eval_result = None

    def peek_sexpr (self):
        """Return a simplification of the Sequence if possible."""
        if not self.sexpr:
            return None
        if not isinstance(self.sexpr, list):
            return get_atom(self.env, self.sexpr)
        procedure, *args = self.sexpr
        if isinstance(procedure, str) and procedure in LOOKUPPROC \
           and procedure != 'define':
            return LOOKUPPROC[procedure](self.env, args)
        return self

    def expand(self, debug=True):
        """Expand the s-expression using `evaluate`."""
        if self.expanded:
            return self.eval_result
        with debugcontext(debug):
            res = evaluate(self.sexpr, self.env, self)
        self.expanded = True
        self.eval_result = res
        return self.eval_result

    def __call__ (self, seq, *args):
        function = self.expand()
        debuginfo('{}({})', function, args, prefix='sequence call')
        return function(seq, *args)

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.sexpr)

class MacroSequence (Sequence):
    """
    Represents a Sequence that may be referred to more than once.

    This is simply a separate marker to characterize a Sequence as one that is
    intended to be drawn as a subroutine in the final image. These Sequences
    are created whenever an s-expression is bound to an identifier or whenever
    a Lambda expression is evaluated.

    """
    pass

class LambdaSequence (MacroSequence):
    """
    Represent a Sequence that manages a set of arguments to be defined within a
    local scope.

    Note that all lambdas are defined as dedicated function calls, even if they
    are not bound to a symbol.

    """
    def __init__ (self, lamda, args):
        self.lamda = lamda
        self.args = args
        self.params = tuple(map(partial(Parameter, lamda_seq=self),
                                self.lamda.params))
        self.local_env = Environment(dict(zip(self.lamda.params, self.params)),
                                     parent_env=self.lamda.env)
        self.param_offset = dict(map(reversed,
                                     enumerate(reversed(self.params))))
        self.stack_offset = 0
        popable_args = [arg for arg in self.args if is_pushable(arg)]
        self.stack_size = len(popable_args)
        super().__init__(self.lamda.sexpr, self.local_env)

    def param_depth (self, param):
        return self.stack_offset + self.param_offset[param]

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   list(zip(self.lamda.params, self.args)),
                                   self.sexpr)

class Lambda (object):
    """
    Define an s-expression that requires a local scope before it can evaluated.
    """
    def __init__ (self, params, sexpr, env):
        self.params = params
        self.sexpr = sexpr
        self.env = env

    def __call__ (self, seq, *args):
        # calling a lambda requires modifying the sequence.
        from pietc.piet import push_op, pop_op, roll_op
        if len(args) != len(self.params):
            raise RuntimeError('lambda: invalid number of parameters')
        debuginfo('{}({}, {})', self.__class__.__name__,
                  list(zip(self.params, args)), self.sexpr,
                  prefix='lambda call')
        lamda_seq = LambdaSequence(self, args)
        seq.append(lamda_seq)
        lamda_seq.expand(debug=False)
        if lamda_seq.stack_offset != 0:
            for _ in range(lamda_seq.stack_size):
                push_op(seq, 1, -1)
                roll_op(seq)
                pop_op(seq)
        return lamda_seq

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.params, self.sexpr)

class Parameter (object):
    """
    Define a lambda argument so that it can be identified across separate
    lambda calls.

    Note that the parameter's value is not stored since identifying this
    parameter's location in the stack is sufficient.

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
        val = self.lamda_seq.args[idx]
        if isinstance(val, Parameter):
            val = val.value
        return val

    def __repr__ (self):
        return '{}({})'.format(self.__class__.__name__, self.symbol)

    def __call__ (self, seq, args):
        idx = self.lamda_seq.param_offset[self]
        function = self.lamda_seq.args[idx]
        return function(seq, args)

class Conditional (object):
    """
    Represent an abstracted choice between two s-expressions.

    The handling of conditional expressions is done manually since conditionals
    are not allowed to be evaluated until simulated or drawn.

    """
    def __init__ (self, if_sexpr, else_sexpr, env):
        self.if_sexpr = if_sexpr
        self.else_sexpr = else_sexpr
        self.seq = None
        self.env = env

    @property
    def has_choice (self):
        return self.seq is not None

    @property
    def choice (self):
        return self.seq

    @choice.setter
    def choice (self, value):
        sexpr = self.if_sexpr if value else self.else_sexpr
        self.seq = Sequence(sexpr, self.env)

    def __call__ (self, seq, *args):
        from pietc.piet import push_op, pop_op, roll_op
        debuginfo('{}({})', self, args, prefix='conditional call')
        if not self.has_choice:
            cond_lamda = ConditionalLambda(self, args)
            popable_args = [arg for arg in args if is_pushable(arg)]
            seq.append(cond_lamda)
            for _ in range(len(popable_args)):
                push_op(seq, 1, -1)
                roll_op(seq)
                pop_op(seq)
            return cond_lamda
        function = self.seq.expand()
        return function(seq, args)

    def __repr__ (self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.if_sexpr, self.else_sexpr)

class ConditionalLambda (Conditional, MacroSequence):
    """Represent a Conditional with stored arguments."""
    def __init__ (self, conditional, args):
        print(args)
        self.conditional = conditional
        self.args = list(args)

    @property
    def choice (self):
        return self.conditional.choice(self, *self.args)

    @choice.setter
    def choice (self, value):
        self.conditional.choice = value

    def __getattr__ (self, attr):
        if hasattr(self.conditional, attr):
            return getattr(self.conditional, attr)
        return MacroSequence.__getattribute__(self, attr)

    def __repr__ (self):
        return '{}([{}, {}], {})'.format(self.__class__.__name__,
                                         self.conditional.if_sexpr,
                                         self.conditional.else_sexpr,
                                         self.args)

Atom = (int, Parameter, type(None))

def is_pushable (atom):
    if isinstance(atom, Parameter):
        atom = atom.value
    if isinstance(atom, Sequence):
        atom.expand(debug=False)
        return True if atom else False
    if not isinstance(atom, Atom):
        return False
    return True

def get_atom (env, atom):
    if isinstance(atom, str):
        return env.lookup(atom)
    return atom

def procedure_call (env, args, proc, arg_count=None):
    """Generic function for invoking a procedure."""
    if arg_count and len(args) != arg_count:
        raise RuntimeError('{}: invalid number of arguments'
                           .format(proc.__name__))
    return proc(env, *args)

def quote_proc (env, *args):
    """Return the first argument without evaluating it."""
    return args[0]

def define_proc (env, *args):
    """Bind a symbol to an s-expression."""
    sym, sexpr = args
    env.bind(sym, MacroSequence(sexpr, env).peek_sexpr())

def lambda_proc (env, *args):
    """Store an s-expression as a Lambda."""
    params, sexpr = args
    return Lambda(params, sexpr, env)

LOOKUPPROC = {
    'define' : partial(procedure_call, proc=define_proc, arg_count=2),
    'quote' : partial(procedure_call, proc=quote_proc, arg_count=1),
    'lambda' : partial(procedure_call, proc=lambda_proc, arg_count=2),
}

def evaluate (sexpr, env, seq):
    """
    Recursive function for evaluating an s-expression within a given scope.

    Parameters
    ==========

    sexpr : str, list
        The s-expression to be evaluated.
    env : Environment
        The scope of the current execution environment. Contains a mapping
        between defined symbols and their values.
    seq : Sequence
        Sequence to store generated piet commands.

    Returns a Sequence or MacroSequence if the evaluation generates them. Such
    an occurance indicates that context is required to continue evaluation.
    Otherwise, this function returns `None`.

    """
    from pietc.piet import push_op
    debuginfo('{}', sexpr, prefix='evaluating')
    if not isinstance(sexpr, list):
        val = get_atom(env, sexpr)
        if is_pushable(val):
            push_op(seq, val)
        return val
    # procedures are functions that manipulate program flow and the environment.
    procedure, *args = sexpr
    if isinstance(procedure, str) and procedure in LOOKUPPROC:
        return LOOKUPPROC[procedure](env, args)
    elif procedure == 'if':
        return env.lookup(procedure)(seq, *args)
    # operators are functions that manipulate the sequence.
    operator, *operand = map(partial(evaluate, env=env, seq=seq), sexpr)
    debuginfo('{}({})', operator, operand, prefix='executing')
    return operator(seq, *operand)
