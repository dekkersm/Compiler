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
        should_create_file = True
        ast = None

        try:
            ast = parser.parse(lexer.tokenize(source))
            should_create_file = not (lexer.were_errors or parser.were_errors)
            print(f'parsed ast: \n{ast}')
        except EOFError:
            logger.error(f"Failed read cpl file! {file_path}")
            exit(-1)

        if ast is not None:
            code = QuadCode(ast, sym_table)
            should_create_file = code.success
            if code is not None and should_create_file:
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
