from ply import lex
from collections import namedtuple, deque

class IndentToken (lex.LexToken):
    def __init__ (self, _type, _value, _lineno, _lexpos):
        self.type = _type
        self.value = _value
        self.lineno = _lineno
        self.lexpos = _lexpos

tokens = (
        'NAME',
        'STRING',
        'INTEGER',
        'INDENT',
        'DEDENT',
        'NEWLINE',
        'IF',
        'ELIF',
        'ELSE',
        'WHILE',
        'PRINT',
        'SCAN',
        'CHAR',
        'INT',
        'BREAK',
        'CONTINUE',
        'EQUALS',
        'NOTEQUALS',
        'GREATEROREQUAL',
        'LESSEROREQUAL',
        'TRUE',
        'FALSE',
        )

literals = (
        '=',
        '+',
        '-',
        '*',
        '/',
        '%',
        ';',
        ':',
        '<',
        '>',
        '!',
        '(',
        ')',
        '#',
        "'",
        '"',
        ' ',
        )

reserved = {
        'if' : 'IF',
        'elif' : 'ELIF',
        'else' : 'ELSE',
        'while' : 'WHILE',
        'print' : 'PRINT',
        'scan' : 'SCAN',
        'char' : 'CHAR',
        'int' : 'INT',
        'break' : 'BREAK',
        'continue' : 'CONTINUE',
        'True' : 'TRUE',
        'False' : 'FALSE',
        }

t_ignore = " \t"

def t_error (tok):
    print("Illegal character encountered: '%s'" % tok.value[0])
    tok.lexer.skip(1)

def t_ignore_COMMENT (tok):
    r"\#.*\n"
    tok.lexer.lineno += 1
    tok.value = len(tok.value) - tok.value.rfind('\n') - 1
    tok.type = 'NEWLINE'
    return tok

def t_NEWLINE (tok):
    r"\n(?:\s*(?:[#].*)?\n)*\s*"
    tok.lexer.lineno += tok.value.count('\n')
    tok.value = len(tok.value) - tok.value.rfind('\n') - 1
    return tok

def t_NAME (tok):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    tok.type = reserved.get(tok.value, 'NAME')
    return tok

def t_STRING (tok):
    r"(\".*\"|\'.*\')"
    tok.value = tok.value[1:-1]
    return tok

def t_INTEGER (tok):
    r"-?[0-9]+"
    return tok

def t_EQUALS (tok):
    r"=="
    return tok

def t_NOTEQUALS (tok):
    r"!="
    return tok

def t_GREATEROREQUAL (tok):
    r">="
    return tok

def t_LESSEROREQUAL (tok):
    r"<="
    return tok

class IndentLexer (object):
    def __init__ (self, lexer):
        self.lexer = lexer
        self.depth_stack = [0]
        self.token_queue = deque()
        self.eof = False

    def token (self):
        if self.token_queue:
            return self.token_queue.popleft()
        if self.eof:
            return None
        tok = self.lexer.token()
        if not tok:
            self.eof = True
            if len(self.depth_stack) > 1:
                tok = IndentToken('DEDENT', None)
                for _ in range(len(self.depth_stack)-1):
                    new = IndentToken(
                            'DEDENT', None,
                            self.lexer.lineno, self.lexer.lexpos)
                    self.token_queue.append(new)
                self.depth_stack = [0]
        elif tok.type == 'NEWLINE':
            if tok.value > self.depth_stack[-1]:
                self.depth_stack.append(tok.value)
                new = IndentToken(
                        'INDENT', None,
                        self.lexer.lineno, self.lexer.lexpos)
                self.token_queue.append(new)
            else:
                while tok.value < self.depth_stack[-1]:
                    self.depth_stack.pop()
                    new = IndentToken(
                            'DEDENT', None,
                            self.lexer.lineno, self.lexer.lexpos)
                    self.token_queue.append(new)
                if tok.value != self.depth_stack[-1]:
                    raise Exception("Indentation mismatch")
        return tok

    def run (self, fname):
        self.lexer.input(open(fname).read())
        while True:
            tok = self.token()
            if not tok: break
            print(tok)

lexer = IndentLexer(lex.lex())
lexer.run('sample.pc')
