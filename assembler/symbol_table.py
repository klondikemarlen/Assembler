class SymbolTable:
    """Keeps a correspondence between symbolic labels an numeric addresses."""

    def __init__(self):
        """Create a new empty symbol table."""
        self.table = {}

    def add_entry(self, symbol, address):
        """Adds the pair (symbol, address) to the table."""
        self.table[symbol] = address

    def contains(self, symbol):
        """Does the symbol table contain the given symbol?

        :rtype: bool
        """
        return symbol in self.table

    def get_address(self, symbol):
        """Return the address associated with the symbol.

        :rtype: int
        """

        return self.table[symbol]
