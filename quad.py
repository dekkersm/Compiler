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

        self.code = self.walk_tree(tree)
        print(self.code)

    def create_file(self, path):
        self.code = textwrap.indent(self.code, 5 * ' ', lambda line: ':' not in line)
        with open(path, 'w') as f:
            f.writelines(self.code)

    def gen_label(self) -> str:
        self.label_count = self.label_count + 1
        return '$L' + str(self.label_count)

    def gen_temp(self) -> str:
        self.temp_count = self.temp_count + 1
        return '$temp' + str(self.temp_count)

    def rel_op(self, relop, exp0, exp0_type, exp1, exp1_type, added_lines):
        # TODO: handle >= and <=
        temp_var = self.gen_temp()
        if exp0_type == 'int' and exp1_type == 'int':
            if relop == '>=' or relop == '<=':
                relop = relop[0]
            return temp_var, added_lines + f'{self.int_op_dict.get(relop)} {temp_var} {exp0} {exp1}\n'
        else:
            # cast int expression to float
            if exp0_type == 'int':
                old_exp = exp0
                exp0 = self.gen_temp()
                added_lines = added_lines + f'ITOR {exp0} {old_exp}\n'
            elif exp1_type == 'int':
                old_exp = exp1
                exp1 = self.gen_temp()
                added_lines = added_lines + f'ITOR {exp1} {old_exp}\n'
            return temp_var, added_lines + f'{self.float_op_dict.get(relop)} {temp_var} {exp0} {exp1}\n'

    def bin_op(self, op, left, left_type, right, right_type, added_lines):
        temp_var = self.gen_temp()
        if left_type == 'int' and right_type == 'int':
            return temp_var, 'int', added_lines + f'{self.int_op_dict.get(op)} {temp_var} {left} {right}\n'
        else:
            # cast int expression to float
            if left_type == 'int':
                old_exp = left
                left = self.gen_temp()
                added_lines = added_lines + f'ITOR {left} {old_exp}\n'
            elif right_type == 'int':
                old_exp = right
                right = self.gen_temp()
                added_lines = added_lines + f'ITOR {right} {old_exp}\n'
            return temp_var, 'float', added_lines + f'{self.float_op_dict.get(op)} {temp_var} {left} {right}\n'

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
                print('ERROR')

        elif node is None:
            return None

        # first node
        elif node[0] == 'program':
            return self.walk_tree(node[2]) + 'HALT'

        # return id and num values
        elif node[0] == 'num':
            return self.walk_tree(node[1])

        elif node[0] == 'id':
            return self.walk_tree(node[1])

        elif node[0] == 'cast_expression':
            new_type = node[1]
            var, var_type, added_lines = self.walk_tree(node[2])
            # do nothing if equal
            if not new_type == var_type:
                old_var = var
                var = self.gen_temp()
                if new_type == 'float':
                    added_lines = added_lines + f'ITOR {var} {old_var}\n'
                else:
                    added_lines = added_lines + f'RTOI {var} {old_var}\n'
            return var, new_type, added_lines

        # operations
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

        elif node[0] == 'not_boolexpr':  # returns temp_var
            exp, added_lines = self.walk_tree(node[1])
            temp_var = self.gen_temp()
            if exp.type == 'int':
                return temp_var, added_lines + f'IEQL {temp_var} {exp} 0\n'
            else:
                return temp_var, added_lines + f'REQL {temp_var} {exp} 0.0\n'

        elif node[0] == 'relop':  # returns temp_var
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
                print('ERROR')

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
            print('error')
