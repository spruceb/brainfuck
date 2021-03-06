import itertools
from brainfuck import minimize

def naive_encode(string):
    result = ""
    for c in string:
        result += "+" * ord(c)
        result += ">"
    result += "+" * 10
    result += "<" * len(string)
    result += "[.>]"
    return result

def one_register_encode(string):
    chars = map(ord, string)
    num = 0
    result = ""
    for c in chars:
        op = "-" if c < num else "+"
        result += op * abs(c - num)
        result += "."
        num = c
    return result

def loop_encode(string):
    result = ""
    if string[-1] != "\n":
        string += "\n"
    chrs = list(enumerate([None] + [ord(c) for c in string]))[1:]
    sorted_chrs = reversed(sorted(chrs, key=lambda x: x[1]))
    groups = itertools.groupby(sorted_chrs, key=lambda x: round(x[1]/10))
    for group in groups:
        group_num, group_chrs = group[0], list(group[1])
        group_chrs = sorted(group_chrs, key=lambda x: x[0])
        result += "+" * group_num
        result += "[>"
        last_index = 1
        for c in group_chrs:
            result += ">" * (c[0] - last_index)
            result += "+" * 10
            last_index = c[0]
        result += "<" * last_index + "-]"
        last_index = 0
        for c in group_chrs:
            result += ">" * (c[0] - last_index)
            op = "+" if c[1] > 10 * group_num else "-"
            result += op * abs(c[1] - 10 * group_num)
            last_index = c[0]
        result += "<" * last_index
    result += ">[.>]"
    return minimize(result)

def optimized_encode(string):
    result = ""
    chars = list(enumerate(map(ord, string)))
    lowest = min(chars, key=lambda x: x[1])
    length = len(chars)
    result += "+" * length
    result += "[->>[>]+[<]<]"
    result += "+" * lowest
    result += "[->>[+>]<[<]<]"




print(loop_encode("You should check out brainfuck"))