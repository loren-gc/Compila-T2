# High level function that takes input tokens and turns it into a syntax tree.
# This is a natural place to use some kind of generator function.

from sly import Parser

class zigParser(Parser):

    tokens = zigLexer.tokens
    precedence = ('left', 'KEYWORD_or'), ('left', 'KEYWORD_and'), ('left', 'EQUALEQUAL', 'EXCLAMATIONMARKEQUAL'), ('left', 'LARROW', 'RARROW', 'LARROWEQUAL', 'RARROWEQUAL'), ('left', 'PLUS', 'MINUS'), ('left', 'ASTERISK', 'SLASH', 'PERCENT'), ('right', 'UMINUS', 'EXCLAMATIONMARK'), ('nonassoc', 'IFX'), ('nonassoc', 'KEYWORD_else')

    @_('stmtlist')
    def program(self, p):
        return ('program', p.stmtlist)

    @_('stmtlist stmt')
    def stmtlist(self, p):
        return p.stmtlist + [p.stmt]

    @_('')
    def stmtlist(self, p):
        return []

    @_('KEYWORD_var IDENTIFIER COLON type EQUAL expr SEMI')
    def stmt(self, p):
        return ('variable: ' + p.IDENTIFIER, 'type: ' + p.type, p.expr)

    @_('KEYWORD_var IDENTIFIER COLON type SEMI')
    def stmt(self, p):
        return ('variable: ' + p.IDENTIFIER, 'type: ' + p.type, None)

    @_('KEYWORD_var IDENTIFIER EQUAL expr SEMI')
    def stmt(self, p):
        return ('variable: ' + p.IDENTIFIER, None, p.expr)

    @_('KEYWORD_const IDENTIFIER COLON type EQUAL expr SEMI')
    def stmt(self, p):
        return ('const: ' + p.IDENTIFIER, 'type: ' + p.type, p.expr)

    @_('KEYWORD_const IDENTIFIER EQUAL expr SEMI')
    def stmt(self, p):
        return ('const: ' + p.IDENTIFIER, None, p.expr)

    @_('IDENTIFIER EQUAL expr SEMI')
    def stmt(self, p):
        return ('assignment', 'location: ' + p.IDENTIFIER, p.expr)

    @_('KEYWORD_if LPAREN expr RPAREN block %prec IFX')
    def stmt(self, p):
        return ('if', p.expr, p.block, None)

    @_('KEYWORD_if LPAREN expr RPAREN block KEYWORD_else stmt')
    def stmt(self, p):
        return ('if', p.expr, p.block, p.stmt)

    @_('KEYWORD_while LPAREN expr RPAREN block')
    def stmt(self, p):
        return ('while', p.expr, p.block)

    @_('KEYWORD_break SEMI')
    def stmt(self, p):
        return 'break'

    @_('KEYWORD_continue SEMI')
    def stmt(self, p):
        return 'continue'

    @_('expr SEMI')
    def stmt(self, p):
        return ('expression', p.expr)

    @_('block')
    def stmt(self, p):
        return p.block

    @_('LBRACE stmtlist RBRACE')
    def block(self, p):
        return ('block', p.stmtlist if p.stmtlist else None)

    @_('IDENTIFIER')
    def type(self, p):
        return p.IDENTIFIER

    @_('expr KEYWORD_or expr')
    def expr(self, p):
        return ('binary_op: or',  p.expr0, p.expr1)

    @_('expr KEYWORD_and expr')
    def expr(self, p):
        return ('binary_op: and', p.expr0, p.expr1)

    @_('expr EQUALEQUAL expr')
    def expr(self, p):
        return ('binary_op: ==',  p.expr0, p.expr1)

    @_('expr EXCLAMATIONMARKEQUAL expr')
    def expr(self, p):
        return ('binary_op: !=',  p.expr0, p.expr1)

    @_('expr LARROW expr')
    def expr(self, p):
        return ('binary_op: <',   p.expr0, p.expr1)

    @_('expr RARROW expr')
    def expr(self, p):
        return ('binary_op: >',   p.expr0, p.expr1)

    @_('expr LARROWEQUAL expr')
    def expr(self, p):
        return ('binary_op: <=',  p.expr0, p.expr1)

    @_('expr RARROWEQUAL expr')
    def expr(self, p):
        return ('binary_op: >=',  p.expr0, p.expr1)

    @_('expr PLUS expr')
    def expr(self, p):
        return ('binary_op: +',   p.expr0, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return ('binary_op: -',   p.expr0, p.expr1)

    @_('expr ASTERISK expr')
    def expr(self, p):
        return ('binary_op: *',   p.expr0, p.expr1)

    @_('expr SLASH expr')
    def expr(self, p):
        return ('binary_op: /',   p.expr0, p.expr1)

    @_('expr PERCENT expr')
    def expr(self, p):
        return ('binary_op: %',   p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return ('unary_op: -', p.expr)
    
    @_('PLUS expr %prec UMINUS')
    def expr(self, p):
        return ('unary_op: +', p.expr)

    @_('EXCLAMATIONMARK expr')
    def expr(self, p):
        return ('unary_op: !', p.expr)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('INTEGER')
    def expr(self, p):
        return 'literal: i32, ' + str(p.INTEGER)

    @_('FLOAT')
    def expr(self, p):
        return 'literal: f64, ' + p.FLOAT

    @_('KEYWORD_true')
    def expr(self, p):
        return 'literal: bool, true'

    @_('KEYWORD_false')
    def expr(self, p):
        return 'literal: bool, false'

    @_('CHAR_LITERAL')
    def expr(self, p):
        return 'literal: u8, ' + str(p.CHAR_LITERAL)

    @_('STRINGLITERAL')
    def expr(self, p):
        return 'literal: []const u8, ' + str(p.STRINGLITERAL)

    @_('IDENTIFIER LPAREN arglist RPAREN')
    def expr(self, p):
        return ('call: ' + p.IDENTIFIER, p.arglist)

    @_('IDENTIFIER LPAREN RPAREN')
    def expr(self, p):
        return ('call: ' + p.IDENTIFIER, [])

    @_('BUILTINIDENTIFIER LPAREN arglist RPAREN')
    def expr(self, p):
        return ('builtin: ' + p.BUILTINIDENTIFIER, p.arglist)

    @_('BUILTINIDENTIFIER LPAREN RPAREN')
    def expr(self, p):
        return ('builtin: ' + p.BUILTINIDENTIFIER, [])

    @_('IDENTIFIER')
    def expr(self, p):
        return 'location: ' + p.IDENTIFIER

    @_('arglist COMMA expr')
    def arglist(self, p):
        return p.arglist + [p.expr]

    @_('expr')
    def arglist(self, p):
        return [p.expr]

    @_('SEMI')
    def stmt(self, p):
        return ('expression', None)

    def error(self, token):
        self._had_error = True
        if token:
            print(f"Syntax error at line {token.lineno}, token={token.type}")
        else:
            print("Parse error in input. EOF")
        
def _build_lines(first, other, values):
    try:
        yield first + next(values)
        for value in values:
            yield other + value
    except StopIteration:
        return

def _build_tree(node):
    if isinstance(node, list):
        if not node:
            yield ' None'
            return
        node = tuple(node)
    if not isinstance(node, tuple):
        yield ' ' + str(node)
        return
    values = [_build_tree(n) for n in node]
    if len(values) == 1:
        yield from _build_lines('──', '  ', values[0])
        return
    start, *mid, end = values
    yield from _build_lines('┬─', '│ ', start)
    for value in mid:
        yield from _build_lines('├─', '│ ', value)
    yield from _build_lines('└─', '  ', end)

def build_tree(root):
    return '\n'.join(_build_tree(root))

def parse_tokens(tokens):
    parser = zigParser()
    parser._had_error = False
    tree = parser.parse(tokens)
    if tree is None:
        return None
    if parser._had_error and tree[1] == []:
        return None
    return tree