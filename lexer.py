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
            'in', 'true', 'false']
operators = ['+', '-', '/', '//', '*', '%',
             'and', 'or', 'not', 'xor',
             '==', '<=', '>=', '!=', '<', '>',
             '^', '|', '&', '~',
             '=',
             '?']
delimiters = [';', ':', '{', '}', ',', '(', ')', '[', ']']
whitespace = [' ', '\n', '\t']


# class Token:
#     def __init__(self, num, value):
#         self.value = value
#         self.num = num

#     def __str__(self):
#         return f"TOKEN<{self.num}, {self.value}>"
        
# the lexer
class Lexer:
    def __init__(self, code):
        self.startPointer = 0
        self.searchPointer = 0
        self.tokens = []
        self.symbolTable = keywords+operators+delimiters
        # self.symbolTable = {
        #     "int": Token("KEYWORD", "int"),
        #     "float": Token("KEYWORD", "float"),
        #     "bool": Token("KEYWORD", "bool"),
        #     "string": Token("KEYWORD", "string"),
        #     "while": Token("KEYWORD", "while"),
        #     "for": Token("KEYWORD", "for"),
        #     "if": Token("KEYWORD", "if"),
        #     "else": Token("KEYWORD", "else"),
        #     "switch": Token("KEYWORD", "switch"),
        #     "default": Token("KEYWORD", "default"),
        #     "to": Token("KEYWORD", "to"),
        #     "in": Token("KEYWORD", "in"),
        #     "true": Token("KEYWORD", "true"),
        #     "false": Token("KEYWORD", "false"),
        #     "+": Token("PLUS_OP", "+"),
        #     }
        self.state = START
        self.code = code
    
    def lexer(self):
        while(self.searchPointer<len(self.code)):
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
                    self.tokens.append((self.symbolTable.index(currentChar), currentChar))
                    self.startPointer = self.searchPointer+1
                elif ws.match(currentChar):
                    self.startPointer = self.searchPointer+1
                elif currentChar=='#':
                    self.state = CMT
                elif ic.match(currentChar):
                    self.state = ERROR

            elif self.state == CMT:
                if currentChar != '\n':
                    self.state = CMT
                else:
                    self.state = START
                    self.startPointer = self.searchPointer+1

            elif self.state == ZERO:
                if currentChar == ".":
                    self.state = FLO_I
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar)  or currentChar == '#':
                    if '0' in self.symbolTable:
                        self.tokens.append((self.symbolTable.index('0'), '0')) # Taking the index if 0 is already recorded in the table
                    else:
                        self.tokens.append((len(self.symbolTable), '0')) # If it is the first time recording 0, then make a entry
                        self.symbolTable.append('0')
                    
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
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
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar)  or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    self.state = START
                    if  lexeme in self.symbolTable:
                        self.tokens.append((self.symbolTable.index(lexeme), lexeme)) # Taking the index if 0 is already recorded in the table
                    else:
                        self.tokens.append((len(self.symbolTable), lexeme)) # If it is the first time recording 0, then make a entry
                        self.symbolTable.append(lexeme)
                    
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
                        
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                else:
                    self.state = ERROR # If we encounter alphabets(Name error) or illegal characters(illegal character error)
            
            elif self.state == FLO_I:
                if d.match(currentChar) or z.match(currentChar):
                    self.state = FLO
                else:
                    self.state = ERROR
                    # Here we call this because 234.x x being anything other can number can make a illegal float literal error while the adjecent lexeme can be valid


            elif self.state == FLO:
                if z.match(currentChar) or d.match(currentChar):
                    pass
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar)  or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    if  lexeme in self.symbolTable:
                        self.tokens.append((self.symbolTable.index(lexeme), lexeme)) # Taking the index if 0 is already recorded in the table
                    else:
                        self.tokens.append((len(self.symbolTable), lexeme)) # If it is the first time recording 0, then make a entry
                        self.symbolTable.append(lexeme)
                    
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                else:
                    self.state = ERROR # If we encounter alphabets(Name error) or illegal characters(illegal character error)
                
            elif self.state == STR_I:
                if q.match(currentChar):
                    self.state = STR
                elif re.match('.', currentChar):
                    self.state = STR_I

            elif self.state == STR:
                if de.match(currentChar) or ws.match(currentChar) or op.match(currentChar)  or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    if  lexeme in self.symbolTable:
                        self.tokens.append((self.symbolTable.index(lexeme), lexeme)) # Taking the index if 0 is already recorded in the table
                    else:
                        self.tokens.append((len(self.symbolTable), lexeme)) # If it is the first time recording 0, then make a entry
                        self.symbolTable.append(lexeme)
                    
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                else:
                    self.state = ERROR # If we encounter alphabets(Name error) or illegal characters(illegal character error)
                

            elif self.state == ID:
                if a.match(currentChar) or d.match(currentChar) or z.match(currentChar):
                    self.state = ID
                elif de.match(currentChar) or ws.match(currentChar) or op.match(currentChar)  or currentChar == '#':
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    self.state = START
                    if  lexeme in self.symbolTable:
                        self.tokens.append((self.symbolTable.index(lexeme), lexeme)) # Taking the index if 0 is already recorded in the table
                    else:
                        self.tokens.append((len(self.symbolTable), lexeme)) # If it is the first time recording 0, then make a entry
                        self.symbolTable.append(lexeme)
                    
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
                        self.state = START
                    elif op.match(currentChar):
                        self.state = OP
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer + 1
                    if op.match(currentChar):
                        self.startPointer = self.searchPointer
                else:
                    self.state = ERROR # If we encounter illegal characters(illegal character error)
                
            elif self.state == OP:
                if op.match(currentChar):
                    self.state = OP
                # elif de.match(currentChar) or ws.match(currentChar) or currentChar == '#' or a.match(currentChar) or d.match(currentChar) or z.match(currentChar):
                elif ic.match(currentChar):
                    self.state = ERROR
                else:
                    lexeme = self.code[self.startPointer:self.searchPointer]
                    if  lexeme in self.symbolTable:
                        self.tokens.append((self.symbolTable.index(lexeme), lexeme)) 
                    else:
                        self.state = ERROR # Operators are already defined in symbol table. If not present, then it is a invalid lexeme
                    self.state = START
                    # Processing the break character
                    if de.match(currentChar):
                        self.tokens.append((self.symbolTable.index(currentChar), currentChar)) # Adding the delimiter as a token into the list
                    elif currentChar == '#':
                        self.state = CMT
                    self.startPointer = self.searchPointer 
                    self.searchPointer -= 1
            
            elif self.state == ERROR:
                if de.match(currentChar):
                    error_lexeme = self.code[self.startPointer:self.searchPointer]
                    self.tokens.append(("INVALID LEXEME", error_lexeme))
                    self.startPointer = self.searchPointer + 1
                    self.state = START
            
            self.searchPointer += 1

    # processing the input when input does not match the required regex
    # def processing(self):
    #     breakChar = self.code[self.searchPointer]
    #     if self.state == START:
    
    #     elif self.state in [INT, FLO, ID, ZERO, STR, OP]:
    #         if op.match(breakChar) or de.match(breakChar) or ws.match(breakChar):
    #             self.tokens.append((self.symbolTable.index(breakChar), self.code[self.startPointer:self.searchPointer]))
    #     else:
    #         self.errorGenerator()
    
    def errorGenerator(self):
        pass
    
# Parser
if __name__ == "__main__":
    path = sys.argv[1]
    file = open(path, 'r')
    code = file.read()
    lexerInstance = Lexer(code)
    lexerInstance.lexer()

    for token in lexerInstance.tokens:
        print(token)