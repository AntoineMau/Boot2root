#!/usr/bin/python

def main():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    key = "isrveawhobpnutfg"
    print(alphabet)
    for char in alphabet:
        print(key[ord(char) & 0xf], end='')
    print()

if __name__ == '__main__':
    main()
