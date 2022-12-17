 #!/usr/bin/python

import subprocess

file = open('combinations', 'r')
bomb_string = '(echo "Public speaking is very easy." ; echo "1 2 6 24 120 720" ; echo "1 b 214" ; echo 9 ; echo opekma ; echo 4 '
for i in file.readlines():
    p = subprocess.Popen(bomb_string + i + ') | ./bomb', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    boom = False
    while True:
            line = p.stdout.readline()
            stdout.append(line)
            if line == 'BOOM!!!\n':
                    boom = True
            if line == '' and p.poll() != None:
                    break
    if boom == False:
            print('4 ' + i)
            break
