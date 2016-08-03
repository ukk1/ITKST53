##Symbolic execution

### Exercise 1
We modified the unsigned average function to use bitwise right shift
or z3.LShR() function:

    u_avg = (a & b) + z3.LShR(a ^ b,1) # Used the formula from Hacker's Delight
    
We found the formula from http://www.informit.com/articles/article.aspx?p=1959565&seqNum=5

####Challenge
Computing the average of two 32-bit signed integer values:

    t = (a & b) + ((a ^ b) >> 1)
    s_avg = t + (z3.LShR(t,31) & (a ^ b))

The formula was found from the Hacker's Delight: http://www.hackersdelight.org/basics2.pdf in Chapter 2-5 Average of Two Integers

### Exercise 2

    class sym_asterisk(sym_binop):
      def _z3expr(self, printable):
        return z3expr(self.a,printable) * z3expr(self.b, printable)
    
    class sym_slash(sym_binop):
      def _z3expr(self, printable):
        return z3expr(self.a, printable) / z3expr(self.b, printable)
        
    def __mul__(self, o):
      res = self.__v * o
      return concolic_int(sym_asterisk(ast(self), ast(o)), res)
    
    def __div__(self, o):
      res = self.__v / o
      return concolic_int(sym_slash(ast(self), ast(o)), res)
      
### Exercise 3
      
### Exercise 4

    def __len__(self):
      res = len(self.__v)
      return concolic_int(sym_length(ast(self)), res)
      
    def __contains__(self, o):
      res = o in self.__v
      return concolic_bool(sym_contains(ast(self), ast(o)), res)

### Exercise 5

### Exercise 6

### Exercise 7
