# High level function that takes input source text and turns it into tokens.
# This is a natural place to use some kind of generator function.
from sly import Lexer

class zigLexer(Lexer):
    tokens = {
        'KEYWORD_and',
        'KEYWORD_break',
        'KEYWORD_const',
        'KEYWORD_continue',
        'KEYWORD_else',
        'KEYWORD_false',
        'KEYWORD_if',
        'KEYWORD_or',
        'KEYWORD_true',
        'KEYWORD_var',
        'KEYWORD_while',
        'IDENTIFIER',
        'BUILTINIDENTIFIER',
        'INTEGER',
        'FLOAT',
        'CHAR_LITERAL',
        'STRINGLITERAL',
        'EQUALEQUAL',
        'EXCLAMATIONMARKEQUAL',
        'LARROWEQUAL',
        'RARROWEQUAL',
        'LARROW',
        'RARROW',
        'PLUS',
        'MINUS',
        'ASTERISK',
        'SLASH',
        'PERCENT',
        'EQUAL',
        'EXCLAMATIONMARK',
        'COLON',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'COMMA',
        'SEMI'
    }
    
    EQUALEQUAL = r'=='
    EXCLAMATIONMARKEQUAL = r'!='
    LARROWEQUAL = r'<='
    RARROWEQUAL = r'>='
    PLUS = r'\+'
    MINUS = r'-'
    ASTERISK = r'\*'
    PERCENT = r'%'
    EQUAL = r'='
    LARROW = r'<'
    RARROW = r'>'
    EXCLAMATIONMARK = r'!'
    COLON = r':'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    COMMA = r','
    SEMI = r';'
    FLOAT = r'\d*\.\d+|\d+\.'
    INTEGER = r'\d+'
    BUILTINIDENTIFIER = r'@[a-zA-Z_][0-9a-zA-Z_]*'
    ignore = ' \t'

    @_(r'[a-zA-Z_][0-9a-zA-Z_]*')
    def IDENTIFIER(self, t):
        keywords = {
            'and', 'break', 'const', 'continue', 'else',
            'false', 'if', 'or', 'true', 'var', 'while'
        }
        if t.value in keywords:
            t.type = 'KEYWORD_' + t.value
        return t

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignore_comment(self, t):
        pass

    @_(r'/')
    def SLASH(self, t):
        return t
    
    @_(r'"(?:\\.|[^"\\])*"')
    def STRINGLITERAL(self, t):
        self.lineno += t.value.count('\n')
        return t

    @_(r'"(?:\\.|[^"\\])*')
    def STRING_UNTERMINATED(self, t):
        print(f'{self.lineno}: Unterminated string literal')
        self.lineno += t.value.count('\n')
    
    @_(r"'(?:\\.|[^'\\\n])*'")
    def CHAR_LITERAL(self, t):
        return t
    
    @_(r"'(?:\\.|[^'\\\n])*")
    def CHAR_UNTERMINATED_ERROR(self, t):
        print(f'{self.lineno}: Unterminated character constant')
    
    def error(self, t):
        print(f'{self.lineno}: Illegal character \'{t.value[0]}\'')
        self.index += 1
    
def tokenize(text):
    lexer = zigLexer()
    yield from lexer.tokenize(text)