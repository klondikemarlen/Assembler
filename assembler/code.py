COMP_CODES = {
      "0": "101010",
      "1": "111111",
     "-1": "111010",
      "D": "001100",
      "A": "110000",
      "M": "110000",
     "!D": "001101",
     "!A": "110001",
     "!M": "110001",
     "-D": "001111",
     "-A": "110011",
     "-M": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "M+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "M-1": "110010",
    "D+A": "000010",
    "D+M": "000010",
    "D-A": "010011",
    "D-M": "010011",
    "A-D": "000111",
    "M-D": "000111",
    "D&A": "000000",
    "D&M": "000000",
    "D|A": "010101",
    "D|M": "010101"
}

DEST_CODES = {
    "null": "000",
       "M": "001",
       "D": "010",
      "MD": "011",
       "A": "100",
      "AM": "101",
      "AD": "110",
     "AMD": "111"
}

JUMP_CODES = {
    "null": "000",
     "JGT": "001",
     "JEQ": "010",
     "JGE": "011",
     "JLT": "100",
     "JNE": "101",
     "JLE": "110",
     "JMP": "111"
}

BUILTIN_SYMBOLS = {
    "R0":      "0000000000000000",
    "R1":      "0000000000000001",
    "R2":      "0000000000000010",
    "R3":      "0000000000000011",
    "R4":      "0000000000000100",
    "R5":      "0000000000000101",
    "R6":      "0000000000000110",
    "R7":      "0000000000000111",
    "R8":      "0000000000001000",
    "R9":      "0000000000001001",
    "R10":     "0000000000001010",
    "R11":     "0000000000001011",
    "R12":     "0000000000001100",
    "R13":     "0000000000001101",
    "R14":     "0000000000001110",
    "R15":     "0000000000001111",
    "SCREEN":  "0100000000000000",  # 0x4000
    "KBD":     "0110000000000000",  # 0x6000
    "SP":      "0000000000000000",
    "LCL":     "0000000000000001",
    "ARG":     "0000000000000010",
    "THIS":    "0000000000000011",
    "THAT":    "0000000000000100",
}


class Code:
    """Translate Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic):
        """Returns the binary code of the 'dest' mnemonic.

        :returns 3 bits
        """
        return DEST_CODES[mnemonic]

    @staticmethod
    def comp(mnemonic):
        """Returns the binary code of the 'comp' mnemonic.

        :returns 7 bits
        """
        return COMP_CODES[mnemonic]

    @staticmethod
    def jump(mnemonic):
        """Returns the binary code of the 'jump' mnemonic.

        :returns 3 bits
        """
        return JUMP_CODES[mnemonic]

    @staticmethod
    def symbol(mnemonic):
        return BUILTIN_SYMBOLS[mnemonic]

    @staticmethod
    def as_bin(x, size=16):
        """Convert x to a 16 bit zero padded binary number."""
        try:
            x = int(x)
        except ValueError as ex:
            raise ex
        return format(x, "b").zfill(size)
