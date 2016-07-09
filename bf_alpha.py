'''Brainfuck Alpha, a layer of macros over brainfuck

Language Spec:
All brainfuck commands still work, and several other commands are added.
Almost every command now takes an integer argument. So, for example:

    +3 translates to +++
    >5 to >>>>>

and so on. The first new command is:

    =

which sets the current cell to its argument value.

The rest of the new commands are actually command families.

`af` and `ab` add "backwards" and "forwards", respectively. This means
they transfer the whole value of the selected cell to the one `n`
ahead or behind. So if the cells were: [0 0 *1* 0 1], with the middle cell
selected, af2 would add 1 to the last cell, so [0 0 *0* 0 3].

`sf` and `sb` are the same, except they subtract the value.

`mf` and `mb` move the current value to the cell specified by their
arguments, meaning they zero that cell then add the current one into it.
'''
import itertools as it
import sys
import brainfuck
from brainfuck import Memory
OLD_TOKENS = ['+', '-', '<', '>', '[', ']', ',', '.']
EXTENDED_TOKENS = ['=']
# These token family dictionaries define mappings from the new commands
# to pure brainfuck. For instance, `af3` maps to `[->3+<3]`. In the
# strings, `\*` denotes a place where the argument will be inserted.
# This is helpful since these strings are not in fact pure brainfuck,
# but in fact make use of prior parts of BF Alpha. For instance the
# definition of `af` uses the new argument to `+`, and the definition
# of `m` relies on `a`. This is made possible by fixed point
# translation, repeated compiling of the code until it no longer
# changes. This works because everything bottoms out in original
# commands eventually.
TOKEN_FAMILIES = {
    'a': {
        'f': '[->\*+<\*]',
        'b': '[-<\*+>\*]'
    },
    's': {
        'f': '[->\*-<\*]',
        'b': '[-<\*->\*]'
    },
    'm': {
        'f': '>\*[-]<\*af\*',
        'b': '<\*[-]>\*ab\*'}
}

def fixed_point_translation(s):
    '''Recursively compile the code until it no longer changes

    As described above several of the BF Alpha definitions use other
    BF Alpha features. However they do all bottom out in pure brainfuck,
    so it only takes a few iterations of compiling to get there.
    '''
    result = ''.join(translate(s))
    if result == s:
        return s
    return fixed_point_translation(result)

def next_number(s, index):
    '''Find the next integer argument after the `index` in `s`'''

    # skips any non-valid characters
    index += len(list(it.takewhile(lambda x: not x.isdigit()
                                   and x not in OLD_TOKENS
                                   and x not in TOKEN_FAMILIES
                                   and x not in EXTENDED_TOKENS, s[index:])))
    # gets as many digits as can be found
    num = ''.join(it.takewhile(lambda x: x.isdigit(), s[index:]))
    index += len(num)
    # if no argument is found, default to 1
    return (int(num) if num else 1, index)

def translate(s):
    '''Compile the BF Alpha code from s to brainfuck'''
    i = 0
    while i < len(s):
        if s[i] in OLD_TOKENS:
            arg, index = next_number(s, i + 1)
            yield s[i] * arg # just the token repeated `arg` times
            i = index
        elif s[i] in EXTENDED_TOKENS:
            arg, index = next_number(s, i + 1)
            if s[i] == '=':
                # the `[-]` zeros the current cell, as in normal BF
                yield '[-]' + '+' * arg
            i = index
        elif s[i] in TOKEN_FAMILIES:
            # `s[i]` is the first character, so `a`, `s`, or `m`
            # The next character should be `f` or `b`, which determines
            # the direction. No validation is done at the moment.
            direction = s[i + 1]
            arg, index = next_number(s, i + 2)
            template = TOKEN_FAMILIES[s[i]][direction]
            template = template.replace('\*', str(arg))
            # Since some of these use BF Alpha features in their
            # definitions, repeated compilation is required
            yield fixed_point_translation(template)
            i = index
        else: i += 1 # ignore non-valid characters

def eval(code, mem=Memory(), cmd_index=0):
    '''Compile BF Alpha code to brainfuck and run it'''
    result = ''.join(translate(code))
    return brainfuck.eval(result, mem, cmd_index)

# This sets `all_matched` to the original function from `brainfuck`
all_matched = brainfuck.all_matched

def repl():
    '''REPL for Brainfuck Alpha code'''
    mem = Memory()
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
        print("Entering Brainfuck-Alpha REPL...")
        repl()
