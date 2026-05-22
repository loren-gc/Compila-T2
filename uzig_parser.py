# High level function that takes input tokens and turns it into a syntax tree.
# This is a natural place to use some kind of generator function.

from sly import Parser
#from analisador_lexico import zigLexer

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
        ('left', 'KEYWORD_or'), ('left', 'KEYWORD_and'), ('left', 'EQUALEQUAL', 'EXCLAMATIONMARKEQUAL'), ('left', 'LARROW', 'RARROW', 'LARROWEQUAL',  'RARROWEQUAL'), ('left', 'PLUS', 'MINUS'), ('left', 'ASTERISK', 'SLASH', 'PERCENT'), ('right', 'UMINUS', 'EXCLAMATIONMARK'), ('nonassoc', 'IFX'), ('nonassoc', 'KEYWORD_else'),
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
        return ('var', p.IDENTIFIER, p.type, p.expr)

    @_('KEYWORD_var IDENTIFIER COLON type SEMI')
    def stmt(self, p):
        return ('var', p.IDENTIFIER, p.type, None)

    @_('KEYWORD_const IDENTIFIER COLON type EQUAL expr SEMI')
    def stmt(self, p):
        return ('const', p.IDENTIFIER, p.type, p.expr)

    @_('IDENTIFIER EQUAL expr SEMI')
    def stmt(self, p):
        return ('assign', p.IDENTIFIER, p.expr)

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
        return ('break',)

    @_('KEYWORD_continue SEMI')
    def stmt(self, p):
        return ('continue',)

    @_('expr SEMI')
    def stmt(self, p):
        return ('expr_stmt', p.expr)

    @_('block')
    def stmt(self, p):
        return p.block

    @_('LBRACE stmtlist RBRACE')
    def block(self, p):
        return ('block', p.stmtlist)
    
    @_('IDENTIFIER')
    def type(self, p):
        return ('type', p.IDENTIFIER)

    @_('expr KEYWORD_or expr')
    def expr(self, p):
        return ('or',  p.expr0, p.expr1)

    @_('expr KEYWORD_and expr')
    def expr(self, p):
        return ('and', p.expr0, p.expr1)

    @_('expr EQUALEQUAL expr')
    def expr(self, p):
        return ('==',  p.expr0, p.expr1)

    @_('expr EXCLAMATIONMARKEQUAL expr')
    def expr(self, p):
        return ('!=',  p.expr0, p.expr1)

    @_('expr LARROW expr')
    def expr(self, p):
        return ('<',   p.expr0, p.expr1)

    @_('expr RARROW expr')
    def expr(self, p):
        return ('>',   p.expr0, p.expr1)

    @_('expr LARROWEQUAL expr')
    def expr(self, p):
        return ('<=',  p.expr0, p.expr1)

    @_('expr RARROWEQUAL expr')
    def expr(self, p):
        return ('>=',  p.expr0, p.expr1)

    @_('expr PLUS expr')
    def expr(self, p):
        return ('+',   p.expr0, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return ('-',   p.expr0, p.expr1)

    @_('expr ASTERISK expr')
    def expr(self, p):
        return ('*',   p.expr0, p.expr1)

    @_('expr SLASH expr')
    def expr(self, p):
        return ('/',   p.expr0, p.expr1)

    @_('expr PERCENT expr')
    def expr(self, p):
        return ('%',   p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('EXCLAMATIONMARK expr')
    def expr(self, p):
        return ('not', p.expr)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('INTEGER')
    def expr(self, p):
        return ('int',    int(p.INTEGER))

    @_('FLOAT')
    def expr(self, p):
        return ('float',  float(p.FLOAT))

    @_('KEYWORD_true')
    def expr(self, p):
        return ('bool',   True)

    @_('KEYWORD_false')
    def expr(self, p):
        return ('bool',   False)

    @_('CHAR_LITERAL')
    def expr(self, p):
        return ('char',   p.CHAR_LITERAL)

    @_('STRINGLITERAL')
    def expr(self, p):
        return ('string', p.STRINGLITERAL)

    @_('IDENTIFIER LPAREN arglist RPAREN')
    def expr(self, p):
        return ('call', p.IDENTIFIER, p.arglist)

    @_('IDENTIFIER LPAREN RPAREN')
    def expr(self, p):
        return ('call', p.IDENTIFIER, [])

    @_('BUILTINIDENTIFIER LPAREN arglist RPAREN')
    def expr(self, p):
        return ('builtin_call', p.BUILTINIDENTIFIER, p.arglist)

    @_('BUILTINIDENTIFIER LPAREN RPAREN')
    def expr(self, p):
        return ('builtin_call', p.BUILTINIDENTIFIER, [])
        
    @_('IDENTIFIER')
    def expr(self, p):
        return ('var', p.IDENTIFIER)
        
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

def parse_tokens(tokens):
    parser = zigParser()
    return parser.parse(iter(tokens))
