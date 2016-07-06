##Privilege separation and server-side sandboxing

###Exercise 2

    if ((dir = NCONF_get_string(conf, name, "dir")))
    {
        /* chroot into dir */
        if (chroot(dir) == 0); {
                chdir("/");
        } 
    }

###Exercise 3

In exercise 3 we modified the zookld.c file to support user and group IDs as well as supplementary group lists as specified in the zook.conf file. We added the three system calls (setresuid, setresgid and setgroups) after the chroot.

    if ((dir = NCONF_get_string(conf, name, "dir")))
    {
        /* chroot into dir */
        if (chroot(dir) == 0); {
                chdir("/");
        }

        setresuid(uid, uid, uid);
        setresgid(gid, gid, gid);
        setgroups(ngids, gids);
    }

Next we modified the zook.conf file to run the services other than root.

    [zookd]
    cmd = zookd
    uid = 61011
    gid = 61011
    dir = /jail

    [zookfs_svc]
    cmd = zookfs
    url = .*
    uid = 61012
    gid = 61012
    dir = /jail
    # You can control what executables zookfs will run as CGI scripts
    # by specifying the UID/GID of allowed CGI executables, as follows;
    # uncomment and replace 123 and 456 with your intended UID and GID:
    args = 61012 61012
    
We also had to modify the chroot-setup.sh file to move and setup correct permissions for the files so that zookfs process will run correctly.

    set_perms 61012:61012 755 /jail/zoobar/ #sets permissions for zoofs to the folder
    chown -hR 61012:61012 /jail/zoobar/ #sets permissions for zoofs to the folder and subfolders
    chmod -R 755 /jail/zoobar/ #sets execute permissions for zoofs to the folder

    python /jail/zoobar/zoodb.py init-person
    python /jail/zoobar/zoodb.py init-transfer
    chown -hR 61012:61012 /jail/zoobar/db/ # sets rights to the databases
