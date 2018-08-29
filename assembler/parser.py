import pdb
import warnings
import functools

from assembler.utils import Utils, ManualCache


class Parser:
    """Encapsulates the access to input code.

    Reads and assembly language command, parses it, and provides convenient
    access to the command's components (fields and symbols). In addition,
    removes all white space and comments.

    The main function of the parser is to break each assembly command into
    its underlying components (fields and symbols).
    """
    command_type_cache = ManualCache(max_size=2048)
    clean_cache = ManualCache(max_size=2048)

    def __init__(self, file):
        """Opens the input file and gets ready to parse it.

        As opening a file is a trivial operation in Python ..
        I'm going to try and make this Parser behave like a file
        so I can do:
        with Parser('example_file) as p:
            for command in p:
                etc.
        """
        self.file = file
        self.command = None
        self.last_read_location = None

    def has_more_commands(self):
        """Are there more commands in the input?

        :rtype: bool

        Replacing do to non-python nature.
        Use try/except instead.
        """
        warnings.warn("The 'has_more_commands()' function is slow! Use the proper Python style instead.")
        return self.fd.readable() and self.last_read_location != self.fd.tell()

    def advance(self):
        """Reads the next command from input and makes it the current command.

        Should only be called if 'has_more_commands()' is true. Initially
        there is no current command.

        Replacing do to non-python nature.
        Use:
        with Parser(file) as p:
            for command in p:
        instead.
        """
        warnings.warn("The 'advance()' function is slow! Use the proper Python style instead.")
        if self.has_more_commands():
            self.last_read_location = self.fd.tell()
            command = self.fd.readline()
            self.command = command
            self.clean()

    def command_type(self):
        """Returns the type of the current command.

        :rtype: A_COMMAND, C_COMMAND, L_COMMAND

        A_COMMAND for @Xxx where Xxx is either a symbol or a decimal number.
        C_COMMAND for dest=comp;jump
        L_COMMAND for (actually pseudo for (Xxx) where Xxx is a symbol.
        """
        try:
            return Parser.command_type_cache[self.command]  # try for cached value
        except KeyError:
            pass
        if Utils.a_command.fullmatch(self.command):
            type_ = "A_COMMAND"
        elif Utils.c_command.fullmatch(self.command):
            type_ = "C_COMMAND"
        elif Utils.l_command.fullmatch(self.command):
            type_ = "L_COMMAND"
        else:
            type_ = None
        Parser.command_type_cache[self.command] = type_  # update cache
        return type_

    def symbol(self):
        """Returns the symbol or decimal Xxx of the current command.

        :rtype: str

        The current command being either @Xxx or (Xxx). Should be called only
        when 'command_type()' is A_COMMAND or L_COMMAND.
        """
        if self.command_type() == "A_COMMAND":
            return self.command[1:]
        elif self.command_type() == "L_COMMAND":
            return self.command[1:-1]
        raise Exception("Invalid 'command_type()'.")

    def dest(self):
        """Returns the 'dest' mnemonic in the current C-command.

        :rtype: str

        There are 8 possibilities.
        Should be called only when 'command_type()' is C_COMMAND.
        """
        if self.command_type() == "C_COMMAND":
            return self.command.split('=')[0] if "=" in self.command else "null"
        raise Exception("Invalid 'command_type()'.")

    def comp(self):
        """Returns the 'comp' mnemonic in the current C-command.

        :rtype: str

        There are 28 possibilities. Should be called only when
        'command_type()' is C_COMMAND.
        """
        if self.command_type() == "C_COMMAND":
            c = Utils.c_command_separators.split(self.command)
            size = len(c)
            if size == 1:
                return c[0]
            elif size == 2:
                if "=" in self.command:
                    return c[1]
                elif ";" in self.command:
                    return c[0]
            elif size == 3:
                return c[1]
        raise Exception("Invalid 'command_type()'.")

    def jump(self):
        """Returns the jump mnemonic in the current C-command.

        :rtype: str

        There are 8 possibilities. Should be called only when 'command_type()'
        is C_COMMAND.
        """
        if self.command_type() == "C_COMMAND":
            return self.command.split(';')[1] if ";" in self.command else "null"
        raise Exception("Invalid 'command_type()'.")

    def clean(self):
        """Remove all whitespace and comments from current line."""
        # pdb.set_trace()
        try:
            self.command = Parser.clean_cache[self.command]  # try for cached value
            return True
        except KeyError:
            pass
        line = self.command[:]
        line = line.split("//")[0]
        line = ''.join(line.split())
        Parser.clean_cache[self.command] = line  # update cache
        self.command = line

    def __enter__(self):
        self.fd = open(self.file, "r")
        return self  # or self.fd ..

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()

    def __iter__(self):
        """When used in a for loop returns file object.

        Maybe I should add line cleanup here too?
        """
        for line in self.fd:
            self.command = line
            self.clean()
            yield self.command
