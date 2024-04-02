from sly import Parser
from cpl_lexer import CPLLexer
from cpl_ast import Declaration, Declarations, Program


class CPLParser(Parser):

    def __init__(self):
        self.idlist = []
    # Get the token list from the lexer (required)
    tokens = CPLLexer.tokens
    debugfile = 'parser.out'

    # Grammar rules and actions
    @_('declarations stmt_block')
    def program(self, p):
        Program()
        return p

    @_('declarations declaration',
       'empty')
    def declarations(self, p):
        if len(p) == 2:
            return Declarations(p.declarations.dec_list + [p.declaration])
        else:
            return Declarations([])

    @_('idlist ":" type ";"')
    def declaration(self, p):
        return Declaration(p.idlist, p.type)

    @_('INT',
       'FLOAT')
    def type(self, p):
        return p[0]

    @_('idlist "," ID')
    def idlist(self, p):
        return p.idlist + [p.ID]

    @_('ID')
    def idlist(self, p):
        return [p[0]]

    @_('assignment_stmt',
       'input_stmt',
       'output_stmt',
       'if_stmt',
       'while_stmt',
       'stmt_block')
    def stmt(self, p):
        return p

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        return p

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        return p

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        return p

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return p

    @_('WHILE "(" boolexpr ")" stmt')
    def while_stmt(self, p):
        return p

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return p

    @_('stmtlist stmt',
       'empty')
    def stmtlist(self, p):
        return p

    @_('boolexpr OR boolterm',
       'boolterm')
    def boolexpr(self, p):
        return p

    @_('boolterm AND boolfactor',
       'boolfactor')
    def boolterm(self, p):
        return p

    @_('NOT "(" boolexpr ")"',
       'expression RELOP expression')
    def boolfactor(self, p):
        return p

    @_('expression ADDOP term',
       'term')
    def expression(self, p):
        return p

    @_('term MULOP factor',
       'factor')
    def term(self, p):
        return p

    @_('"(" expression ")"')
    def factor(self, p):
        return p.expression

    @_('CAST "(" expression ")"')
    def factor(self, p):
        return p

    @_('ID', 'NUM')
    def factor(self, p):
        return p[0]

    @_('')
    def empty(self, p):
        pass
