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

    setresuid(uid, uid, uid);
    setresgid(gid, gid, gid);
    setgroups(ngids, gids);
