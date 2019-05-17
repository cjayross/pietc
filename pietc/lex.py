from ply.lex import lex

tokens = (
    'LPAREN',
    'RPAREN',
    'SYMBOL',
    'INTEGER',
    'BOOL',
    'CHAR',
    'STRING',
    'NIL',
    'QUOTE',
)

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SYMBOL = r'[a-zA-Z!$%&*+./:<=>?"@^_~-][0-9a-zA-Z!$%&*+./:<=>?"@^_~-]*'
t_QUOTE = r"'"

def t_STRING (tok):
    r'"(\\"|\\n|[a-zA-Z0-9*+/!?=<>. -])*"'
    tok.value = tok.value[1:-1]
    tok.value = tok.value.replace('\\"', '"')
    tok.value = tok.value.replace('\\n', '\n')
    tok.value = ['quote', list(map(ord, tok.value))]
    return tok

def t_INTEGER (tok):
    r'-?[0-9]+'
    tok.value = int(tok.value)
    return tok

def t_BOOL (tok):
    r'\#t|\#f'
    tok.value = 1 if tok.value == '#t' else 0
    return tok

def t_CHAR (tok):
    r'\#\\(space|newline|.)'
    tok.value = tok.value[2:]
    if len(tok.value) > 1:
        tok.value = ord(' ') if tok.value == 'space' else ord('\n')
    return tok

def t_NIL (tok):
    r'nil'
    tok.value = 'nil'
    return tok

t_ignore_COMMENT = r';[^\n]*'
t_ignore = ' \t'

def t_error (tok):
    print('parse error: illegal character `%s`' % tok.value[0])
    tok.lexer.skip(1)

def t_newline (tok):
    r'\n+'
    tok.lexer.lineno += len(tok.value)

lexer = lex()
