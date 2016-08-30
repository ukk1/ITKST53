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
    


## Exercise 2: Attack Credentials

Hashing and salting seems to work properly.
Token check seems to be verified when transferring.

## Exercise 3: Attack the Python Sandbox