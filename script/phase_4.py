#!/usr/bin/python

import sys

def func4(nb):
    var1 = 0
    var2 = 0
    if nb < 2:
        var2 = 1
    else:
        var1 = func4(nb - 1)
        var2 = func4(nb - 2)
        var2 += var1
    return var2


def main():
    nb = int(sys.argv[1])
    print(func4(nb))

if __name__ == '__main__':
    main()
