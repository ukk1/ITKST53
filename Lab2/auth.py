from zoodb import *
from debug import *
from os import urandom
import hashlib
import random
import pbkdf2
import binascii

def hash_pwd(password):
    salt = binascii.hexlify(urandom(8))
    saltedpass = binascii.hexlify(pbkdf2.PBKDF2(password, salt).hexread(32))
    return saltedpass, salt    

def check_pwd(password): #TODO: Taa toimimaan
    creddb = cred_setup()
    salt = creddb.query(Cred).get(salt)
    if password == binascii.hexlify(pbkdf2.PBKDF2(password, salt).hexread(32)):
	return True
    else:
	return False        

def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None
    if check_pwd:#cred.password == password:
        return newtoken(db, cred)
    else:
        return None

def register(username, password):
    persondb = person_setup()
    creddb = cred_setup()
    person = persondb.query(Person).get(username) # need to be changed to person

    if person:
        return None

    newperson = Person()
    newcred = Cred()
    newperson.username = username
    newcred.username = username

    newcred.password, newcred.salt = hash_pwd(password)    
    
    persondb.add(newperson)
    creddb.add(newcred)
    persondb.commit()

    creddb.commit()
    return newtoken(creddb, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False

