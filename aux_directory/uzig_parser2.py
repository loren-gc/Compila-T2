# High level function that takes input tokens and turns it into a syntax tree.
# This is a natural place to use some kind of generator function.

import sys
from sly import Parser
from uzig_lexer import zigLexer


def _node(tag, *children):
    return (tag,) + children


class zigParser(Parser):

    tokens = zigLexer.tokens
    precedence = ( ('nonassoc', 'LOWER_THAN_ELSE'), ('nonassoc', 'KEYWORD_else'), ('left', 'KEYWORD_or'), ('left', 'KEYWORD_and'), ('left', 'EQUALEQUAL', 'EXCLAMATIONMARKEQUAL'), ('left', 'LARROW', 'LARROWEQUAL', 'RARROW', 'RARROWEQUAL'), ('left', 'PLUS', 'MINUS'), ('left', 'ASTERISK', 'SLASH', 'PERCENT'), ('right', 'UMINUS', 'UPLUS', 'EXCLAMATIONMARK'),
    )

    @_('statement_list')
    def program(self, p):
        return _node('program', p.statement_list)

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
        return _node('assignment', p.location, p.expression)

    @_('KEYWORD_var IDENTIFIER COLON type EQUAL expression SEMI')
    def variable_definition(self, p):
        return _node(f'variable: {p.IDENTIFIER}', p.type, p.expression)

    @_('KEYWORD_var IDENTIFIER COLON type SEMI')
    def variable_definition(self, p):
        return _node(f'variable: {p.IDENTIFIER}', p.type, 'None')

    @_('KEYWORD_var IDENTIFIER EQUAL expression SEMI')
    def variable_definition(self, p):
        return _node(f'variable: {p.IDENTIFIER}', 'None', p.expression)

    @_('KEYWORD_const IDENTIFIER COLON type EQUAL expression SEMI')
    def const_definition(self, p):
        return _node(f'const: {p.IDENTIFIER}', p.type, p.expression)

    @_('KEYWORD_const IDENTIFIER EQUAL expression SEMI')
    def const_definition(self, p):
        return _node(f'const: {p.IDENTIFIER}', 'None', p.expression)

    @_('KEYWORD_if LPAREN expression RPAREN block %prec LOWER_THAN_ELSE')
    def if_statement(self, p):
        return _node('if', p.expression, p.block, 'None')

    @_('KEYWORD_if LPAREN expression RPAREN block KEYWORD_else block')
    def if_statement(self, p):
        return _node('if', p.expression, p.block0, p.block1)

    @_('KEYWORD_if LPAREN expression RPAREN block KEYWORD_else if_statement')
    def if_statement(self, p):
        return _node('if', p.expression, p.block, p.if_statement)

    @_('KEYWORD_while LPAREN expression RPAREN block')
    def while_statement(self, p):
        return _node('while', p.expression, p.block)

    @_('KEYWORD_break SEMI')
    def break_statement(self, p):
        return 'break'

    @_('KEYWORD_continue SEMI')
    def continue_statement(self, p):
        return 'continue'

    @_('expression SEMI')
    def expression_statement(self, p):
        return _node('expression', p.expression)

    @_('SEMI')
    def expression_statement(self, p):
        return _node('expression', 'None')

    @_('LBRACE statement_list RBRACE')
    def block(self, p):
        return _node('block', p.statement_list)

    @_('LBRACE RBRACE')
    def block(self, p):
        return _node('block', 'None')

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
        return _node(f'binary_op: {p[1]}', p.expression0, p.expression1)

    @_('PLUS expression %prec UPLUS',
       'MINUS expression %prec UMINUS',
       'EXCLAMATIONMARK expression')
    def expression(self, p):
        return _node(f'unary_op: {p[0]}', p.expression)

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('location')
    def expression(self, p):
        return p.location

    @_('BUILTINIDENTIFIER LPAREN expression_list RPAREN')
    def expression(self, p):
        return _node(f'builtin: {p.BUILTINIDENTIFIER}', p.expression_list)

    @_('BUILTINIDENTIFIER LPAREN RPAREN')
    def expression(self, p):
        return _node(f'builtin: {p.BUILTINIDENTIFIER}', [])

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


def parse_tokens(token_stream):
    return zigParser().parse(token_stream)

def _collect_lines(node, lines, indent, last):
    branch = '└── ' if last else '├── '
    extension = '    ' if last else '│   '
    if isinstance(node, list):
        if not node:
            return
        node = tuple(node)
    if not isinstance(node, tuple):
        lines.append(indent + branch + str(node))
        return
    label, *children = node
    lines.append(indent + branch + str(label))
    for i, child in enumerate(children):
        _collect_lines(child, lines, indent + extension, i == len(children) - 1)

def build_tree(root):
    lines = []
    _collect_lines(root, lines, '', True)
    return '\n'.join(lines)