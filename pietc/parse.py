import math
import operator as op
from ply.yacc import yacc
from pietc.lex import tokens, lexer

def p_sexpression_list (p):
    '''sexpression_list : sexpression_list sexpression
                        | sexpression'''
    if len(p) == 3:
        p[0] = p[1] + [p[2],]
    else:
        p[0] = [p[1],]

def p_sexpression (p):
    '''sexpression : LPAREN sexpression_list RPAREN
                   | atom'''
    if len(p) == 4:
        # type : list
        p[0] = p[2]
    else:
        # type : (str, int, float, None)
        p[0] = p[1]

def p_atom (p):
    '''atom : SYMBOL
            | INTEGER
            | BOOL
            | FLOAT
            | STRING
            | CHAR
            | NIL'''
    p[0] = p[1]

parser = yacc()

if __name__ == '__main__':
    with open('test.pl') as File:
        res = parser.parse(File.read())
        print(res)
