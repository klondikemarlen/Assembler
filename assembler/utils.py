import re


class Utils:
    """Helpful utilities for Assembler.

    These might be used in multiple modules.
    """
    comment = re.compile(r"\\")
    whitespace = re.compile("\s+")
    symbol = re.compile("[a-zA-Z_.$:][\w\d_.$:]*")
    constant = re.compile("[\d]*")
    bad_constant = re.compile("-|0[bBxX]+")
    a_command = re.compile("@({}|{})".format(symbol.pattern, constant.pattern))
    dest = re.compile("\w+")  # could be more specific
    comp = re.compile("[!\w+\-&|]+")  # could be more specific
    jump = re.compile("\w+")  # could be more specific
    c_command = re.compile("{c}|{c};{j}|{d}={c}|{d}={c};{j}".format(d=dest.pattern, c=comp.pattern, j=jump.pattern))
    c_command_separators = re.compile("[;=]")
    l_command = re.compile("\({}\)".format(symbol.pattern))


class ManualCache:
    def __init__(self, max_size=None):
        self.cache = {}
        # self.hit_table = {}
        self.hits = 0
        self.misses = 0
        self.maxsize = max_size

    @property
    def currsize(self):
        return len(self.cache)

    def __getitem__(self, item):
        try:
            value = self.cache[item]
            # self.hit_table[item] += 1
            self.hits += 1
            return value
        except KeyError:
            self.misses += 1
            raise

    def __setitem__(self, key, value):
        if self.maxsize is None or self.currsize <= self.maxsize:
            self.cache[key] = value
            # self.hit_table[key] = 0
        # If over maxsize just stop storing stuff.

        # else:  # delete a random 0 hit key
            # for k, v in self.cache.items():
            #     if v == 0:
            #         del self.cache[key]
            #         break
    def __repr__(self):
        return repr(self.cache) + "\n" + str(self)

    def __str__(self):
        return self.cache_info()

    def cache_info(self):
        """Should print out data like lru_cache builtin.

        e.g. CacheInfo(hits=3, misses=8, maxsize=32, currsize=8)
        """
        return "CacheInfo(hits={}, misses={}, maxsize={}, currsize={})".format(self.hits, self.misses, self.maxsize, self.currsize)


if __name__ == "__main__":
    # print(Utils.a_command.pattern)
    # print(repr(Utils.a_command.fullmatch("@Help")))
    assert Utils.a_command.fullmatch("@Help") is not None
    assert Utils.a_command.fullmatch("@125") is not None
    assert Utils.a_command.fullmatch("@1Help") is None
    assert Utils.a_command.fullmatch("@-124") is None

    # print(Utils.c_command.pattern)
    assert Utils.c_command.fullmatch("A=M") is not None
    assert Utils.c_command.fullmatch("A=D;JMP") is not None
    assert Utils.c_command.fullmatch("A=D|M;JMP") is not None
    assert Utils.c_command.fullmatch("A;JMP") is not None
    assert Utils.c_command.fullmatch("D;JMP") is not None
    assert Utils.c_command.fullmatch("A") is not None
    assert Utils.c_command.fullmatch("!A") is not None
    assert Utils.c_command.fullmatch("D=D+A") is not None
    assert Utils.c_command.fullmatch("M|D|A") is not None  # future use?
    assert Utils.c_command.fullmatch("A;") is None
    assert Utils.c_command.fullmatch("=A") is None
    assert Utils.c_command.fullmatch("=A;") is None

    # print(Utils.l_command.pattern)
    assert Utils.l_command.fullmatch("(TEST)") is not None
    assert Utils.l_command.fullmatch("(A)") is not None
    assert Utils.l_command.fullmatch("(A32)") is not None
    assert Utils.l_command.fullmatch("(25Hel)") is None
    assert Utils.l_command.fullmatch("(TEST") is None

    assert Utils.c_command_separators.split("a=d;jmp") == ['a', 'd', 'jmp']
