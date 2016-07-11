from debug import *
from zoodb import *
import rpclib

socket = "/authsvc/sock"
conn = rpclib.client_connect(socket)

def login(username, password):
    ## Fill in code here.
    arguments = {'username': username, 'password': password}
    return conn.call('login', **arguments)

def register(username, password):
    ## Fill in code here.
    kwargs = {}#{'username': username, 'password': password}
    kwargs['username'] = username
    kwargs['password'] = password
    return conn.call('register', **kwargs)

def check_token(username, token):
    ## Fill in code here.
    arguments = {'username': username, 'token': token}
    return conn.call('check_token', **arguments)

