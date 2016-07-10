from functools import reduce


class Atom:
    '''Class for atomic elements, i.e. Lisp symbols
    
    Effectively just a wrapper over a string
    '''
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def __repr__(self):
        return 'Atom("{}")'.format(self.string)

    def __eq__(self, other):
        if isinstance(other, Atom):
            return self.string == other.string
        return self.string == other


class ConsCell:
    '''A 2-ple for use in singly linked Lisp lists

    If the first and second values are both None, the cell is null,
    or '()
    '''
    def __init__(self, first, second):
        self.car = first
        self.cdr = second

    def isnull(self):
        return self.car is None and self.cdr is None

    def __str__(self):
        if self.isnull():
            return '()'
        elif not isinstance(self.cdr, ConsCell):
            return '({} . {})'.format(self.car, self.cdr)
        elif self.cdr.isnull():
            return '({})'.format(self.car)
        else:
            return '({} {}'.format(self.car, str(self.cdr)[1:])

    def __repr__(self):
        return 'Cell({}, {})'.format(repr(self.car), repr(self.cdr))

    def __eq__(self, other):
        return self.car == other.car and self.cdr == other.cdr


def matching_paren(string, index):
    '''Find the close paren matching the open paren at `index`'''
    assert(string[index] == '(')
    count = 1
    for i, c in enumerate(string[index + 1:]):
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
        if count == 0:
            return i + index + 1


def paren_split(string):
    '''Generate a list of the s-exps in an s-exp

    Requires that the string contains a single s-exp with nothing but
    whitespace before and after it
    '''
    string = string.strip()
    assert(string[0] == '(' and string[-1] == ')')
    # strips the beginning and ending parens
    string = string[1:-1].strip()
    while len(string) > 0:
        if string[0] == '(':
            # if the current item in the s-exp is another s-exp, yield
            # it wrapped in its parens
            close_index = matching_paren(string, 0)
            yield string[:close_index + 1]
            string = string[close_index + 1:]
        else:
            # if it's an atom, yield it and skip the following whitespace
            partition = string.partition(' ')
            yield partition[0]
            string = partition[2]
        string = string.strip()


def lisp_parse(code_string, delim='()'):
    '''Parse a string as Lisp into ConsCells and Atoms'''
    # strip unnecessary whitespace
    code_string = code_string.replace('\n', ' ').replace('\t', ' ')
    code_string = code_string.strip()

    # '() is an empty cell
    if code_string.replace(' ', '') == ''.join(delim):
        return ConsCell(None, None)
    elif code_string[0] != delim[0]:  # if it isn't an s-exp it's an atom
        return Atom(code_string)
    else:
        # gets the top level s-exp list
        tokens = list(paren_split(code_string))
        # recursively parses all of them, and creates cons cells
        # containing them as in Lisp, ending with '()
        return reduce(lambda x, y: ConsCell(lisp_parse(y), x),
                      reversed(tokens), ConsCell(None, None))


def de_listify(lst):
    '''Transform a list of lists, strings, and ints to an s-expr
    
    Example: takes `["test", [1], "two"]` and returns
        ConsCell(
            Atom(test), 
            ConsCell(
                Atom(1), 
                ConsCell())
            Atom(two)
            ConsCell())
    '''
    if isinstance(lst, Atom) or isinstance(lst, ConsCell):
        return lst
    elif isinstance(lst, str):
        return Atom(lst)
    elif isinstance(lst, int):
        return Atom(str(lst))
    lst = list(lst)
    return reduce(lambda x, y: ConsCell(de_listify(y), x),
                  reversed(lst), ConsCell(None, None))


def deep_listify(lst):
    '''Recursively transform an s-expr into a Python list'''
    if type(lst) is Atom:
        return lst.string
    elif type(lst) is ConsCell:
        if lst.isnil():
            return []
        return [listify(lst.car)] + listify(lst.cdr)


def listify(parse_tree):
    '''Get a Python list of the elements of an s-expr
    
    Unlike `deep_listify` this will keep nested s-exprs or atoms in
    their original states.
    '''
    while not parse_tree.isnull():
        yield parse_tree.car
        parse_tree = parse_tree.cdr


def progn(parse_tree):
    '''Wrap code in a `progn` bock
    
    As in Lisps, this means to execute every statement in the block
    passed as an "argument" to `progn` sequentially.
    '''
    return ConsCell(Atom('progn'), parse_tree)


def fixed_point(data, f):
    '''Get a fixed point of `f`, starting with `data`

    A fixed point `x` of `f` is an `x` such that `x = f(x)`. This
    function finds such a value by calling `f` on data, and then on the
    result, and so on until the result is the same as the input for the
    last call.
    '''
    result = f(data)
    if result == data:
        return result
    return fixed_point(result, f)


def all_matched(code, chars=('(', ')')):
    '''Check to see if all of the pairs (from `chars`) have matches'''
    nest_count = 0
    for c in code:
        if c == chars[0]:
            nest_count += 1
        elif c == chars[1]:
            nest_count -= 1
    return nest_count == 0
