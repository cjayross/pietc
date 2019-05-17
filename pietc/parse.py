import math
import operator as op
from functools import partial
from ply.yacc import yacc
from pietc.lex import tokens, lexer

def p_sexpression_list (p):
    '''sexpression_list : sexpression_list sexpression
                        | sexpression
                        |'''
    if len(p) == 3:
        p[0] = p[1] + [p[2],]
    elif len(p) == 2:
        p[0] = [p[1],]
    else:
        p[0] = []

def p_sexpression (p):
    '''sexpression : QUOTE LPAREN sexpression_list RPAREN
                   | LPAREN sexpression_list RPAREN
                   | QUOTE atom
                   | atom'''
    if len(p) == 5:
        p[0] = ['quote', p[3]]
    elif len(p) == 4:
        p[0] = p[2]
    elif len(p) == 3:
        p[0] = ['quote', p[2]]
    else:
        p[0] = p[1]

def p_atom (p):
    '''atom : SYMBOL
            | INTEGER
            | BOOL
            | CHAR
            | STRING
            | NIL'''
    p[0] = p[1]

parser = yacc()
