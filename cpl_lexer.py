from sly import Lexer


class CPLLexer(Lexer):
    tokens = {ELSE, FLOAT, IF, INPUT, INT, OUTPUT, WHILE,
              # operators
              RELOP, ADDOP, MULOP, OR, AND, NOT, CAST,
              # extra symbols
              ID, NUM}

    literals = {'(', ')', '{', '}', ',', ':', ';', '='}

    # String containing ignored characters
    ignore = ' \t'
    ignore_comment = r'\/\*(\*(?!\/)|[^*])*\*\/'

    ELSE = r'else'
    FLOAT = r'float'
    IF = r'if'
    INPUT = r'input'
    INT = 'int'
    OUTPUT = 'output'
    WHILE = r'while'

    RELOP = r'==|!=|>=|<=|<|>'
    ADDOP = r'[-+]'
    MULOP = r'[*/]'
    OR = r'\|\|'
    AND = r'&&'
    NOT = r'!'

    @_(r'static\_cast<(int|float)>')
    def CAST(self, t):
        if 'int' in t.value:
            t.value = 'int'
        else:
            t.value = 'float'
        return t

    ID = r'[a-zA-Z][a-zA-Z0-9]*'

    @_(r'\d+\.\d*|\d+')
    def NUM(self, t):
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
