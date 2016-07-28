##Privilege separation and server-side sandboxing

###Exercise 2

    if ((dir = NCONF_get_string(conf, name, "dir")))
    {
	if (chroot(dir)) {
	 return 1;
	}
	if (chdir("/")) {
		return 1;
	}

###Exercise 3

In exercise 3 we modified the zookld.c file to support user and group IDs as well as supplementary group lists as specified in the zook.conf file. We added the three system calls (setresuid, setresgid and setgroups) after the chroot.

    if ((dir = NCONF_get_string(conf, name, "dir")))
    {
	if (chroot(dir)) {
	 return 1;
	}
	if (chdir("/")) {
		return 1;
	}
    setresgid(gid, gid, gid);
    setresuid(uid, uid, uid);
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
                    gid = 61012 # gid same as dynamic_svc because this needs to access persondb
 
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
    
  
In addition we also needed to make multiple changes to login.py to use the new auth service instead of the old functionality and
modify auth.py so that it adds entries to both persondb and creddb when registering.

### Exercise 6

Added "salt = Column(UnicodeText(128))" to the cred-database initialization.

Added hash_pwd(password) and check_pwd(password) functions to auth.py
Also modified to login function to use the new check_pwd and register to use
new hash_pwd:

    # Hashes the given password
    def hash_pwd(password):
        salt = binascii.hexlify(urandom(8))
        saltedpass = binascii.hexlify(pbkdf2.PBKDF2(password, salt).hexread(32))
        return saltedpass, salt    
    
    # Checks if the given password matches the stored hash
    def check_pwd(password):
        creddb = cred_setup()
        salt = creddb.query(Cred).get(salt)
        if password == binascii.hexlify(pbkdf2.PBKDF2(password, salt).hexread(32)):
            return True
        else:
            return False

    def login(username, password):
        db = cred_setup()
        cred = db.query(Cred).get(username)
        if not cred:
            return None
        if check_pwd:                           
            return newtoken(db, cred)
        else:
            return None

    def register(username, password):
    ...
        newcred.password, newcred.salt = hash_pwd(password)
    ...


### Exercise 7

Bank database setup:

    class Bank(BankBase):
        __tablename__ = "bank"
        username = Column(String(128), primary_key=True)
        zoobars = Column(Integer, nullable=False, default=10)
        
Bank service:

    [bank_svc]
            cmd = /zoobar/bank-server.py
            args = /banksvc/sock
            dir = /jail
            uid = 61016
            gid = 61012 # Group same as dynamic svc so this can access persondb and transferdb
          
bank-server:

    #!/usr/bin/python
    
    import rpclib
    import sys
    import bank
    from debug import *
    from sqlalchemy.orm import class_mapper
    def serialize(model): # Serialization needed for the get_log data
      """Transforms a model into a dictionary which can be dumped to JSON."""
      # first we get the names of all the columns on your model
      columns = [c.key for c in class_mapper(model.__class__).columns]
      # then we return their values in a dict
      return dict((c, getattr(model, c)) for c in columns)
    
    class BankRpcServer(rpclib.RpcServer):
        ## Fill in RPC methods here.
        def rpc_transfer(self, sender, recipient, zoobars):
            return bank.transfer(sender, recipient, zoobars)
        def rpc_balance(self, username):
            return bank.balance(username)
        def rpc_newaccount(self, username):
            return bank.newaccount(username)
        def rpc_get_log(self, username):
            serialized_labels = [
               serialize(label)
               for label in bank.get_log(username)
            ]
            return serialized_labels
    (_, dummy_zookld_fd, sockpath) = sys.argv
    
    s = BankRpcServer()
    s.run_sockpath_fork(sockpath)

chroot-setup.sh for bankdb:

    create_socket_dir /jail/banksvc 61016:61016 755
    python /jail/zoobar/zoodb.py init-bank
    chown 61016:61016 /jail/zoobar/db/bank/
    chmod 300 /jail/zoobar/db/bank/
    chown 61016:61016 /jail/zoobar/db/bank/bank.db
    chmod 600 /jail/zoobar/db/bank/bank.db

Needed to modify login.py so that the new bank account balance will be set with RPC call:

    def addRegistration(self, username, password):
        token = auth_client.register(username, password)
        if token is not None:
            bank_client.newaccount(username)
            return self.loginCookie(username, token)
        else:
            return None


### Exercise 8

Modified bank_client.py to get token and validate it:

    def validate(sender, token):
        arguments = {'username': sender, 'token': token}
        conn2 = rpclib.client_connect("/authsvc/sock")
        return conn2.call('check_token', **arguments)
        
    def transfer(sender, recipient, zoobars, token):
        if validate(sender, token):
            arguments = {'sender': sender, 'recipient': recipient, 'zoobars': zoobars}
            return conn.call('transfer', **arguments)
        else:
            return

transfer.py:

    def transfer():
        warning = None
        try:
            if 'recipient' in request.form:
                zoobars = eval(request.form['zoobars'])
                bank_client.transfer(g.user.person.username,
                              request.form['recipient'], zoobars, g.user.token)
                warning = "Sent %d zoobars" % zoobars
        except (KeyError, ValueError, AttributeError) as e:
            traceback.print_exc()
            warning = "Transfer to %s failed" % request.form['recipient']
    
        return render_template('transfer.html', warning=warning)
        
### Exercise 9

Modified profile-server.py:

    def rpc_run(self, pcode, user, visitor):
        uid = 61017

        userdir = '/tmp'
        ...
        


### Exercise 10

### Exercise 11

Modified profile-server.py to change privileges:

    def __init__(self, user, visitor):
        self.user = user
        self.visitor = visitor
        os.chdir('/tmp')
        os.setgid(61012)
        os.setuid(61016)
        
### Endnotes

At the end we revised all the rights in chroot-setup and tried to reduce them as much as possible:

    chown 61012:61012 /jail/zoobar/db/person/
    chmod 330 /jail/zoobar/db/person
    chown 61015:61015 /jail/zoobar/db/cred/
    chmod 300 /jail/zoobar/db/cred/
    chown 61012:61012 /jail/zoobar/db/transfer/
    chmod 330 /jail/zoobar/db/transfer/
    chown 61016:61016 /jail/zoobar/db/bank/
    chmod 300 /jail/zoobar/db/bank/
    
    chown 61012:61012 /jail/zoobar/db/person/person.db
    chmod 660 /jail/zoobar/db/person/person.db
    chown 61015:61015 /jail/zoobar/db/cred/cred.db
    chmod 600 /jail/zoobar/db/cred/cred.db
    chown 61012:61012 /jail/zoobar/db/transfer/transfer.db
    chmod 660 /jail/zoobar/db/transfer/transfer.db
    chown 61016:61016 /jail/zoobar/db/bank/bank.db
    chmod 600 /jail/zoobar/db/bank/bank.db
    
    
    chown 61014:61014 /jail/zoobar/index.cgi