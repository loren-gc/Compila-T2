# High level function that takes input tokens and turns it into a syntax tree.
# This is a natural place to use some kind of generator function.

from sly import Parser
# from analisador_lexico import zigLexer

class zigParser(Parser):
    """
    LALR(1) parser for the uZig language.
    Produces an AST as nested tuples/lists.

    Grammar (informal):
        program       ::= stmt*
        stmt          ::= var_decl | const_decl | assign_stmt
                        | if_stmt  | while_stmt
                        | break    | continue
                        | expr_stmt | block
        var_decl      ::= 'var'   IDENTIFIER ':' type ('=' expr)? ';'
        const_decl    ::= 'const' IDENTIFIER ':' type  '=' expr   ';'
        assign_stmt   ::= IDENTIFIER '=' expr ';'
        if_stmt       ::= 'if' '(' expr ')' block ('else' stmt)?
        while_stmt    ::= 'while' '(' expr ')' block
        block         ::= '{' stmt* '}'
        type          ::= IDENTIFIER
        expr          ::= binary | unary | primary
        primary       ::= literal | IDENTIFIER | call | builtin_call | '(' expr ')'
        call          ::= IDENTIFIER       '(' arglist? ')'
        builtin_call  ::= BUILTINIDENTIFIER '(' arglist? ')'
        arglist       ::= expr (',' expr)*
    """

    tokens = zigLexer.tokens

    precedence = (
        ('left',     'KEYWORD_or'),
        ('left',     'KEYWORD_and'),
        ('left',     'EQUALEQUAL', 'EXCLAMATIONMARKEQUAL'),
        ('left',     'LARROW', 'RARROW', 'LARROWEQUAL', 'RARROWEQUAL'),
        ('left',     'PLUS', 'MINUS'),
        ('left',     'ASTERISK', 'SLASH', 'PERCENT'),
        ('right',    'UMINUS', 'EXCLAMATIONMARK'),
        ('nonassoc', 'IFX'),
        ('nonassoc', 'KEYWORD_else'),
    )

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
        return ('variable: ' + p.IDENTIFIER, 'type: ' + p.type)

    @_('KEYWORD_const IDENTIFIER COLON type EQUAL expr SEMI')
    def stmt(self, p):
        return ('constant: ' + p.IDENTIFIER, 'type: ' + p.type, p.expr)

    @_('IDENTIFIER EQUAL expr SEMI')
    def stmt(self, p):
        return ('assignment', 'location: ' + p.IDENTIFIER, p.expr)

    @_('KEYWORD_if LPAREN expr RPAREN block %prec IFX')
    def stmt(self, p):
        return ('if', p.expr, p.block)

    @_('KEYWORD_if LPAREN expr RPAREN block KEYWORD_else stmt')
    def stmt(self, p):
        return ('if', p.expr, p.block, p.stmt)

    @_('KEYWORD_while LPAREN expr RPAREN block')
    def stmt(self, p):
        return ('while', p.expr, p.block)

    @_('KEYWORD_break SEMI')
    def stmt(self, p):
        return ('break',)

    @_('KEYWORD_continue SEMI')
    def stmt(self, p):
        return ('continue',)

    @_('expr SEMI')
    def stmt(self, p):
        return ('expression', p.expr)

    @_('block')
    def stmt(self, p):
        return p.block

    @_('LBRACE stmtlist RBRACE')
    def block(self, p):
        return ('block', p.stmtlist)

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
        return 'literal: f32, ' + str(p.FLOAT)

    @_('KEYWORD_true')
    def expr(self, p):
        return 'literal: bool, true'

    @_('KEYWORD_false')
    def expr(self, p):
        return 'literal: bool, false'

    @_('CHAR_LITERAL')
    def expr(self, p):
        return 'literal: char, ' + str(p.CHAR_LITERAL)

    @_('STRINGLITERAL')
    def expr(self, p):
        return 'literal: str, ' + str(p.STRINGLITERAL)

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

    def error(self, token):
        if token:
            raise SyntaxError(
                f"Syntax error at line {token.lineno}: "
                f"unexpected token '{token.value}' (type: {token.type})"
            )
        else:
            raise SyntaxError("Syntax error: unexpected end of input")
        
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
    tree = zigParser().parse(tokens)
    if tree is not None:
        return build_tree(tree)
    return ''