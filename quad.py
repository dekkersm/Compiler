import string
from random import choices


class QuadCode:
    int_relop_dict = {'==':'IEQL',
                      '!=':'INQL',
                      '>=':'ILSS!!!!!',
                      '<=':'IGRT!!!!!',
                      '<':'ILSS',
                      '>':'IGRT'}

    float_relop_dict = {'==':'REQL',
                      '!=':'RNQL',
                      '>=':'ILSS!!!!!',
                      '<=':'IGRT!!!!!',
                      '<':'RLSS',
                      '>':'RGRT'}

    def __init__(self, tree, symbol_table):
        self.label_count = 0
        self.symbolTable = symbol_table
        self.output = []
        self.walk_tree(tree)
        self.format_output()

    def format_output(self):
        for line in self.output:
            print(line)
        print('HALT')

    def write_line(self, line):
        self.output.append(line)

    def create_label(self) -> str:
        self.label_count = self.label_count + 1
        return '$L' + str(self.label_count)

    def create_temp(self) -> str:
        return '$' + ''.join(choices(string.ascii_lowercase + string.digits, k=4))

    def walk_tree(self, node):
        # literals
        if isinstance(node, float):
            return node, 'float'
        elif isinstance(node, int):
            return node, 'int'
        elif isinstance(node, str):
            var_type = self.symbolTable.search(node)
            if var_type:
                return node, var_type
            else:
                print('ERROR')

        elif node is None:
            return None

        # first node
        elif node[0] == 'program':
            return self.walk_tree(node[2])

        # return id and num values
        elif node[0] == 'num':
            return self.walk_tree(node[1])

        elif node[0] == 'id':
            return self.walk_tree(node[1])

        elif node[0] == 'cast_expression':
            new_type = self.walk_tree(node[1])
            var_type = self.walk_tree(node[2])
            # do nothing if equal
            if not new_type == var_type:
                new_var = self.create_temp()

        # operations
        elif node[0] == '&&':
            boolterm = self.walk_tree(node[1])
            boolfactor = self.walk_tree(node[2])
        elif node[0] == '||':
            boolexpr = self.walk_tree(node[1])
            boolterm = self.walk_tree(node[2])
        elif node[0] == 'not_boolexpr':  # returns tuple(temp_var, type)
            exp = self.walk_tree(node[1])
            temp_var = self.create_temp()
            if exp.type == 'int':
                return f'IEQL {temp_var} {exp} 0'
            else:
                return f'REQL {temp_var} {exp} 0.0'
        elif node[0] == 'relop':  # returns tuple(temp_var, type)
            relop = node[1]
            exp0, exp0_type = self.walk_tree(node[2])
            exp1, exp1_type = self.walk_tree(node[3])
            temp_var = self.create_temp()
            if exp0_type == 'int' and exp1_type == 'int':
                self.write_line(f'{self.int_relop_dict.get(relop)} {temp_var} {exp0} {exp1}')
                return temp_var, 'int'
            else:
                # cast int expression to float
                if exp0_type == 'int':
                    old_exp = exp0
                    exp0 = self.create_temp()
                    self.write_line(f'ITOR {exp0} {old_exp}')
                elif exp1_type == 'int':
                    old_exp = exp1
                    exp1 = self.create_temp()
                    self.write_line(f'ITOR {exp1} {old_exp}')
                self.write_line(f'{self.float_relop_dict.get(relop)} {temp_var} {exp0} {exp1}')
                return temp_var, 'float'
        elif node[0] == 'addop':
            addop = node[1]
            left = self.walk_tree(node[1])
            right = self.walk_tree(node[2])
        elif node[0] == 'mulop':
            mulop = node[1]
            left = self.walk_tree(node[1])
            right = self.walk_tree(node[2])

        # stmt:
        elif node[0] == 'stmtlist':
            for stmt in node[1]:
                self.write_line(self.walk_tree(stmt))

        elif node[0] == 'input_stmt':
            var, var_type = self.walk_tree(node[1])
            if var_type == 'float':
                return f'RINP {var}'
            elif var_type == 'int':
                return f'IINP {var}'

        elif node[0] == 'output_stmt':
            var, var_type = self.walk_tree(node[1])
            if var_type == 'float':
                return f'RPRT {var}'
            elif var_type == 'int':
                return f'IPRT {var}'

        elif node[0] == 'assignment_stmt':
            left, left_type = self.walk_tree(node[1])
            right, right_type = self.walk_tree(node[2])
            if left_type == 'int' and right_type == 'int':
                return f'IASN {left} {right}'
            elif left_type == 'float' and right_type == 'float':
                return f'RASN {left} {right}'
            elif left_type == 'float' and right_type == 'int':
                new_right = self.create_temp()
                return f'ITOR {new_right} {right}' \
                       f'RASN {left} {new_right}'
            else:
                print('ERROR')

        elif node[0] == 'if_stmt':
            bool_var, bool_type = self.walk_tree(node[1])
            stmt0 = self.walk_tree(node[2])
            stmt1 = self.walk_tree(node[3])
            first_label = self.create_label()
            second_label = self.create_label()
            if_stmt = f'JMPZ {first_label} {bool_var}\n' \
                      f'{stmt0}\n' \
                      f'JMP {second_label}\n' \
                      f'{first_label}: {stmt1}\n' \
                      f'{second_label}:'
            return if_stmt

        elif node[0] == 'while_stmt':
            var = self.walk_tree(node[1])
            var_type = self.symbolTable.search(var)
            exp_type = self.walk_tree(node[2])