class Node:

    def __init__(self, nodeType, value):
        self.children = []
        self.type = nodeType
        self.value = value

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return f"'{self.value}'"

# class ParseTree:
#     def printTree():
#         pass
