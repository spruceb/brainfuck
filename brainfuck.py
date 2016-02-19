#!/usr/local/bin/python3
import sys
import readline

CELL_SIZE = 2 ** 32 # 32 bit unsigned registers
class Memory:
    def __init__(self):
        self.memory = [0] * 30000
        self.ptr = 0
    @property
    def loc(self):
        return self.memory[self.ptr]
    @loc.setter
    def loc(self, value):
        self.memory[self.ptr] = value % CELL_SIZE
    def __repr__(self):
        output = ""
        end = max(self.ptr, ([0] + [i for i, d in enumerate(self.memory) if d != 0])[-1])
        for i, data in enumerate(self.memory[:end + 1]):
            if i == self.ptr:
                output += " *{}* ".format(data)
            else: 
                output += " {} ".format(data)
        return output.strip()

def match_index(index, code, reverse=False, chars=("[", "]")):
    open_, close_ = chars if not reverse else reversed(chars)
    assert(code[index] == open_)
    nest_count = 1
    index_range = range(index-1, -1, -1) if reverse else range(index + 1, len(code))
    for i in index_range:
        if code[i] == open_:
            nest_count += 1
        elif code[i] == close_:
            nest_count -= 1
            if nest_count == 0:
                return i
    return None

def remove_pairs(string, pair):
    result = []
    count = [0,0]
    pair_seq = False
    def end_seq():
        if count == [0, 0]: return
        most_in_seq = pair[0 if count[0] > count[1] else 1]
        diff = abs(count[0] - count[1])
        result.append(most_in_seq * diff)
        count[0] = count[1] = 0
    for c in string:
        if c not in pair:
            if pair_seq:
                end_seq()
                pair_seq = False
            result += c
        else:
            count[pair.index(c)] += 1
            pair_seq = True
    end_seq()
    return "".join(result)


def minimize(brainfuck):
    brainfuck = remove_pairs(brainfuck, ("+", "-"))
    brainfuck = remove_pairs(brainfuck, (">", "<"))
    return brainfuck

def eval(code, mem=Memory(), cmd_index=0):
    code = minimize(code)
    output = ""
    while cmd_index < len(code):
        cmd = code[cmd_index]
        if cmd == ">":
            mem.ptr += 1
        elif cmd == "<":
            mem.ptr -= 1
            if mem.ptr < 0: 
                mem.ptr = 0
        elif cmd == "+":
            mem.loc += 1
            if mem.ptr >= len(mem.memory):
                mem.ptr = len(mem.memory) - 1
        elif cmd == "-":
            mem.loc -= 1
        elif cmd == ".":
            print(chr(mem.loc), end="")
            output += chr(mem.loc)
        elif cmd == ",":
            mem.loc = ord(sys.stdin.read(1))
        elif cmd == "[":
            if mem.loc == 0:
                cmd_index = match_index(cmd_index, code)
        elif cmd == "]":
            if mem.loc != 0:
                cmd_index = match_index(cmd_index, code, reverse=True)

        if cmd_index is None:
            raise SyntaxError("No matching bracket")

        cmd_index += 1
    return output

def all_matched(code, chars=("[", "]")):
    nest_count = 0
    for c in code:
        if c == chars[0]:
            nest_count += 1
        elif c == chars[1]:
            nest_count -= 1
    return nest_count == 0

def repl():
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
        print("Entering Brainfuck REPL...")
        repl()
        
