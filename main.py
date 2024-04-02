from cpl_lexer import CPLLexer
from cpl_parser import CPLParser

if __name__ == '__main__':
    data = ''' /* Min - Finding minimum between two numbers */
a, b: float;
{
   input(a);
   input(b);
   if (a < b)
      output(a);
    else
      output(b);
}
'''
    lexer = CPLLexer()
    # for tok in lexer.tokenize(data):
    #     print(tok)

    parser = CPLParser()

    try:
        result = parser.parse(lexer.tokenize(data))
        print(result)
    except EOFError:
        print("end")
