from ply import yacc
from pietc.lex import tokens

precedence = (
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        )

def p_file_inputs (p):
    '''file_inputs : file_input
                   | file_input file_inputs
       file_input  : stmt
                   | NEWLINE'''
    pass

def p_stmt (p):
    '''stmt : simple_stmt
            | compound_stmt'''
    pass

def p_simple_stmt (p):
    '''simple_stmt : atom_chain_stmt NEWLINE'''
    pass

def p_compound_stmt (p):
    '''compound_stmt : if_stmt
                     | while_stmt'''
    pass

def p_atom_chain_stmt (p):
    '''atom_chain_stmt : atom_stmt
                       | atom_stmt ";"
                       | atom_stmt ";" atom_chain_stmt'''
    pass

def p_atom_stmt (p):
    '''atom_stmt : expr_stmt
                 | print_stmt
                 | scan_stmt
                 | flow_stmt'''
    pass

def p_expr_stmt (p):
    '''expr_stmt : assign_expr
                 | value_expr'''
    pass

def p_print_stmt (p):
    '''print_stmt : PRINT CHAR NAME
                  | PRINT CHAR INTEGER
                  | PRINT CHAR STRING
                  | PRINT INT NAME
                  | PRINT INT INTEGER
                  | PRINT INT STRING'''
    pass

def p_scan_stmt (p):
    '''scan_stmt : SCAN CHAR NAME
                 | SCAN INT NAME'''
    pass

def p_flow_stmt (p):
    '''flow_stmt : BREAK
                 | CONTINUE'''
    pass

def p_if_stmt (p):
    '''if_stmt : IF value_expr ":" block
               | IF value_expr ":" block ELSE ":" block
               | IF value_expr ":" block elif_chain_stmt
               | IF value_expr ":" block elif_chain_stmt ELSE ":" block'''
    pass

def p_elif_chain_stmt (p):
    '''elif_chain_stmt : ELIF value_expr ":" block
                       | ELIF value_expr ":" block elif_chain_stmt'''
    pass

def p_while_stmt (p):
    '''while_stmt : WHILE value_expr ":" block'''
    pass

def p_block (p):
    '''block : simple_stmt
             | NEWLINE INDENT stmt_chain_stmt DEDENT'''
    pass

def p_stmt_chain_stmt (p):
    '''stmt_chain_stmt : stmt
                       | stmt stmt_chain_stmt'''
    pass

def p_assign_expr (p):
    '''assign_expr : NAME "=" value_expr'''
    pass

def p_value_expr (p):
    '''value_expr : atom_expr
                  | atom_expr compare_op value_expr'''
    pass

def p_compare_op (p):
    '''compare_op : "<"
                  | ">"
                  | LESSEROREQUAL
                  | GREATEROREQUAL
                  | EQUALS
                  | NOTEQUALS'''
    pass

def p_atom_expr (p):
    '''atom_expr : term
                 | term "+" atom_expr
                 | term "-" atom_expr'''

def p_term (p):
    '''term : factor
            | factor "*" term
            | factor "/" term
            | factor "%" term'''
    pass

def p_factor (p):
    '''factor : atom
              | "(" atom_expr ")"'''
    pass

def p_atom (p):
    '''atom : INTEGER
            | NAME
            | TRUE
            | FALSE'''
    pass

def p_error (p):
    raise Exception("Syntax error: %s" % p.value)

yacc.yacc()
yacc.parse(open('sample.pc').read())
