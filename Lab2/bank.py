from zoodb import *
from debug import *

import time

def transfer(sender, recipient, zoobars):
    bankdb = bank_setup()
    senderp = bankdb.query(Bank).get(sender)
    recipientp = bankdb.query(Bank).get(recipient)    

    sender_balance = senderp.zoobars - zoobars
    recipient_balance = recipientp.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        raise ValueError()

    senderp.zoobars = sender_balance
    recipientp.zoobars = recipient_balance
    bankdb.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

def newaccount(username):
    bankdb = bank_setup()
    newbank = Bank()
    newbank.username = username
    bankdb.add(newbank)
    bankdb.commit()

def balance(username):
    db = bank_setup()
    person = db.query(Bank).get(username)
    return person.zoobars

def get_log(username):
    db = transfer_setup()
    return db.query(Transfer).filter(or_(Transfer.sender==username,
                                         Transfer.recipient==username))

