# DogeLang

## Project Description
This project implements a basic front end compiler for a imperative langauge with basic constructs including looping, conditional and functional constructs.

> For language implementational details, check [test cases](./test-cases/) and [resources](./resources/).

## How the compiler works
1. The input program code is first tokenized using [lexer](./lexer.py) (lexical analysis) written in python.
2. This was developed by generating a Deterministic Finite Automata ([DFA](./resources/lexer-DFA.pdf)) for the langauge. The DFA is converted into a working program using if-else conructs. Refer to code for futher details.
3. The tokenized programme(in the form of a list) is given to the [parser](./parser.py) which carries out syntax analysis.
4. The parser we have used is an LL(1) topdown parser, it uses our [CFG](./resources/grammar.txt) and [parse-table](./resources/parse-table.xlsx) (check credits for the website) do syntax analysis and build the parse tree.
5. The parser is also capable of detecting errors and take appropriate action to move forward with the parsing process rather than halting at that point of the program.

## How to run the project
- Clone the repository onto your local machine.
- To run the compiler on your own file <br>
Windows: `python parser.py [location of the file to run the compiler on]`<br>
Ubuntu: `python3 parser.py [location of the file to run the compiler on]`

## Credits
This project has been developed under Dr. Aruna Malapati for the course "Compiler Construction" at BITS Pilani Hyderabad Campus.

The parse table for the language is generted using this [website](http://jsmachines.sourceforge.net/machines/).

## Team Details
1. [Shashivardhan Reddy vadyala](https://github.com/ShashiWerdun) 
2. [Bathini Sai Akash]()
3. [Dasoju Pranay Kumar]()
4. [Chaitanya Chakka](https://github.com/ChiatanyaChakka)