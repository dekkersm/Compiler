from cpl_lexer import CPLLexer
from cpl_parser import CPLParser
from symbol_table import SymTable
from quad import QuadCode

if __name__ == '__main__':
    data = ''' a, b: float;
c, d: int;
/* TODO: Test! */
{
    /* Cast is required here! */
    c = static_cast<int>(a + d);
    c = static_cast<int>(a) + d;
    b = a + static_cast<int>(d);

    c = static_cast<int>(static_cast<float>(a) * static_cast<float>(c));

    /* Both should produce the same Quad code. */
    b = static_cast<int>(b) + static_cast<int>(a);
    b = static_cast<float>(static_cast<int>(b) + static_cast<int>(a));
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
