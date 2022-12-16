#!/bin/bash

echo -e "\n### Decompression ###"
tar -xf fun

echo -e "\n### Run Python ###"
python fun.py

echo -e "\n### Compile Python ###"
gcc main.c

echo -e "\n### Trouver le mot de pass ###"
echo -n `./a.out | head -n1 | cut -d " " -f4` | sha256sum

echo -e "\n### Nettoyage ###"
rm -rf a.out ft_fun main.c
