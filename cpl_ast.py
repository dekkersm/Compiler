from quad import QuadCode, Symbol


out_code = QuadCode()


class Declaration:
    id_list: list[str]
    type: str

    def __init__(self, id_list, type):
        self.id_list = id_list
        self.type = type
        for i in id_list:
            out_code.add_symbol(Symbol(i, self.type))


class Declarations:
    dec_list: list[Declaration]

    def __init__(self, dec_list):
        self.dec_list = dec_list


class Program:
    def __init__(self):
        for i in out_code.symbol_table: print(i)
