import pdb
import sys
import os

from assembler.parser import Parser
from assembler.code import Code
from assembler.symbol_table import SymbolTable

if len(sys.argv) < 2:
    exit("You need to pass in a file name to be Assembled.")
file = sys.argv[1]
out_file = file.rsplit(".")[0] + ".hack"

sym_table = SymbolTable()
address = 0
with Parser(file) as p:
    # pdb.set_trace()
    for command in p:
        if command:
            command_type = p.command_type()
            if command_type == "L_COMMAND":
                sym_table.add_entry(p.symbol(), address)
            if command_type in ("A_COMMAND", "C_COMMAND"):
                address += 1

next_symbol = 16
debug_line_count = 1
binary = ''
with Parser(file) as p:
    with open(out_file, 'w') as out_f:
        # pdb.set_trace()
        for command in p:
            if command:
                # format is: ixxaccccccdddjjj.
                command_type = p.command_type()
                if command_type == "A_COMMAND":
                    symbol = p.symbol()
                    try:
                        binary = Code.symbol(symbol)
                    except KeyError:
                        if sym_table.contains(symbol):
                            symbol = sym_table.get_address(symbol)
                        try:
                            binary = Code.as_bin(symbol)
                        except ValueError:
                            sym_table.add_entry(symbol, next_symbol)
                            binary = Code.as_bin(next_symbol)
                            next_symbol += 1
                elif command_type == "C_COMMAND":
                    comp = Code.comp(p.comp())
                    dest = Code.dest(p.dest())
                    jump = Code.jump(p.jump())
                    a_bit = "1" if "M" in p.comp() else "0"
                    binary = "111" + a_bit + comp + dest + jump
                elif command_type == "L_COMMAND":
                    debug_line_count += 1  # still need to increment debug counter
                    continue
                else:
                    pdb.set_trace()
                    raise Exception("Messed up binary code.")
                out_f.write(binary)
                out_f.write(os.linesep)
            debug_line_count += 1

# print(Parser.command_type_cache)
# print(Parser.clean_cache)
