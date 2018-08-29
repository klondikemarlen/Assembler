"""
Hack Assembler in Python
by: Marlen
"""
import pdb
import sys
import os
import re

COMP_CODES = {
      "0": "101010",
      "1": "111111",
     "-1": "111010",
      "D": "001100",
      "A": "110000",
     "!D": "001101",
     "!A": "110001",
     "-D": "001111",
     "-A": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "D+A": "000010",
    "D-A": "010011",
    "A-D": "000111",
    "D&A": "000000",
    "D|A": "010101"
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


class Assembler:
    def __init__(self):
        self.line_count = 0
        self.symbol_table = {}
        self.next_symbol = 16

    def convert_file(self, file):
        """Convert a file from Hack Assembly language to binary.

        Each binary instruction must be 16 bits long.
        Theoretically more than just the specified COMP_CODES are
        possible but this assembler doesn't handle them and throws an
        error.
        """

        debug_line_count = 1
        out_file = self.preparse_file(file)
        out_line = ""

        with open(file) as f:
            with open(out_file, "wb") as outf:
                for line in f:
                    clean_line = ASMTools.clean_line(line)
                    if clean_line and not ASMTools.is_label(clean_line):
                        try:
                            out_line = self.parse_line(clean_line)
                        except AssembleError as ex:
                            ex.add_debug_info(line, debug_line_count)
                            print(ex)
                            exit(1)
                        outf.write(out_line.encode())
                        outf.write(os.linesep.encode())
                    debug_line_count += 1

    def preparse_file(self, file):
        """Extract all the lables from the file.

        Add these to the local symbol table.
        """

        debug_line_count = 1
        path, filename = os.path.split(file)
        filename = str(filename)
        out_file = os.path.join(path, filename.rsplit('.')[0] + ".hack")

        with open(file, "r") as f:
            for line in f:
                line = ASMTools.clean_line(line)
                if ASMTools.is_label(line):
                    try:
                        self.parse_as_label(line)
                    except AssembleError as ex:
                        ex.add_debug_info(line, debug_line_count)
                        print(ex)
                        exit(1)
                elif line != "":
                    self.line_count += 1
                debug_line_count += 1
        return out_file

    def parse_as_label(self, line):
        """Parse (name) designations.

        This will throw an error if you use the same label in two places.
        """
        label = line[1:-1]
        ASMTools.check_if_valid_symbol(label)
        if label in self.symbol_table:
            print("Label '{}' occurs in 2 places!".format(label))
            raise Exception("You can't have the same label in more than one place!")
        self.symbol_table[label] = ASMTools.as_bin(self.line_count)

    def parse_line(self, line):
        """Convert the line into a 16 bit binary code.

        Line format is: ixxaccccccdddjjj
        """
        if line.startswith("@"):  # A-Instruction
            binary = self.parse_as_symbol(line)
        else:  # C-Instruction.
            binary = "111"
            dest, comp, jump = ASMTools.get_dest_comp_jump(line)

            # Set opcode bit.
            binary += "1" if "M" in comp else "0"

            # Both M and A codes are the same from here on.
            # So why not make all M's into A's and just deal with one of them?
            comp = comp.replace("M", "A")
            try:
                binary += COMP_CODES[comp]
            except KeyError:
                raise AssembleError(COMP_CODES, comp)
            try:
                binary += DEST_CODES[dest]
            except KeyError:
                raise AssembleError(DEST_CODES, dest)
            try:
                binary += JUMP_CODES[jump]
            except KeyError:
                raise AssembleError(JUMP_CODES, dest)
        return binary

    def parse_as_symbol(self, line):
        """Parse @name designations.

        This sequentially tries to to convert the symbol to binary,
        if that fails it tries to find it in the BUILTIN_SYMBOLS table,
        if that fails it tries to find it in the local symbol/label table,
        if that fails it create a new code starting from address 16.
        """
        symbol = line[1:]  # remove @ sign
        ASMTools.check_if_valid(symbol)
        try:
            binary = ASMTools.as_bin(symbol)
        except ValueError:
            try:
                binary = BUILTIN_SYMBOLS[symbol]
            except KeyError:
                try:
                    binary = self.symbol_table[symbol]
                except KeyError:
                    binary = ASMTools.as_bin(self.next_symbol)
                    self.symbol_table[symbol] = binary
                    self.next_symbol += 1
        return binary


class ASMTools:
    whitespace = re.compile("\s+")
    symbol = re.compile("[a-zA-Z_.$:][\w\d_.$:]*")
    constant = re.compile("[\d]*")
    bad_constant = re.compile("-|0[bBxX]+")

    @staticmethod
    def check_if_valid(symbol):
        """Check if the passed symbol is valid.

        Constants:
            Constants must be non-negative and are written in decimal
        notation.
        """
        if ASMTools.constant.fullmatch(symbol):
            return True
        try:
            ASMTools.check_if_valid_symbol(symbol)
        except AssembleError as ex:
            if ASMTools.bad_constant.match(symbol):
                raise AssembleError("Constants must be non-negative and written in decimal notation. A user-defined symbol can be any sequence of letters, digits, underscore (_), dot (.), dollar sign ($), and colon (:) that does not begin with a digit.", symbol, value_type="Constant or Symbol")
            raise

    @staticmethod
    def check_if_valid_symbol(symbol):
        """Check if passed symbol is valid.

        Symbols:
            A user-defined symbol can be any sequence of letters, digits,
        underscore (_), dot (.), dollar sign ($), and colon (:) that
        does not begin with a digit.
        """

        if ASMTools.symbol.fullmatch(symbol):
            return True
        else:
            raise AssembleError("A user-defined symbol can be any sequence of letters, digits, underscore (_), dot (.), dollar sign ($), and colon (:) that does not begin with a digit.", symbol, value_type="Symbol")

    @staticmethod
    def get_dest_comp_jump(line):
        """Break the line into its D, C and J codes.

        D -> Destination codes, before "=" sign, (optional)
        C -> Computation codes, after "=", before ";", MANDATORY
        J -> Jump codes, after ";" (optional)
        """
        dest, compjump = line.split('=') if "=" in line else ("null", line)
        comp, jump = compjump.split(';') if ";" in compjump else (compjump, "null")
        return dest, comp, jump

    @staticmethod
    def as_bin(x, size=16):
        """Convert x to a 16 bit zero padded binary number."""
        try:
            x = int(x)
        except ValueError as ex:
            raise ex
        return format(x, "b").zfill(size)

    @staticmethod
    def clean_line(line):
        """Remove comments and whitespace from line."""
        line = line.split("//")[0]
        line = line.strip()
        line = ''.join(ASMTools.whitespace.split(line))
        return line

    @staticmethod
    def is_label(line):
        """Return True if line is a Label.

        Assumes a 'cleaned' line.
        """
        return line and line.startswith("(") and line.endswith(")")


class AssembleError(Exception):
    def __init__(self, valid_values, value, value_type="statement",
                 debug_line_count="Unknown"):
        self.expression = value
        self.valid_values = valid_values
        self.debug_line_count = debug_line_count
        self.line = ""
        self.value_type = value_type
        self.message = "An error occurred on line {}. '{}' is not a valid {}.".format(self.debug_line_count, value, self.value_type)

    def add_debug_info(self, line, debug_line_count):
        self.line = line
        self.debug_line_count = debug_line_count

    def __str__(self):
        s = 'Error in line {}:\n\n{}\n'.format(self.debug_line_count, self.line)
        s += self.message
        s += "\nValid examples:\n"
        if isinstance(self.valid_values, dict):
            s += ', '.join([k for k in self.valid_values.keys()])
        else:
            s += self.valid_values
        return s


if __name__ == "__main__":
    asm = Assembler()
    # for n in range(16):
    #     print('"R{}", "{}",'.format(n, asm.as_bin(n)))

    if len(sys.argv) == 2:
        asm.convert_file(sys.argv[1])
    else:
        print("Try: python3 Assembler.py [somefile.asm]")
