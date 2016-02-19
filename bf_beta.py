import itertools as it
import sys
import bf_alpha
from functools import reduce

FUNCTIONS = {'+': '+', '-': '-', '>': '>', '<': '<', 'while-n-0': None, 'input': ',',
             'output': '.', 'add!-relative': 'a', 'sub!-relative': 's', 'move-relative': 'm',
             'set-to': '=',
}

class Atom:
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string
    def __repr__(self):
        return 'Atom("{}")'.format(self.string)
    def __eq__(self, other):
        if type(other) is Atom: return self.string == other.string
        return self.string == other

class ConsCell:
    def __init__(self, first, second):
        self.car = first
        self.cdr = second
    def isnull(self):
        return self.car is None and self.cdr is None
    def __str__(self):
        if self.isnull(): return '()'
        elif type(self.cdr) is not ConsCell:
            return '({} . {})'.format(self.car, self.cdr)
        elif self.cdr.isnull():
            return '({})'.format(self.car)
        else:
            return '({} {}'.format(self.car, str(self.cdr)[1:])
        
    def __repr__(self):
        return 'Cell({}, {})'.format(repr(self.car), repr(self.cdr))
    
def matching_paren(string, index):
    assert(string[index] == '(')
    count = 1
    for i, c in enumerate(string[index + 1:]):
        if c == '(': count += 1
        elif c == ')': count -= 1
        if count == 0: return i + index + 1 

def paren_split(string):
    string = string.strip()
    assert(string[0] == '(' and string[-1] == ')')
    string = string[1:-1]
    while len(string) > 0:
        if string[0] == '(':
            close = matching_paren(string, 0)
            yield string[:close + 1]
            string = string[close + 1:]
        else:
            partition = string.partition(' ')
            yield partition[0]
            string = partition[2]
        string = string.strip()
    
def lisp_parse(s, delim=('()')):
    s = s.replace('\n', ' ')
    s = s.replace('\t', ' ')
    s = s.strip()
    if s.replace(' ', '') == '()':
        return ConsCell(None, None)
    elif s[0] != '(':
        return Atom(s)
    else:
        tokens = list(paren_split(s))
        return reduce(lambda x, y: ConsCell(lisp_parse(y), x),
                      reversed(tokens), ConsCell(None, None))
def listify(parse_tree):
   while not parse_tree.isnull():
       yield parse_tree.car
       parse_tree = parse_tree.cdr
def progn(parse_tree):
    return ConsCell(Atom('progn'), parse_tree)

def compile(parse_tree):
    if type(parse_tree.car) is Atom and parse_tree.car == "progn":
        parse_tree = parse_tree.cdr
        for node in listify(parse_tree):
            yield from compile(node)
    elif parse_tree.car.string in FUNCTIONS:
        f = parse_tree.car.string
        if f in '+-><':
            args = list(listify(parse_tree.cdr))
            if len(args) == 0: arg = '1'
            else: arg = args[0].string
            yield FUNCTIONS[f] + arg
        elif f == 'input': yield functions
        elif f == 'output': yield '.'
        elif f == 'set-to':
            args = list(listify(parse_tree.cdr))
            yield '=' + args[0].string
        elif f in ('add!-relative', 'sub!-relative', 'move-relative'):
            args = list(listify(parse_tree.cdr))
            if len(args) == 0: arg = '1'
            else: arg = int(args[0].string)
            if arg > 0:
                yield FUNCTIONS[f] + 'f' + str(arg)
            else:
                yield FUNCTIONS[f] + 'b' + str(abs(arg))
        elif f == 'while-n-0':
            yield '['
            yield from compile(progn(parse_tree.cdr))
            yield ']'
    else:
        raise RuntimeError('Unknown function: {}'.format(parse_tree.car))

def eval(code, mem):
    compilation = ''.join(compile(lisp_parse(code)))
    return bf_alpha.eval(compilation, mem)

def all_matched(code):
    return bf_alpha.brainfuck.all_matched(code, '()')

def repl():
    mem = bf_alpha.brainfuck.Memory()
    while True:
        print(mem)
        code = input("| ")
        if not all_matched(code):
            while not all_matched(code):
                code += input("..| ")
        output = eval(code, mem)
        if output: print()
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, "r") as program_file:
            code = program_file.read()
            eval(code)
    else:
        print("Entering Brainfuck-Beta REPL...")
        repl()
