import logging
import sys

from cpl_lexer import CPLLexer
from cpl_parser import CPLParser
from symbol_table import SymTable
from quad import QuadCode

if __name__ == '__main__':
    args = sys.argv[1:]
    logger = logging.getLogger()
    logger.error(f"------------May Dekkers---------------")

    if len(args) == 1 and args[0].split('.')[1] == 'ou':
        file_path = args[0]
        file_name = file_path.split('.')[0]
        try:
            with open(file_path, 'r') as f:
                source = f.read()
        except IOError:
            logger.error(f"Failed to open source file {file_path}")
            exit(-1)

        lexer = CPLLexer()
        sym_table = SymTable()
        parser = CPLParser(sym_table)

        try:
            ast = parser.parse(lexer.tokenize(source))
            print(f'parsed ast: \n{ast}')
        except EOFError:
            logger.error(f"Failed read clp file! {file_path}")
            exit(-1)

        if ast is not None:
            code = QuadCode(ast, sym_table)
            if code is not None:
                code.create_file(file_name + '.qud')
            else:
                logger.error(f"Encountered errors while trying to compile {file_path}!")
                exit(-1)
        else:
            logger.error(f"Encountered syntax errors while trying to parse {file_path}!")
            exit(-1)
    else:
        logger.error(f"Bad arguments. terminating compiler")
        exit(-1)
