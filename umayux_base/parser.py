def isfloat(s):
    try:
        float(s)
    except ValueError:
        return False
    return True


def split(s):
    ret = []
    buf = ""
    separators = set([" ", "(", ")"])
    for i in xrange(len(s)):
        if s[i] in separators:
            if buf != "":
                ret.append(buf)
                buf = ""
        else:
            buf += s[i]

        if s[i] == "(" or s[i] == ")":
            ret.append(s[i])
    return ret


def cast(s):
    for i in xrange(len(s)):
        if type(s[i]) == list:
            cast(s[i])
        elif s[i].isdigit():
            s[i] = int(s[i])
        elif isfloat(s[i]):
            s[i] = float(s[i])


def parse(s):
    s = split(s)
    cast(s)
    stack = [[]]
    for i in xrange(len(s)):
        if s[i] == "(":
            stack.append([])
        elif s[i] == ")":
            l = stack.pop()
            stack[-1].append(l)
        else:
            stack[-1].append(s[i])
    return stack[0][0]


def main():
    s = "(si (3.4 df) 23)"
    print parse(s)


if __name__ == "__main__":
    main()