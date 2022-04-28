import sys
import warnings
import pandas as pd

from lexer import *
from node import *

warnings.filterwarnings('ignore')

if __name__ == "__main__":

    path = sys.argv[1]
    file = open(path, 'r')

    # reading the code file
    code = file.read()

    # lexical analysis
    lexerInstance = Lexer(code)
    lexerInstance.lexer()

    # reading grammar file
    grammar_file = open("./resources/grammar.txt", "r")
    grammar_string = grammar_file.read()
    grammar_file.close()
    grammar_string = grammar_string.split('\n')
    # print(grammar_string)
    grammar = [rule.split(' ') for rule in grammar_string]
    grammar = [rule[:1]+rule[2:] for rule in grammar]
    # for rule in grammar:
    #     print(rule)

    # reading parse table from excel file into pandas dataframe object
    parse_table_df = pd.read_excel("./resources/parse-table.xlsx")
    parse_table_df.set_index('Nonterminal', inplace=True)

    # list terminals and non-terminals
    terminals = parse_table_df.columns
    non_terminals = parse_table_df.index.dropna()

    # enumerating the grammar rules for parse table
    for nt in non_terminals:
        for t in terminals:
            if not isinstance(parse_table_df[t][nt], str):
                parse_table_df[t][nt] = -1
            else:
                parse_table_df[t][nt] = grammar_string.index(
                    parse_table_df[t][nt])
    # print(parse_table_df)

    # Modification of parse table to handle errors
    follow_sets_df = pd.read_excel("./resources/followSets.xlsx")
    follow_sets_df.set_index('Nonterminal', inplace=True)

    # print(follow_sets_df)
    for nt in non_terminals:
        follow_set_string = follow_sets_df['FOLLOW'][nt][1:-1]
        follow_set = follow_set_string.split(",")
        if follow_set_string[-1] == ',' or follow_set_string[0] == ',':
            follow_set.append(',')
        follow_set = [item for item in follow_set if item != '']

        for t in follow_set:
            if parse_table_df[t][nt] == -1:
                parse_table_df[t][nt] = -2

    # print(parse_table_df)

    # base node of parse tree
    baseNode = Node(nodeType='non-terminal', value='PROGRAM')

    # stack and input tape for the parser
    stack = [Node(nodeType='terminal', value='$'), baseNode]
    input_tape = []

    # print(f'number of tokens: {len(lexerInstance.tokens)}')

    # populate the input tape with input tokens
    for token in lexerInstance.tokens:
        if token[1] in keywords+delimiters:
            input_tape.append(token[1])
        elif token[1] in bops:
            input_tape.append('bop')
        elif token[1] in uops:
            input_tape.append('uop')
        elif token[1].isnumeric():
            input_tape.append('number')
        elif token[1] in lexerInstance.symbolTable:
            input_tape.append('id')

    input_tape.append('$')

    # print(f'length of input tape: {len(input_tape)}')
    # print(f'input tape: {input_tape}')
    errorFlag = 0
    print(f'input tape: {input_tape}\nstack: {stack}\n---')
    print('\t\tPARSING PROCESS:')
    # parsing the input tape
    while len(input_tape) != 0:
        if stack[-1].value in terminals:
            print('stack top is a terminal')
            if stack[-1].value == input_tape[0]:
                stack.pop()
                input_tape.pop(0)
            else:
                print('Error: non-matching terminals')
                errorFlag += 1
                stack.pop()
        else:
            rule = parse_table_df[input_tape[0]][stack[-1].value]
            print(f'reducing non-terminal')
            if rule < 0:
                print('Error: ', end="")
                errorFlag += 1
                if rule == -1:
                    input_tape.pop(0)
                    print("Skipping a token in input")
                else:
                    stack.pop()
                    print("Popping the stack.")
            else:
                print(f'rule used: {grammar_string[rule]}')
                if grammar[rule][1] == "''":
                    stack.pop()
                else:
                    children = grammar[rule][1:]
                    stack_append = []
                    for value in children:
                        if value in terminals:
                            stack_append.append(
                                Node(nodeType='terminal', value=value))
                        elif value in non_terminals:
                            stack_append.append(
                                Node(nodeType='non-terminal', value=value))
                    stack[-1].children = stack_append
                    stack = stack[:-1] + stack_append[::-1]
        print(f'input tape: {input_tape}\nstack: {stack}\n---')

    if (len(stack) == 0) and (len(input_tape) == 0) and errorFlag == 0:
        print('parsing complete. string accepted.\n---')
    else:
        print("Errors encountered ")

    # print the parse tree
    print('\t\tPARSE TREE:')
    current_level = [baseNode]
    next_level = []
    print([baseNode])
    while True:
        for node in current_level:
            print(node.children, end=' ')
            next_level += node.children
        print()
        current_level = next_level
        next_level = []
        if len(current_level) == 0:
            break
