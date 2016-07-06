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
        args = 61012 61012
    
We also had to modify the chroot-setup.sh file to move and setup correct permissions for the files so that zookfs process will run correctly.

    set_perms 61012:61012 755 /jail/zoobar/ #sets permissions for zoofs to the folder
    chown -hR 61012:61012 /jail/zoobar/ #sets permissions for zoofs to the folder and subfolders
    chmod -R 755 /jail/zoobar/ #sets execute permissions for zoofs to the folder

    python /jail/zoobar/zoodb.py init-person
    python /jail/zoobar/zoodb.py init-transfer
    chown -hR 61012:61012 /jail/zoobar/db/ # sets rights to the databases

###Exercise 4

For this exercise, we had to modify the zook.conf file to separate dynamic and static content. Also modification for the chroot-setup.sh file was needed to have the server working properly with these new changes.

    [zook]
        port       = 8080
        # To run multiple services, list them separated by commas, like:
        #  http_svcs = first_svc, second_svc
        http_svcs  =  dynamic_svc, static_svc
        extra_svcs = echo_svc

    [dynamic_svc]
        cmd = zookfs
        url = .*cgi.*(login|logout|echo|users|transfer|zoobarjs|) #serve only the provided python files
        uid = 61012
        gid = 61012
        dir = /jail
        args = 61014 61014 #uid and guid, which are used to run index.cgi file

    [static_svc]
        cmd = zookfs
        url = .*
        uid = 61013
        gid = 61013
        dir = /jail
        args = 123 456 #static_svc requires some argument to work properly

Below are the changes made to the chroot-setup.sh file for this exercise. The modifications will make the static_svc uid and guid as the owner of the /jail/zoobar folder and other dynamic content, such as index.cgi and db folder is owned by the dynamic_svc uid and guid.

    chown -hR 61013:61013 /jail/zoobar/ #sets permissions for static_svc uid and guid

    python /jail/zoobar/zoodb.py init-person
    python /jail/zoobar/zoodb.py init-transfer

    chown -hR 61012:61012 /jail/zoobar/db/ # sets rights to the databases for dynamic_svc
    chmod 330 /jail/zoobar/db
    chown 61012:61012 /jail/zoobar/db/person
    chmod 330 /jail/zoobar/db/person
    chown 61012:61012 /jail/zoobar/db/transfer
    chmod 330 /jail/zoobar/db/transfer

    chown 61014:61014 /jail/zoobar/index.cgi

### Exercise 5

zoodb.py modifications:
    
    9: Added CredBase = declarative_base()
    27: Added class Cred(TransferBase):
                        __tablename__ = "cred"
                        username = Column(String(128), primary_key=True)
                        password = Column(String(128))
                        token = Column(String(128))
    58: Modified  print "Usage: %s [init-person|init-transfer|init-cred]" % sys.argv[0]
    66: Added     elif cmd == 'init-cred':
                        cred_setup()
                        
zook.conf modifications:

    45: Added [auth_svc]
                    cmd = /zoobar/auth-server.py
                    args = /authsvc/sock
                    dir = /jail
                    uid = 61015
                    gid = 61015
 
chroot-setup.sh database right modifications:

    python /jail/zoobar/zoodb.py init-cred
    
    chown -hR 61012:61012 /jail/zoobar/db/transfer/transfer.db
    chown -hR 61012:61012 /jail/zoobar/db/person/person.db # sets rights to the databases
    chmod 330 /jail/zoobar/db
    chown 61012:61012 /jail/zoobar/db/person
    chmod 330 /jail/zoobar/db/person
    chown 61012:61012 /jail/zoobar/db/transfer
    chmod 330 /jail/zoobar/db/transfer
    chown -hR 61015:61015 /jail/zoobar/db/cred/cred.db
    chown 61015:61015 /jail/zoobar/db/cred
    chmod 300 /jail/zoobar/db/cred