#!/usr/local/bin/python3
import sys

class Memory:
    def __init__(self):
        self.memory = [0] * 30000
        self.ptr = 0
    @property
    def loc(self):
        return self.memory[self.ptr]
    @loc.setter
    def loc(self, value):
        self.memory[self.ptr] = value
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

def eval(code, mem=Memory(), cmd_index=0):
    while cmd_index < len(code):
        cmd = code[cmd_index]
        if cmd == ">":
            mem.ptr += 1
        elif cmd == "<":
            mem.ptr -= 1
        elif cmd == "+":
            mem.loc += 1
        elif cmd == "-":
            mem.loc -= 1
        elif cmd == ".":
            print(chr(mem.loc), end="")
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
        eval(code, mem)

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError as e:
        print("Entering Brainfuck REPL...")
        repl()
    else:
        with open(filename, "r") as program_file:
            code = program_file.read()
            eval(code)