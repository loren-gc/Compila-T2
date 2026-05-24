import sys
from sly import Parser
from uzig_lexer import UZigLexer

class UZigParser(Parser):
    tokens = UZigLexer.tokens

    precedence = (
        ('nonassoc', 'LOWER_THAN_ELSE'),
        ('nonassoc', 'KEYWORD_else'),
        ('left', 'KEYWORD_or'),
        ('left', 'KEYWORD_and'),
        ('left', 'EQUALEQUAL', 'EXCLAMATIONMARKEQUAL'),
        ('left', 'LARROW', 'LARROWEQUAL', 'RARROW', 'RARROWEQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'ASTERISK', 'SLASH', 'PERCENT'),
        ('right', 'UMINUS', 'UPLUS', 'EXCLAMATIONMARK'), 
    )

    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    @_('assignment_statement',
       'variable_definition',
       'const_definition',
       'if_statement',
       'while_statement',
       'break_statement',
       'continue_statement',
       'expression_statement')
    def statement(self, p):
        return p[0]

    @_('location EQUAL expression SEMI')
    def assignment_statement(self, p):
        return ('assignment', p.location, p.expression)

    @_('KEYWORD_var IDENTIFIER COLON type EQUAL expression SEMI')
    def variable_definition(self, p):
        return (f'variable: {p.IDENTIFIER}', p.type, p.expression)

    @_('KEYWORD_var IDENTIFIER COLON type SEMI')
    def variable_definition(self, p):
        return (f'variable: {p.IDENTIFIER}', p.type, 'None')

    @_('KEYWORD_var IDENTIFIER EQUAL expression SEMI')
    def variable_definition(self, p):
        return (f'variable: {p.IDENTIFIER}', 'None', p.expression)

    @_('KEYWORD_const IDENTIFIER COLON type EQUAL expression SEMI')
    def const_definition(self, p):
        return (f'const: {p.IDENTIFIER}', p.type, p.expression)

    @_('KEYWORD_const IDENTIFIER EQUAL expression SEMI')
    def const_definition(self, p):
        return (f'const: {p.IDENTIFIER}', 'None', p.expression)

    @_('KEYWORD_if LPAREN expression RPAREN block %prec LOWER_THAN_ELSE')
    def if_statement(self, p):
        return ('if', p.expression, p.block, 'None')

    @_('KEYWORD_if LPAREN expression RPAREN block KEYWORD_else block')
    def if_statement(self, p):
        return ('if', p.expression, p.block0, p.block1)

    @_('KEYWORD_if LPAREN expression RPAREN block KEYWORD_else if_statement')
    def if_statement(self, p):
        return ('if', p.expression, p.block, p.if_statement)

    @_('KEYWORD_while LPAREN expression RPAREN block')
    def while_statement(self, p):
        return ('while', p.expression, p.block)

    @_('KEYWORD_break SEMI')
    def break_statement(self, p):
        return 'break'

    @_('KEYWORD_continue SEMI')
    def continue_statement(self, p):
        return 'continue'

    @_('expression SEMI')
    def expression_statement(self, p):
        return ('expression', p.expression)

    @_('SEMI')
    def expression_statement(self, p):
        return ('expression', 'None')

    @_('LBRACE statement_list RBRACE')
    def block(self, p):
        return ('block', p.statement_list)

    @_('LBRACE RBRACE')
    def block(self, p):
        return ('block', 'None')

    @_('expression PLUS expression',
       'expression MINUS expression',
       'expression ASTERISK expression',
       'expression SLASH expression',
       'expression PERCENT expression',
       'expression LARROWEQUAL expression',
       'expression LARROW expression',
       'expression RARROWEQUAL expression',
       'expression RARROW expression',
       'expression EQUALEQUAL expression',
       'expression EXCLAMATIONMARKEQUAL expression',
       'expression KEYWORD_and expression',
       'expression KEYWORD_or expression')
    def expression(self, p):
        return (f'binary_op: {p[1]}', p.expression0, p.expression1)

    @_('PLUS expression %prec UPLUS',
       'MINUS expression %prec UMINUS',
       'EXCLAMATIONMARK expression')
    def expression(self, p):
        return (f'unary_op: {p[0]}', p.expression)

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('location')
    def expression(self, p):
        return p.location

    @_('BUILTINIDENTIFIER LPAREN expression_list RPAREN')
    def expression(self, p):
        return (f'builtin: {p.BUILTINIDENTIFIER}', p.expression_list)

    @_('BUILTINIDENTIFIER LPAREN RPAREN')
    def expression(self, p):
        return (f'builtin: {p.BUILTINIDENTIFIER}', [])

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return p.expression

    @_('INTEGER')
    def literal(self, p):
        return f"literal: i32, {p.INTEGER}"

    @_('FLOAT')
    def literal(self, p):
        return f"literal: f64, {p.FLOAT}"

    @_('KEYWORD_true', 'KEYWORD_false')
    def literal(self, p):
        return f"literal: bool, {p[0]}"

    @_('STRINGLITERAL')
    def literal(self, p):
        return f"literal: []const u8, {p.STRINGLITERAL}"

    @_('CHAR_LITERAL')
    def literal(self, p):
        return f"literal: u8, {p.CHAR_LITERAL}"
    
    @_('expression')
    def expression_list(self, p):
        return [p.expression]

    @_('expression_list COMMA expression')
    def expression_list(self, p):
        return p.expression_list + [p.expression]

    @_('IDENTIFIER')
    def location(self, p):
        return f"location: {p.IDENTIFIER}"

    @_('IDENTIFIER')
    def type(self, p):
        return f"type: {p.IDENTIFIER}"

    def error(self, token):
        if token:
            print(f"Syntax error at line {token.lineno}, token={token.type}")
        else:
            print("Parse error in input. EOF")

def parse_tokens(tokens):
    parser = UZigParser()
    return parser.parse(tokens)

def build_tree(root):
    return '\n'.join(_build_tree(root))

def _build_tree(node):
    if isinstance(node, list):
        if not node: return
        node = tuple(node)
    if not isinstance(node, tuple):
        yield " " + str(node)
        return
    values = [_build_tree(n) for n in node]
    if len(values) == 1:
        yield from build_lines('──', '  ', values[0])
        return
    start, *mid, end = values
    yield from build_lines('┬─', '│ ', start)
    for value in mid:
        yield from build_lines('├─', '│ ', value)
    yield from build_lines('└─', '  ', end)

def build_lines(first, other, values):
    try:
        yield first + next(values)
        for value in values:
            yield other + value
    except StopIteration:
        return