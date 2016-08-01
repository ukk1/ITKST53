##Symbolic execution

### Exercise 1
We modified the unsigned average function to use bitwise right shift
or z3.LShR() function:

    u_avg = (a & b) + z3.LShR(a ^ b,1) # Used the formula from Hacker's Delight
    
We found the formula from http://www.informit.com/articles/article.aspx?p=1959565&seqNum=5

### Exercise 2