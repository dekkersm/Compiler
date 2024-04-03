class SymTable:
    # Initialize a empty dictionary for storing identifiers
    def __init__(self):
        self.symbols = {}

    # Insert tokens into symbols dictionary
    def insert(self, token, type):
        self.symbols[token] = type

    def search(self, token):
        if token in self.symbols.keys():
            return self.symbols.get(token)
        return False
