##Attacking server isolation

## Exercise 1: Attack privilege isolation

## Exercise 2: Attack Credentials

The solution uses random.random() for salt, which is not cryptographically secure:
    
    hashinput = "%s%.10f" % (cred.password, random.random())

## Exercise 3: Attack the Python Sandbox