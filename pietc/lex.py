from ply import lex
from collections import deque

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
        'LEADINGWS',
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

# t_ignore = " \t"

def t_error (tok):
    print("Illegal character encountered: '%s'" % tok.value[0])
    tok.lexer.skip(1)

def t_ignore_COMMENT (tok):
    r"(?:\#.*\n)+\s*"
    tok.lexer.lineno += tok.value.count('\n')
    tok.value = len(tok.value) - tok.value.rfind('\n') - 1
    tok.type = 'NEWLINE'
    return tok

def t_ignore_WORDSEPERATION (tok):
    r"(?<=[^ \t\n])[ \t]+"
    pass

def t_LEADINGWS (tok):
    r"(?<=\n)[ \t]+"
    tok.value = len(tok.value)
    return tok

def t_NEWLINE (tok):
    r"\n(?:\s*(?:\#.*)?\n)*"
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
    def __init__ (self, lexer, verbose):
        self.lexer = lexer
        self.token_stream = None
        self.verbose = verbose

    def mark_tokens (self, tokens):
        NO_INDENT = 0
        MAY_INDENT = 1
        MUST_INDENT = 2
        indent = NO_INDENT
        for tok in tokens:
            if tok.type == ':':
                indent = MAY_INDENT
                tok.must_indent = False
            elif tok.type == 'NEWLINE':
                if indent == MAY_INDENT:
                    indent = MUST_INDENT
                tok.must_indent = False
            elif tok.type == 'LEADINGWS':
                tok.must_indent = False
            else:
                if indent == MUST_INDENT:
                    tok.must_indent = True
                else:
                    tok.must_indent = False
                indent = NO_INDENT
            yield tok

    def track_indentation (self, tokens):
        ws_lineno = 1
        ws_lexpos = 0
        depth = 0
        depth_stack = [0]
        for tok in tokens:
            if tok.type == 'LEADINGWS':
                depth = tok.value
                ws_lineno = tok.lineno
                ws_lexpos = tok.lexpos
                continue
            elif tok.type == 'NEWLINE':
                depth = 0
                ws_lineno = tok.lineno
                ws_lexpos = tok.lexpos
                yield tok
                continue

            if tok.must_indent:
                if not (depth > depth_stack[-1]):
                    raise IndentationError('expected indentation')
                depth_stack.append(depth)
                yield IndentToken('INDENT', None, ws_lineno, ws_lexpos)
            else:
                if depth == depth_stack[-1]:
                    pass
                elif depth > depth_stack[-1]:
                    raise IndentationError('unexpected indentation')
                else:
                    try:
                        level = depth_stack.index(depth)
                    except ValueError:
                        raise IndentationError('indentation mismatch')
                    for _ in range(level+1, len(depth_stack)):
                        yield IndentToken('DEDENT', None, ws_lineno, ws_lexpos)
                        depth_stack.pop()
            yield tok
        if len(depth_stack) > 1:
            for _ in range(1, len(depth_stack)):
                yield IndentToken('DEDENT', None, ws_lineno, ws_lexpos)

    def token_filter (self):
        tokens = self.mark_tokens(iter(self.lexer.token, None))
        for tok in self.track_indentation(tokens):
            yield tok

    def input (self, s):
        self.lexer.input(s)
        self.token_stream = self.token_filter()

    def token (self):
        try:
            tok = self.token_stream.send(None)
            if self.verbose:
                print(tok)
            return tok
        except StopIteration:
            return None

    def run (self):
        while True:
            tok = self.token()
            if not tok: break

    # def token (self):
    #     if self.token_queue:
    #         return self.token_queue.popleft()
    #     if self.eof:
    #         return None
    #     tok = self.lexer.token()
    #     lineno = self.lexer.lineno
    #     lexpos = self.lexer.lexpos
    #     if not tok:
    #         self.eof = True
    #         if len(self.depth_stack) > 1:
    #             tok = IndentToken('DEDENT', None, lineno, lexpos)
    #             for _ in range(len(self.depth_stack)-1):
    #                 new = IndentToken('DEDENT', None, lineno, lexpos)
    #                 self.token_queue.append(new)
    #             self.depth_stack = [0]
    #     elif tok.type == 'NEWLINE':
    #         if tok.value > self.depth_stack[-1]:
    #             self.depth_stack.append(tok.value)
    #             new = IndentToken('INDENT', None, lineno, lexpos)
    #             self.token_queue.append(new)
    #         else:
    #             while tok.value < self.depth_stack[-1]:
    #                 self.depth_stack.pop()
    #                 new = IndentToken('DEDENT', None, lineno, lexpos)
    #                 self.token_queue.append(new)
    #             if tok.value != self.depth_stack[-1]:
    #                 raise Exception("Indentation mismatch")
    #     return tok

if __name__ == '__main__':
    lexer = IndentLexer(lex.lex(), True)
    lexer.input(open('sample.pc').read())
    lexer.run()
