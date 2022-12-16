#!/usr/bin/python

from os import listdir
from re import findall

main_c = [0] * 750
dir_name = 'ft_fun/'

for file in listdir(dir_name):
    with open(f'{dir_name}{file}', 'r') as f:
        content = f.read()
        match = findall(r'(\d*)$', content)
        main_c[int(match[0]) - 1] = content

with open('main.c', 'w') as f:
    f.write('\n'.join(main_c))
