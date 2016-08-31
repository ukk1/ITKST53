##Attacking server isolation

## Exercise 1: Attack privilege isolation

 Privilege separation seems to be done as instructed, the services in zook.conf are separated:
 
    zookd:          61011:61011
    dynamic_svc:    61012:61012
    static_svc:     61013:61014
    auth_svc:       61015:61016
    bank_svc:       61017:61017
    profile_svc:    0:0, which will be switched to 61018:61016
    
 The database rights seems to be in order too:
 
    -rw------- 1 61017 61017 3072 Aug 24 10:23 bank.db
    -rw------- 1 61015 61014 3072 Aug 24 10:23 cred.db
    -rw-rw---- 1 61012 61016 3072 Aug 24 11:17 person.db
    -rw------- 1 61017 61014 2048 Aug 24 10:10 transfer.db
    
Comparing the design to our environment there was misconfiguration error regarding the ProfileAPIServer since in our environment we accidentally set the group and user ID to the same value as the bank service.

    class ProfileAPIServer(rpclib.RpcServer):
        def __init__(self, user, visitor):
        self.user = user
        self.visitor = visitor
        os.chdir('/tmp')
        os.setgid(61012)
        os.setuid(61016)

    [bank_svc]
        cmd = /zoobar/bank-server.py
        args = /banksvc/sock
        dir = /jail
        uid = 61016
        gid = 61012

## Exercise 2: Attack Credentials

####Hashing and salting

Password hashing and salting was done by following good security practices. They used the recommended PBKDF2 module and os.urandom function as advised. They also used the same length for the salt as we did - 8-bytes.

    salt = os.urandom(8)
    password_hash = pbkdf2.PBKDF2(password, salt).hexread(32)

They also verified that the given password matches the one stored in the database correctly when user logs in.

    def login(username, password):
        db = cred_setup()
        cred = db.query(Cred).get(username)
        if not cred:
            return None
        salt = cred.salt.decode('base64').strip()
        if cred.password == pbkdf2.PBKDF2(password, salt).hexread(32):
            return newtoken(db, cred)
        else:
            return None

Also when new user registers into the application the code takes care that the password is not stored in cleartext.

    newcred = Cred()
    newcred.username = username
    newcred.password = password_hash
    newcred.salt = salt.encode('base64').strip()
    cred_db.add(newcred)
    cred_db.commit()

In the database they also added a new column to store the salt value.

    class Cred(CredBase):
        __tablename__ = "cred"
        username = Column(String(128), primary_key=True)
        password = Column(String(128))
        token = Column(String(128))
        salt = Column(String(8))

####Token verification

The tokens were validated properly when transfering zoobars. In our code we did not verified the token in the bank, which was a clear coding error and thus the token was not being validated in the bank. 

The bank service also verifies the tokens before any zoobar transfering is allowed. 

bank_client.py

    def transfer(sender, recipient, zoobars, token):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('transfer', sender=sender, recipient=recipient,
                      zoobars=zoobars, token=token)

bank-server.py

    def rpc_transfer(self, sender, recipient, zoobars, token):
        return bank.transfer(sender, recipient, zoobars, token)

bank.py

    def transfer(sender, recipient, zoobars, token):
        bank_db = bank_setup()
        senderp = bank_db.query(Bank).get(sender)
        recipientp = bank_db.query(Bank).get(recipient)

        if not auth_client.check_token(senderp.username, token):
            raise ValueError()

## Exercise 3: Attack the Python Sandbox

The sandbox seems to work fine. The system creates separate user directories
to /jail/userdata/*b64username* 
I tried but was unable to access another user's folder for example with:

    x = object.__subclasses__()[40]("../dXNlcjI\=/keke.txt").read()
    print(x)
    
In the profile code.

