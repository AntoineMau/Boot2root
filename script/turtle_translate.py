import sys

with open(sys.argv[1], 'r') as file :
    filedata = file.read()

filedata = filedata.replace('Tourne gauche de', 'left')
filedata = filedata.replace('Tourne droite de', 'right')
filedata = filedata.replace('Avance', 'forward')
filedata = filedata.replace('Recule', 'back')
filedata = filedata.replace(' degrees', '')
filedata = filedata.replace(' spaces', '')
filedata = filedata.replace('Can you digest the message? :)', '')


with open(sys.argv[1] + '_translate', 'w') as file:
    file.write(filedata)
