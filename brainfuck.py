import sys
try:
    filename = sys.argv[1]
except IndexError as e:
    print("Requires a filename")
    sys.exit()
with open(filename, "r") as program_file:
    code = program_file.read()

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
    
    def inc(self):
        self.ptr += 1
    
    def dec(self):
        self.ptr -= 1
   
    def plus(self):
        self.loc += 1

    def minus(self):
        self.loc -= 1

    def output(self):
        print(chr(self.loc), end="")

    def input(self):
        self.loc = sys.stdin.read(1)

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
    raise SyntaxError("No matching close bracket")

mem = Memory()
cmd_index = 0
while cmd_index < len(code):
    cmd = code[cmd_index]
    if cmd == ">":
        mem.inc()
    elif cmd == "<":
        mem.dec()
    elif cmd == "+":
        mem.plus()
    elif cmd == "-":
        mem.minus()
    elif cmd == ".":
        mem.output()
    elif cmd == ",":
        mem.input()
    elif cmd == "[":
        if mem.loc == 0:
            cmd_index = match_index(cmd_index, code)
    elif cmd == "]":
        if mem.loc != 0:
            cmd_index = match_index(cmd_index, code, reverse=True)

    cmd_index += 1