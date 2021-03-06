import re
import sys

# regex for character groups
a = re.compile("[a-zA-Z_]")
d = re.compile('[1-9]')
z = re.compile('0')
op = re.compile('[+\-*/%=<>!^|&~?]')
ic = re.compile('[$@\`]')
ws = re.compile("[\\n\\t ]")
de = re.compile('[;:{},\(\)\[\]]')
q = re.compile('["\']')

# state map
START = 'start_state'
DE = 'delimiter'
ID = 'identifier'

CMT = 'comment'

OP = 'operator'

STR = 'string_literal'
STR_I = 'string_intermediate'

INT = 'integer_literal'

FLO = 'floating_point_literal'
FLO_I = 'floating_intermediate'

ZERO = "zero_literal"

ERROR = "error_state"

# Reserved items for symbol table
keywords = ['int', 'float', 'boolean', 'string',
            'while', 'for', 'if', 'else', 'switch', 'to', 'default',
            'in', 'true', 'false', '=', 'fn', 'do']
bops = ['+', '-', '/', '//', '*', '%',
             'and', 'or', 'xor',
             '==', '<=', '>=', '!=', '<', '>',
             '^', '|', '&',
             '+=', '-=', '*=', '/=', '%=',
             '?']
uops = ['++', '--', 'not', '~']
operators = ['+', '-', '/', '//', '*', '%',
             'and', 'or', 'not', 'xor',
             '==', '<=', '>=', '!=', '<', '>',
             '^', '|', '&', '~',
             '+=', '-=', '*=', '/=', '%=', '=',
             '++', '--',
             '?']
delimiters = [';', ':', '{', '}', ',', '(', ')', '[', ']']
whitespace = [' ', '\n', '\t']


