from ply import yacc
from pietc.lex import tokens

precedence = (
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        )

variables = {}
commands = []

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
    commands.append(["print_string", p[3]])

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
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]

def p_stmt_chain_stmt (p):
    '''stmt_chain_stmt : stmt
                       | stmt stmt_chain_stmt'''
    p[0] = p[1]

def p_assign_expr (p):
    '''assign_expr : NAME "=" value_expr'''
    p[0] = variables[p[1]] = p[3]
    commands.append(["push", p[3]])

def p_value_expr (p):
    '''value_expr : atom_expr
                  | atom_expr compare_op value_expr'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '<':
        p[0] = p[1] < p[3]
        commands.append(["push", p[1]])
        commands.append(["push", p[3]])
        commands.append(["greater", 0])
    elif p[2] == '>':
        p[0] = p[1] > p[3]
        commands.append(["push", p[1]])
        commands.append(["push", p[3]])
        commands.append(["less", 0])
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]
    elif p[2] == '==':
        p[0] = p[1] == p[3]
        commands.append(["push", p[1]])
        commands.append(["push", p[3]])
        commands.append(["equals", 0])
    else:
        p[0] = p[1] != p[3]

def p_compare_op (p):
    '''compare_op : "<"
                  | ">"
                  | LESSEROREQUAL
                  | GREATEROREQUAL
                  | EQUALS
                  | NOTEQUALS'''
    p[0] = p[1]

def p_atom_expr (p):
    '''atom_expr : term
                 | term "+" atom_expr
                 | term "-" atom_expr'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1] - p[3]

def p_term (p):
    '''term : factor
            | factor "*" term
            | factor "/" term
            | factor "%" term'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    else:
        p[0] = p[1] % p[3]

def p_factor (p):
    '''factor : atom
              | "(" atom_expr ")"'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_atom (p):
    '''atom : INTEGER
            | NAME
            | STRING
            | TRUE
            | FALSE'''
    if p[1] == 'True':
        p[0] = 1
    elif p[1] == 'False':
        p[0] = 0
    else:
        try:
            p[0] = int(p[1])
        except ValueError:
            p[0] = variables.get(p[1], None)

def p_error (p):
    raise Exception("Syntax error: %s" % p.value)

yacc.yacc()
yacc.parse(open('sample.pc').read())
