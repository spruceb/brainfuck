import itertools as it
import sys
import brainfuck
OLD_TOKENS = ['+', '-', '<', '>', '[', ']', ',', '.']
EXTENDED_TOKENS = ['=']
TOKEN_FAMILIES = {'a': {'f': '[->\*+<\*]', 'b': '[-<\*+>\*]'},
                  's': {'f': '[->\*-<\*]', 'b': '[-<\*->\*]'},
                  'm': {'f': '>\*[-]<\*af\*', 'b': '<\*[-]>\*ab\*'}}

def fixed_point_translation(s):
    result = ''.join(translate(s))
    if result == s:
        return s
    return fixed_point_translation(result)

def next_number(s, index):
    index += len(list(it.takewhile(lambda x: not x.isdigit()
                                   and x not in OLD_TOKENS
                                   and x not in TOKEN_FAMILIES
                                   and x not in EXTENDED_TOKENS, s[index:])))
    num = ''.join(it.takewhile(lambda x: x.isdigit(), s[index:]))
    index += len(num)
    return (int(num) if num else 1, index)

def translate(s):
    i = 0
    while i < len(s):
        if s[i] in OLD_TOKENS:
            arg, index = next_number(s, i + 1)
            yield s[i] * arg
            i = index
        elif s[i] in EXTENDED_TOKENS:
            arg, index = next_number(s, i + 1)
            if s[i] == '=':
                yield '[-]' + '+' * arg
            i = index
        elif s[i] in TOKEN_FAMILIES:
            direction = s[i + 1]
            arg, index = next_number(s, i + 2)
            template = TOKEN_FAMILIES[s[i]][direction]
            template = template.replace('\*', str(arg))
            yield fixed_point_translation(template)
            i = index
        else: i += 1

def eval(code, mem=brainfuck.Memory(), cmd_index=0):
    result = ''.join(translate(code))
    return brainfuck.eval(result, mem, cmd_index)

all_matched = brainfuck.all_matched

def repl():
    mem = brainfuck.Memory()
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
