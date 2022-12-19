# Solution 6

Cette solution consiste à analyser l'`ISO` en lui même, pour cela nous le montons sur notre machine, ce qui nous permet d'avoir accès aux fichiers qui le compose.

Nous trouvons un fichier `filesystem.squashfs`. Ce type de fichier contient tous les fichiers qui composent l'arborescence de notre `ISO`.

Un fois extrait, nous lancons la commande `unsquashfs` sur le fichier, commande qui va nous décompresser tous les fichiers présents dans le `filesystem`.

Une fois cela fait, voici ce que nous obtenons :

```shell
$ ls -1 squashfs-root
bin
boot
dev
etc
home
initrd.img
lib
media
mnt
opt
proc
root
run
sbin
selinux
srv
sys
tmp
usr
var
vmlinuz
```

Nous avons donc accès à tous les fichiers de la VM.

Nous avons trouvé trois façons d'exploiter ces fichier, il en existe certainement d'autres.

- Récupérer le mot de passe `ftp` de `lmezard` :

```shell
$ cat home/LOOKATME/password
lmezard:G!@M6f4Eatau{sF"
```

Ce qui nous permet de bypasser toute la partie web et commencer les mini-jeux du `writeup1`.

- Récupérer le mini-jeux `turtle` directement dans le home de `thor` :

```shell
$ ls home/thor
README  turtle
```

Ce mini-jeu donne accès au mot de passe de l'utilisateur `zaz` pour se connecter en `SSH`.

- Regarder dans le `bash_history` de `root` :

```shell
$ cat root/.bash_history
...
adduser zaz
646da671ca01bb5d84dbb5fb2238dc8e
...
```

En remontant les logs, nous trouvons trace de la création de l'utilisateur `zaz` avec son mot de passe.
