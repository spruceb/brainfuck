#!/usr/local/bin/python3
'''Interpret and execute brainfuck code

This module is a simple interpreter for the Brainfuck esolang.
It uses 2^32 cells rather than the usual 30000.
It also includes a REPL.

Brainfuck is an extremely simple yet Turing complete programming
language. The essential aspects are the data cells (n array of
integers) and the data pointer, which is effectively just an index into
the cell array. The commands are:
    
    +: add one to cell at pointer
    -: subtract one from cell at pointer
    >: move pointer to the right
    <: move pointer to the left
    [: begin a "loop", if the current cell value is 0, jumps to the
        matching "]", otherwise does nothing
    ]: end a "loop", if the current value is not 0, jumps back to the
        matching "[", otherwise does nothing
    ,: takes user input and sets the current cell to the ASCII result
    .: prints the current cell as an ASCII character
'''
import sys
import readline
import itertools as it

# max value to be stored in a cell
CELL_SIZE = 2 ** 32


class Memory:
    '''Store data for brainfuck runtime'''
    MEMORY_SIZE = 30000

    def __init__(self):
        '''Initializes data and memory pointer'''
        self.memory = [0] * self.MEMORY_SIZE
        self.ptr = 0

    @property
    def loc(self):
        return self.memory[self.ptr] % CELL_SIZE

    @loc.setter
    def loc(self, value):
        self.memory[self.ptr] = value % CELL_SIZE

    def __repr__(self):
        # gets max of the pointer location and the last non-zero
        last_nonzero = reduce(lambda x, y: y, # the reduce gets last item
            it.takewhile(lambda pair: pair[0], enumerate(self.memory)))
        end = max(self.ptr, last_nonzero[0] or 0)
        output = ''.join(
            (' *{}* ' if i == self.ptr else ' {} ').format(data)
                for i, data in enumerate(self.memory[:end + 1]))
        return output.strip()


def match_index(index, code, reverse=False, chars=('[', ']')):
    '''Find index of bracket matching one at passed index
    
    This function searches through the string `code` for the bracket
    at `index`. `reverse` determines whether we're looking for the close
    bracket matching an open or the open bracket matching a close
    bracket. Other pairs of characters can be searched for based on
    what is passed for `chars`
    '''
    open_, close_ = chars if not reverse else reversed(chars)
    # fails if given the wrong index
    assert(code[index] == open_)
    index_range = (range(index + 1, len(code)) if not reverse
                   else range(index - 1, -1, -1))
    nest_count = 1
    for i in index_range:
        if code[i] == open_:
            nest_count += 1
        elif code[i] == close_:
            nest_count -= 1
            if nest_count == 0:
                return i

def remove_pairs(string, pair):
    '''Remove sequential occurrences of canceling values
    
    Used to remove things like ++-- from brainfuck code, as this would
    just do nothing, or collapse >>><< to just >
    ''' 
    result = []
    count = [0, 0]
    pair_seq = False

    # this sub-function just checks the counts for which of the pair
    # occurred more, then appends their difference to the result
    # this has the effect of turning +++-- into just +
    def end_seq():
        if count == [0, 0]:
            return
        most_in_seq = pair[count[0] <= count[1]]
        diff = abs(count[0] - count[1])
        result.append(most_in_seq * diff)
        count[0] = count[1] = 0

    # goes through each character, appending to result unless it's part
    # of a pair sequence, then collapses those as much as possible
    for c in string:
        if c not in pair:
            if pair_seq:
                end_seq()
                pair_seq = False
            result.append(c)
        else:
            count[pair.index(c)] += 1
            pair_seq = True
    end_seq()
    return ''.join(result)


def minimize(brainfuck):
    '''Remove unnecessary pairs from brainfuck code
    
    There are two pairs of brainfuck instructions that cancel each other
    out when in sequence. + and - because those add and subtract to the
    current cell, and >, < because those add and subtract from the
    pointer value. We remove these sequences to shorten code.
    '''
    brainfuck = remove_pairs(brainfuck, ('+', '-'))
    brainfuck = remove_pairs(brainfuck, ('>', '<'))
    return brainfuck


def eval(code, mem=Memory(), cmd_index=0):
    '''Run brainfuck code with a given Memory object
    
    Also starts execution at the `cmd_index`
    '''
    code = minimize(code)
    output = ''
    while cmd_index < len(code):
        cmd = code[cmd_index]
        if cmd == '>':
            mem.ptr += 1
        elif cmd == '<':
            mem.ptr -= 1
            if mem.ptr < 0:
                mem.ptr = 0
        elif cmd == '+':
            mem.loc += 1
            if mem.ptr >= len(mem.memory):
                mem.ptr = len(mem.memory) - 1
        elif cmd == '-':
            mem.loc -= 1
        elif cmd == '.':
            print(chr(mem.loc), end='')
            output += chr(mem.loc)
        elif cmd == ',':
            mem.loc = ord(sys.stdin.read(1))
        elif cmd == '[':
            if mem.loc == 0:
                cmd_index = match_index(cmd_index, code)
        elif cmd == ']':
            if mem.loc != 0:
                cmd_index = match_index(cmd_index, code, reverse=True)

        if cmd_index is None:
            raise SyntaxError('No matching bracket')

        cmd_index += 1
    return output


def all_matched(code, chars=('[', ']')):
    '''Checks that all bracket pairs have matches'''
    nest_count = 0
    for c in code:
        if c == chars[0]:
            nest_count += 1
        elif c == chars[1]:
            nest_count -= 1
    return nest_count == 0


def repl():
    '''Runs the REPL'''
    mem = Memory()
    while True:
        print(mem)
        code = input('| ')
        # if there are unclosed loops, waits for closes before executing
        if not all_matched(code):
            while not all_matched(code):
                code += input('..| ')
        output = eval(code, mem)
        if output:
            print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, 'r') as program_file:
            code = program_file.read()
            eval(code)
    else:
        print('Entering Brainfuck REPL...')
        repl()
