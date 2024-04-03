import logging

from sly import Parser
from cpl_lexer import CPLLexer


class CPLParser(Parser):

    def __init__(self, symbol_table):
        super().__init__()
        self.symbolTable = symbol_table

    # Get the token list from the lexer (required)
    tokens = CPLLexer.tokens
    debugfile = 'parser.out'

    # Grammar rules and actions
    @_('declarations stmt_block')
    def program(self, p):
        return 'program', p.declarations, p.stmt_block

    @_('declarations declaration',
       'empty')
    def declarations(self, p):
        if len(p) == 2:
            return p.declarations + [p.declaration]
        else:
            return []

    @_('idlist ":" type ";"')
    def declaration(self, p):
        for token in p.idlist:
            if not self.symbolTable.search(token):
                self.symbolTable.insert(token, p.type)
            else:
                return f'ERROR: Variable already defined at line {p.lineno}'
        return 'declaration', p.idlist, p.type

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
        return p[0]

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        return 'assignment_stmt', p.ID, p.expression

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        return 'input_stmt', p.ID

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        return 'output_stmt', p.expression

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return 'if_stmt', p.boolexpr, p.stmt0, p.stmt1

    @_('WHILE "(" boolexpr ")" stmt')
    def while_stmt(self, p):
        return 'while_stmt', p.boolexpr, p.stmt

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return 'stmtlist', p.stmtlist

    @_('stmtlist stmt')
    def stmtlist(self, p):
        p.stmtlist.append(p.stmt)
        return p.stmtlist

    @_('empty')
    def stmtlist(self, p):
        return []

    @_('boolexpr OR boolterm')
    def boolexpr(self, p):
        return p[1], p.boolexpr, p.boolterm

    @_('boolterm')
    def boolexpr(self, p):
        return p.boolterm

    @_('boolterm AND boolfactor')
    def boolterm(self, p):
        return p[1], p.boolterm, p.boolfactor

    @_('boolfactor')
    def boolterm(self, p):
        return p.boolfactor

    @_('NOT "(" boolexpr ")"')
    def boolfactor(self, p):
        return 'not_boolexpr', p.boolexpr

    @_('expression RELOP expression')
    def boolfactor(self, p):
        return 'relop', p.RELOP, p.expression0, p.expression1

    @_('expression ADDOP term')
    def expression(self, p):
        return 'addop', p.ADDOP, p.expression, p.term

    @_('term')
    def expression(self, p):
        return p.term

    @_('term MULOP factor')
    def term(self, p):
        return 'mulop', p.MULOP, p.term, p.factor

    @_('factor')
    def term(self, p):
        return p.factor

    @_('"(" expression ")"')
    def factor(self, p):
        return p.expression

    @_('CAST "(" expression ")"')
    def factor(self, p):
        return 'cast_expression', p.CAST, p.expression

    @_('ID')
    def factor(self, p):
        return 'id', p.ID

    @_('NUM')
    def factor(self, p):
        return 'num', p.NUM

    @_('')
    def empty(self, p):
        pass

    def error(self, token):
        logger = logging.getLogger()
        logger.error(f'SYNTAX ERROR: near token "{token.value}" at line {token.lineno}')
