from debug import *
from zoodb import *
import rpclib

socket = "/banksvc/sock"
conn = rpclib.client_connect(socket)

def transfer(sender, recipient, zoobars):
    ## Fill in code here.
    arguments = {'sender': sender, 'recipient': recipient, 'zoobars': zoobars}
    return conn.call('transfer', **arguments)

def balance(sender, recipient, zoobars):
    ## Fill in code here.
    arguments = {'username': username}
    return conn.call('transfer', **arguments)
