from debug import *
from zoodb import *
import rpclib

socket = "/banksvc/sock"
conn = rpclib.client_connect(socket)

def transfer(sender, recipient, zoobars, token):
    if validate(sender, token): # TODO: Check if this is actually working
        arguments = {'sender': sender, 'recipient': recipient, 'zoobars': zoobars}
        return conn.call('transfer', **arguments)
    else:
	return

def balance(username):
    ## Fill in code here.
    arguments = {'username': username}
    return conn.call('balance', **arguments)

def newaccount(username):
    arguments = {'username': username}
    return conn.call('newaccount', **arguments)

def get_log(username):
    arguments = {'username': username}
    return conn.call('get_log', **arguments)

def validate(sender, token):
    arguments = {'username': sender, 'token': token}
    conn2 = rpclib.client_connect("/authsvc/sock")
    return conn2.call('check_token', **arguments)
