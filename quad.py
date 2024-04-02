class Symbol:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return self.name + " " + self.type


class QuadCode:
    def __init__(self):
        self.symbol_table = []
        self.output = []

    def add_symbol(self, symbol: Symbol):
        if any(i.name == symbol.name for i in self.symbol_table):
            print("error")
        else:
            self.symbol_table.append(symbol)

    def add_line(self, line):
        self.output.append(line)