# the lexer
class Lexer:
    def __init__(self, code):
        self.startPointer = 0
        self.searchPointer = 0
        self.tokens = []
        self.symbolTable = keywords+operators+delimiters
        self.state = START
        self.code = code
        self.lineNumber = 1

    def lexer(self):
        while(self.searchPointer < len(self.code)):
            currentChar = self.code[self.searchPointer]

            if self.state == START:
                if a.match(currentChar):
                    self.state = ID
                elif q.match(currentChar):
                    self.state = STR_I
                elif d.match(currentChar):
                    self.state = INT
                elif z.match(currentChar):
                    self.state = ZERO
                elif currentChar == '.':
                    self.state = FLO_I
                elif op.match(currentChar):
                    self.state = OP
                elif de.match(currentChar):
                    self.tokens.append(
                        (self.symbolTable.index(currentChar), currentChar, self.lineNumber))
                    self.startPointer = self.searchPointer+1
                elif ws.match(currentChar):
                    self.startPointer = self.searchPointer+1
                    if currentChar == '\n':
                        self.lineNumber += 1
                elif currentChar == '#':
                    self.state = CMT
                elif ic.match(currentChar):
                    self.state = ERROR

            elif self.state == CMT:
                if currentChar != '\n':
                    self.state = CMT
                else:
                    self.state = START
                    self.startPointer = self.searchPointer+1
                    self.lineNumber += 1

            elif self.state == ZERO:
                if currentChar == ".":
                    self.state = FLO_I
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar) or currentChar == '#':
                    if '0' in self.symbolTable:
                        # Taking the index if 0 is already recorded in the table
                        self.tokens.append(
                            (self.symbolTable.index('0'), '0', self.lineNumber))
                    else:
                        # If it is the first time recording 0, then make a entry
                        self.tokens.append(
                            (len(self.symbolTable), '0', self.lineNumber))
                        self.symbolTable.append('0')

                    # Processing the break character
                    if de.match(currentChar):
                        # Adding the delimiter as a token into the list
                        self.tokens.append(
                            (self.symbolTable.index(currentChar), currentChar, self.lineNumber))
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1

                # else:
                #     self.errorGenerator() # If we encounter alphabets(Name error) or illegal characters(illegal character error)

            elif self.state == INT:
                if z.match(currentChar) or d.match(currentChar):
                    pass
                elif currentChar == '.':
                    self.state = FLO_I
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar) or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    self.state = START
                    if lexeme in self.symbolTable:
                        # Taking the index if 0 is already recorded in the table
                        self.tokens.append(
                            (self.symbolTable.index(lexeme), lexeme, self.lineNumber))
                    else:
                        # If it is the first time recording 0, then make a entry
                        self.tokens.append(
                            (len(self.symbolTable), lexeme, self.lineNumber))
                        self.symbolTable.append(lexeme)

                    # Processing the break character
                    if de.match(currentChar):
                        # Adding the delimiter as a token into the list
                        self.tokens.append(
                            (self.symbolTable.index(currentChar), currentChar, self.lineNumber))

                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                else:
                    # If we encounter alphabets(Name error) or illegal characters(illegal character error)
                    self.state = ERROR

            elif self.state == FLO_I:
                if d.match(currentChar) or z.match(currentChar):
                    self.state = FLO
                else:
                    self.state = ERROR
                    # Here we call this because 234.x x being anything other can number can make a illegal float literal error while the adjecent lexeme can be valid

            elif self.state == FLO:
                if z.match(currentChar) or d.match(currentChar):
                    pass
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar) or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    if lexeme in self.symbolTable:
                        # Taking the index if 0 is already recorded in the table
                        self.tokens.append(
                            (self.symbolTable.index(lexeme), lexeme))
                    else:
                        # If it is the first time recording 0, then make a entry
                        self.tokens.append(
                            (len(self.symbolTable), lexeme, self.lineNumber))
                        self.symbolTable.append(lexeme)

                    # Processing the break character
                    if de.match(currentChar):
                        # Adding the delimiter as a token into the list
                        self.tokens.append(
                            (self.symbolTable.index(currentChar), currentChar, self.lineNumber))
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                else:
                    # If we encounter alphabets(Name error) or illegal characters(illegal character error)
                    self.state = ERROR

            elif self.state == STR_I:
                if q.match(currentChar):
                    self.state = STR
                elif re.match('.', currentChar):
                    self.state = STR_I

            elif self.state == STR:
                if de.match(currentChar) or ws.match(currentChar) or op.match(currentChar) or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    if lexeme in self.symbolTable:
                        # Taking the index if 0 is already recorded in the table
                        self.tokens.append(
                            (self.symbolTable.index(lexeme), lexeme, self.lineNumber))
                    else:
                        # If it is the first time recording 0, then make a entry
                        self.tokens.append(
                            (len(self.symbolTable), lexeme, self.lineNumber))
                        self.symbolTable.append(lexeme)

                    # Processing the break character
                    if de.match(currentChar):
                        # Adding the delimiter as a token into the list
                        self.tokens.append(
                            (self.symbolTable.index(currentChar), currentChar, self.lineNumber))
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    if op.match(currentChar):
                        self.startPointer = self.searchPointer
                    else:
                        self.startPointer = self.searchPointer + 1
                else:
                    # If we encounter alphabets(Name error) or illegal characters(illegal character error)
                    self.state = ERROR

            elif self.state == ID:
                if a.match(currentChar) or d.match(currentChar) or z.match(currentChar):
                    self.state = ID
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar) or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    self.state = START
                    if lexeme in self.symbolTable:
                        # Taking the index if 0 is already recorded in the table
                        self.tokens.append(
                            (self.symbolTable.index(lexeme), lexeme, self.lineNumber))
                    else:
                        # If it is the first time recording 0, then make a entry
                        self.tokens.append(
                            (len(self.symbolTable), lexeme, self.lineNumber))
                        self.symbolTable.append(lexeme)

                    # Processing the break character
                    if de.match(currentChar):
                        # Adding the delimiter as a token into the list
                        self.tokens.append(
                            (self.symbolTable.index(currentChar), currentChar, self.lineNumber))
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                    if op.match(currentChar):
                        self.startPointer = self.searchPointer
                else:
                    # If we encounter illegal characters(illegal character error)
                    self.state = ERROR

            elif self.state == OP:
                if op.match(currentChar):
                    self.state = OP
                elif ic.match(currentChar):
                    self.state = ERROR
                else:
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    self.state = START
                    if lexeme in self.symbolTable:
                        self.tokens.append(
                            (self.symbolTable.index(lexeme), lexeme, self.lineNumber))
                    else:
                        i = 0
                        while i < len(lexeme):
                            if lexeme[i:i+2] in operators:
                                self.tokens.append(
                                    (self.symbolTable.index(lexeme[i:i+2]), lexeme[i:i+2], self.lineNumber))
                                i += 2
                            else:
                                self.tokens.append(
                                    (self.symbolTable.index(lexeme[i]), lexeme[i], self.lineNumber))
                                i += 1

                    if currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer
                    self.searchPointer -= 1

            elif self.state == ERROR:
                if currentChar == ';' or currentChar == '\n':
                    error_lexeme = self.code[self.startPointer:self.searchPointer+1]
                    self.tokens.append(
                        ("INVALID LEXEME", error_lexeme, self.lineNumber))
                    self.startPointer = self.searchPointer + 1
                    self.state = START

            self.searchPointer += 1

    def errorGenerator(self):
        pass
