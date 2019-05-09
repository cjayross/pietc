from ply.lex import lex

tokens = (
    'LPAREN',
    'RPAREN',
    'SYMBOL',
    'INTEGER',
    'BOOL',
    'FLOAT',
    'CHAR',
    'STRING',
    'NIL',
    'QUOTE',
    'UNQUOTE',
)

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SYMBOL = r'[a-zA-Z!$%&*+./:<=>?"@^_~-][0-9a-zA-Z!$%&*+./:<=>?"@^_~-]*'
t_QUOTE = r"'"
t_UNQUOTE = r','

def t_STRING (tok):
    r'"(\\"|\\n|[a-zA-Z*+/!?=<>. -])*"'
    tok.value = tok.value[1:-1]
    tok.value = tok.value.replace('\\"', '"')
    tok.value = tok.value.replace('\\n', '\n')
    return tok

def t_FLOAT (tok):
    r'-?([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)'
    tok.value = float(tok.value)
    return tok

def t_INTEGER (tok):
    r'-?[0-9]+'
    tok.value = int(tok.value)
    return tok

def t_BOOL (tok):
    r'\#t|\#f'
    tok.value = True if tok.value == '#t' else False
    return tok

def t_CHAR (tok):
    r'\#\\(space|newline|.)'
    tok.value = tok.value[2:]
    if len(tok.value) > 1:
        tok.value = ' ' if tok.value == 'space' else '\n'
    return tok

def t_NIL (tok):
    r'nil'
    return None

t_ignore_COMMENT = r';[^\n]*'
t_ignore = ' \t\n'

lexer = lex()
