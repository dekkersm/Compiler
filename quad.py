import logging
import textwrap


class QuadCode:
    int_op_dict = {'==': 'IEQL',
                   '!=': 'INQL',
                   '>=': 'ILSS!!!!!',
                   '<=': 'IGRT!!!!!',
                   '<': 'ILSS',
                   '>': 'IGRT',
                   '+': 'IADD',
                   '-': 'ISUB',
                   '*': 'IMLT',
                   '/': 'IDIV'}

    float_op_dict = {'==': 'REQL',
                     '!=': 'RNQL',
                     '>=': 'ILSS!!!!!',
                     '<=': 'IGRT!!!!!',
                     '<': 'RLSS',
                     '>': 'RGRT',
                     '+': 'RADD',
                     '-': 'RSUB',
                     '*': 'RMLT',
                     '/': 'RDIV'}

    def __init__(self, tree, symbol_table):
        self.label_count = 0
        self.temp_count = 0
        self.symbolTable = symbol_table
        self.logger = logging.getLogger()
        self.success = True

        self.code = self.walk_tree(tree)
        print(self.code)

    def create_file(self, path):
        # format file
        self.code = textwrap.indent(self.code, 5 * ' ', lambda line: ':' not in line)
        with open(path, 'w') as f:
            f.writelines(self.code)

    def gen_label(self) -> str:
        self.label_count = self.label_count + 1
        return '$L' + str(self.label_count)

    def gen_temp(self) -> str:
        self.temp_count = self.temp_count + 1
        return '$temp' + str(self.temp_count)

    # returns the new var id, the new type and code lines
    def cast_expression(self, var, curr_type, to_type):
        code_lines = ''
        # do nothing if equal
        if not curr_type == to_type:
            old_var = var
            var = self.gen_temp()
            if to_type == 'float':
                code_lines = f'ITOR {var} {old_var}\n'
            else:
                code_lines = f'RTOI {var} {old_var}\n'
        return var, to_type, code_lines

    # returns the execution return identifier and the added code lines
    def rel_op(self, relop, exp0, exp0_type, exp1, exp1_type, added_lines):
        temp_var = self.gen_temp()
        if exp0_type == 'int' and exp1_type == 'int':
            if relop == '>=' or relop == '<=':
                # for these relops, take the first char in '<=/>=' and flip the attributes
                # then, preform not on the result
                return temp_var, added_lines + f'{self.int_op_dict.get(relop[0])} {temp_var} {exp1} {exp0}\n' \
                                               f'{self.int_op_dict.get("==")} {temp_var} {temp_var} {0}\n'
            return temp_var, added_lines + f'{self.int_op_dict.get(relop)} {temp_var} {exp0} {exp1}\n'
        else:
            # cast int expression to float
            exp0, exp0_type, new0_lines = self.cast_expression(exp0, exp0_type, 'float')
            exp1, exp1_type, new1_lines = self.cast_expression(exp1, exp1_type, 'float')
            added_lines = added_lines + new0_lines + new1_lines
            if relop == '>=' or relop == '<=':
                # for these relops, take the first char in '<=/>=' and flip the attributes
                # then, preform not on the result
                return temp_var, added_lines + f'{self.float_op_dict.get(relop[0])} {temp_var} {exp1} {exp0}\n' \
                                               f'{self.float_op_dict.get("==")} {temp_var} {temp_var} {0}\n'
            return temp_var, added_lines + f'{self.float_op_dict.get(relop)} {temp_var} {exp0} {exp1}\n'

    def bin_op(self, op, left, left_type, right, right_type, added_lines):
        temp_var = self.gen_temp()
        if left_type == 'int' and right_type == 'int':
            return temp_var, 'int', added_lines + f'{self.int_op_dict.get(op)} {temp_var} {left} {right}\n'
        else:
            # cast int expression to float
            left, left_type, new0_lines = self.cast_expression(left, left_type, 'float')
            right, right_type, new1_lines = self.cast_expression(right, right_type, 'float')
            return temp_var, 'float', \
                added_lines + new0_lines + new1_lines + f'{self.float_op_dict.get(op)} {temp_var} {left} {right}\n'

    def walk_tree(self, node):
        # literals
        if isinstance(node, float):
            return node, 'float', ''
        elif isinstance(node, int):
            return node, 'int', ''
        elif isinstance(node, str):
            var_type = self.symbolTable.search(node)
            if var_type:
                return node, var_type, ''
            else:
                self.logger.error(f'ERROR: Using undefined symbol {node}!')
                self.success = False
                return '', '', ''

        elif node is None:
            return None

        # first node
        elif node[0] == 'program':
            return self.walk_tree(node[2]) + 'HALT\n' \
                                             'May Dekkers'

        # return id and num values
        elif node[0] == 'num':
            return self.walk_tree(node[1])

        elif node[0] == 'id':
            return self.walk_tree(node[1])

        elif node[0] == 'cast_expression':
            new_type = node[1]
            var, var_type, added_lines = self.walk_tree(node[2])
            var, new_type, new_lines = self.cast_expression(var, var_type, new_type)
            return var, new_type, added_lines + new_lines

        # operations:
        elif node[0] == '&&':
            boolterm, boolterm_lines = self.walk_tree(node[1])
            boolfactor, boolfactor_lines = self.walk_tree(node[2])
            added_lines = boolterm_lines + boolfactor_lines
            var = self.gen_temp()
            return var, added_lines + f'IMLT {var} {boolterm} {boolfactor}\n'
        elif node[0] == '||':
            boolexpr, boolexpr_lines = self.walk_tree(node[1])
            boolterm, boolterm_lines = self.walk_tree(node[2])
            added_lines = boolexpr_lines + boolterm_lines
            var = self.gen_temp()
            return var, added_lines + f'IADD {var} {boolexpr} {boolterm}\n'

        elif node[0] == 'not_boolexpr':  # returns the execution return value and the added code lines
            exp, added_lines = self.walk_tree(node[1])
            if exp.type == 'int':
                return exp, added_lines + f'IEQL {exp} {exp} 0\n'
            else:
                return exp, added_lines + f'REQL {exp} {exp} 0.0\n'

        elif node[0] == 'relop':
            relop = node[1]
            exp0, exp0_type, exp0_lines = self.walk_tree(node[2])
            exp1, exp1_type, exp1_lines = self.walk_tree(node[3])
            added_lines = exp0_lines + exp1_lines
            return self.rel_op(relop, exp0, exp0_type, exp1, exp1_type, added_lines)

        elif node[0] == 'addop' or node[0] == 'mulop':
            op = node[1]
            left, left_type, left_lines = self.walk_tree(node[2])
            right, right_type, right_lines = self.walk_tree(node[3])
            added_lines = left_lines + right_lines
            return self.bin_op(op, left, left_type, right, right_type, added_lines)

        # stmt:
        elif node[0] == 'stmtlist':
            stmts = ''
            for stmt in node[1]:
                stmts = stmts + self.walk_tree(stmt)
            return stmts

        elif node[0] == 'input_stmt':
            var, var_type, expr_lines = self.walk_tree(node[1])
            if var_type == 'float':
                return expr_lines + f'RINP {var}\n'
            elif var_type == 'int':
                return expr_lines + f'IINP {var}\n'

        elif node[0] == 'output_stmt':
            var, var_type, expr_lines = self.walk_tree(node[1])
            if var_type == 'float':
                return expr_lines + f'RPRT {var}\n'
            elif var_type == 'int':
                return expr_lines + f'IPRT {var}\n'

        elif node[0] == 'assignment_stmt':
            left, left_type, temp = self.walk_tree(node[1])
            right, right_type, expr_lines = self.walk_tree(node[2])
            if left_type == 'int' and right_type == 'int':
                return expr_lines + f'IASN {left} {right}\n'
            elif left_type == 'float' and right_type == 'float':
                return expr_lines + f'RASN {left} {right}\n'
            elif left_type == 'float' and right_type == 'int':
                new_right = self.gen_temp()
                return expr_lines + f'ITOR {new_right} {right}\n' + f'RASN {left} {new_right}\n'
            else:
                self.logger.error(f'ERROR: Cannot convert float to int!')
                self.success = False
                return ''

        elif node[0] == 'if_stmt':
            bool_var, bool_lines = self.walk_tree(node[1])
            stmt0 = self.walk_tree(node[2])
            stmt1 = self.walk_tree(node[3])
            first_label = self.gen_label()
            second_label = self.gen_label()
            if_stmt = bool_lines + f'JMPZ {first_label} {bool_var}\n' \
                                   f'{stmt0}' \
                                   f'JMP {second_label}\n' \
                                   f'{first_label}: {stmt1}' \
                                   f'{second_label}: '
            return if_stmt

        elif node[0] == 'while_stmt':
            bool_var, bool_lines = self.walk_tree(node[1])
            stmt = self.walk_tree(node[2])
            first_label = self.gen_label()
            second_label = self.gen_label()
            while_stmt = bool_lines + f'{first_label}: JMPZ {second_label} {bool_var}\n' \
                                      f'{stmt}' \
                                      f'JMP {first_label}\n' \
                                      f'{second_label}:'
            return while_stmt

        else:
            self.logger.error(f'ERROR: Encountered unexpected token {node[0]}')
            self.success = False
