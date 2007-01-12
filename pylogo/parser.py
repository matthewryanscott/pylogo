import structs

tokens = (
    'TO', 'END',
    'NAME',
    'COLON',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'GREATER_EQUAL', 'LESS_EQUAL', 'GREATER', 'LESS', 
    'NOT_EQUAL', 'EQUAL', 
    'NUMBER', 'QUOTE',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
    'NEWLINE',
    )

def t_TO(t):
    r'[tT][oO]'
    t.lineno = t.lexer.lineno
    return t

t_END = '[eE][nN][dD]'
t_NAME = r'[a-zA-Z_.][a-zA-Z_.0-9]*'
t_COLON = r':'
t_PLUS = r'[+]'
t_MINUS = r'-'
t_TIMES = r'[*]'
t_DIVIDE = r'/'
t_GREATER_EQUAL = r'>=|=>'
t_LESS_EQUAL = r'<=|=<'
t_GREATER = r'>'
t_LESS = r'<'
t_NOT_EQUAL = r'<>|!='
t_EQUAL = r'='
t_QUOTE = r'"'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_LBRACKET(t):
    r'\['
    t.lineno = t.lexer.lineno
    return t

t_RBRACKET = r'\]'

t_ignore = ' \t'

def t_NUMBER(t):
    r'[0-9]+(?:\.[0-9]*)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += t.value.count("\n")
    return t

def t_error(t):
    print "Illegal character %r at line %s" % (
        t.value[0], t.lexer.lineno)
    t.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

precedence = (
    ('nonassoc', 'GREATER_EQUAL', 'LESS_EQUAL', 'GREATER', 'LESS',
     'NOT_EQUAL', 'EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    #('right', 'UMINUS'),
    )

def p_program(t):
    """
    program : expression NEWLINE program
            | statement_to NEWLINE program
            | expression
            | statement_to
    """
    if len(t) == 4:
        t[0] = structs.sourcelist([t[1], t[3]],
                                  linenos=[(0, t.lineno(1)),
                                           (1, t.lineno(3)+1)])
    else:
        t[0] = structs.sourcelist([t[1]], lineno=t.lineno(1))

def p_statement_to(t):
    """statement_to : TO NAME to_args NEWLINE expression NEWLINE END"""
    t[0] = structs.ToExpression(t[1], t[2], t[4])

def p_to_args(t):
    """to_args : var_spec to_args
               | var_spec"""
    if len(t) == 3:
        # first form
        t[0] = [t[1]] + t[2]
    else:
        t[0] = [t[1]]

def p_var_spec(t):
    """var_spec : COLON NAME
                | QUOTE NAME
                | NAME"""
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = t[2]

def p_expression_mult(t):
    """
    expression : expression expression
    """
    t[0] = structs.sourcelist.join(t[1], t[2])

def p_expression_command(t):
    """
    expression : NAME expression
    """
    t[0] = structs.sourcelist.join([t[1]], t[2])

def p_expression_operator(t):
    """
    expression : expression operator expression
    """
    t[0] = structs.sourcelist(
        [structs.logoexpression([t[1], t[2], t[3]], paren=False)])

def p_expression_paren(t):
    """
    expression : LPAREN expression RPAREN
    """
    t[0] = structs.sourcelist([structs.logoexpression(t[1])])

def p_expression_list(t):
    """
    expression : LBRACKET expression RBRACKET
    """
    t[0] = structs.sourcelist(t[2], lineno=t.lineno(2))

def p_expression_identity(t):
    """
    expression : value
               | variable
    """
    t[0] = structs.sourcelist([t[1]])

def p_value(t):
    """value : string
             | NUMBER"""
    t[0] = t[1]

def p_string(t):
    """string : QUOTE NAME
              | QUOTE TO
              | QUOTE END"""
    t[0] = structs.logosymbol(t[2])

def p_variable(t):
    """variable : COLON NAME"""
    t[0] = structs.logovar(t[2])

def p_operator(t):
    """operator : PLUS
                | MINUS
                | TIMES
                | DIVIDE
                | GREATER_EQUAL
                | LESS_EQUAL
                | GREATER
                | LESS
                | NOT_EQUAL
                | EQUAL"""
    t[0] = structs.operator(t[1])

def p_error(t):
    if t:
        print "Syntax error at %r" % t.value
    else:
        print "Syntax error at unknown location"

import ply.yacc as yacc
parser = yacc.yacc(debug=True)
