from cpl_lexer import CPLLexer
from cpl_parser import CPLParser
from symbol_table import SymTable
from quad import QuadCode

if __name__ == '__main__':
    data = ''' /* Min - Finding minimum between two numbers */
a, b: float;
{
   input(a);
   input(b);
   if (a < 2.5)
      output(a);
    else
      output(b);
}
'''
    lexer = CPLLexer()
    # for tok in lexer.tokenize(data):
    #     print(tok)

    sym_table = SymTable()
    parser = CPLParser(sym_table)

    try:
        ast = parser.parse(lexer.tokenize(data))
        print(ast)
        QuadCode(ast, sym_table)
    except EOFError:
        print("end")
