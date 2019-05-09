import math
import operator as op
from ply.yacc import yacc
from pietc.lex import tokens, lexer

def p_sexpression (p):
    '''sexpression : LPAREN sexpression_list RPAREN | atom'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = list(p[1])

def p_sexpression_list (p):
    '''sexpression_list : sexpression_list sexpression | sexpression'''
    if len(p) > 2:
        p[0] = p[1].append(p[2])
    else:
        p[0] = [p[1],]

def p_atom (p):
    '''atom : SYMBOL | INTEGER | BOOL | FLOAT | CHAR | SYMBOL | NIL'''
    p[0] = p[1]
