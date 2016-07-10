'''Brainfuck Beta compiler and REPL

Language spec:
This is just a Lisp (really s-expression) version of BF Alpha, in
preparation for further improvements. All of the previous commands
are the same, although some are renamed. Arguments are now passed as
in Lisp, so:

    (+ 2) is +2

and so on.

+, -, <, and > remain the same.
`,` is now `input`.
`.` is now `output`.
`af` and `ab` are now both part of `add!-relative`, which can perform
    both functionalities based on its arguments.
The same is true for `s` and `m`, now `sub!-relative` and move-relative`
The exclamation points mark "mutating" functions, as in Common Lisp.
    Specifically functions that "move" the current cell's value.
`=` is `set-to`.
`[` and `]` are replaced with `while-n-0`, which is just the same as
    enclosing its argument (which is code) in a `[]` pair.
'''
import itertools as it
import sys
import bf_alpha
from bf_alpha import Memory
from lisp_core import listify, Atom, ConsCell, lisp_parse, progn, all_matched
from functools import reduce

CORE_FUNCTIONS = {
    '+': '+',
    '-': '-',
    '>': '>',
    '<': '<',
    'while-n-0': None,
    'input': ',',
    'output': '.',
    'add!-relative': 'a',
    'sub!-relative': 's',
    'move-relative': 'm',
    'set-to': '='
}

# Functions that require an extra argument to specify the direction they
# work in. So af and ab, etc.
DIRECTIONAL_FUNCTIONS = {
    'add!-relative',
    'sub!-relative',
    'move-relative'
}

# Functions that don't take any arguments
NO_ARGUMENT_FUNCTIONS = {
    '.',
    ','
}


def compile(parse_tree):
    '''Compile an AST of lisp-like BF Beta to BF Alpha
    
    For the most part performing simple translations from the
    `CORE_FUNCTIONS` dict.
    '''
    print(parse_tree)
    if isinstance(parse_tree.car, Atom):
        # the first item in a "code" s-exp should be the called function
        # since this isn't a true lisp there's no way for another s-exp
        # to evaluate to a function
        function = parse_tree.car.string
        if function == 'progn':
            # if the function is `progn`, just evaluate every statement
            # in the body individually
            parse_tree = parse_tree.cdr
            for node in listify(parse_tree):
                yield from compile(node)
        elif function in CORE_FUNCTIONS:
            if function == 'while-n-0':
                # while-n-0 just creates a normal brainfuck loop around
                # its body. The body is given the same as `progn`, and
                # is wrapped in it (as that's the only way to do code
                # blocks in BF Beta)
                yield '['
                yield from compile(progn(parse_tree.cdr))
                yield ']'
            elif function in NO_ARGUMENT_FUNCTIONS:
                yield CORE_FUNCTIONS[function]
            else:
                # All other functions do take an argument
                args = list(listify(parse_tree.cdr))
                arg = args[0].string if len(args) > 0 else '1'
                result_function = CORE_FUNCTIONS[function]
                modifier = ''
                if function in DIRECTIONAL_FUNCTIONS:
                    # forward if the argument is positive, backwards if
                    # it's negative. BF Alpha arguments are always
                    # positive though, so they are converted
                    modifier = 'f' if int(arg) > 0 else 'b'
                    arg = str(abs(int(arg)))
                yield CORE_FUNCTIONS[function] + modifier + arg 
    else:
        raise RuntimeError('Unknown function: {}'.format(parse_tree.car))


def eval(code, mem):
    '''Parse code into a cons-cell tree structure, then evaluate it'''
    parse_tree = lisp_parse(code)
    return eval_tree(parse_tree, mem)


def eval_tree(parse_tree, mem):
    '''Get the compiled BF Alpha code from the parse_tree and run it'''
    compilation = ''.join(compile(parse_tree))
    return bf_alpha.eval(compilation, mem)


def repl():
    '''REPL Brainfuck Beta code'''
    mem = Memory()
    while True:
        print(mem)
        code = input("| ")
        if not all_matched(code):
            while not all_matched(code):
                code += input("..| ")
        output = eval(code, mem)
        if output:
            print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, "r") as program_file:
            code = program_file.read()
            eval(code)
    else:
        print("Entering Brainfuck-Beta REPL...")
        repl()
