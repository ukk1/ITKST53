## Place your answers here.

Exercise 1:

I first started to look for any vulnerable functions within the program that are known to be vulnerable to buffer overflows. OWASP states the following: "C library functions such as strcpy (), strcat (), sprintf () and vsprintf () operate on null terminated strings and perform no bounds checking." So these particular functions were the ones I was interested in if they were being used by the program.

[http.c:165] 
The program allocates 8192 bytes for the variable 'buf' and 512 bytes for the variable 'envvar'. The envvar variable can be overwritten by the sprintf function, because it does not perform any bounds checking for the buffer size.

    static char buf[8192];   // Here the program allocates the 8192 bytes for the variable 'buf'
    char envvar[512]; // Here it allocates 512 bytes for the variable 'envvar'
    sprintf(envvar, "HTTP_%s", buf); // Here sprintf will copy the content of envvar to buf

If the input exceeds the 512 byte limit it will overflow the buffer and we as an attacker will have control of the execution of the program. There are also other functions that does not perform bound checking and are prone to buffer overflow related attacks. 

------

[http.c:276]
The program allocates 1024 bytes for a variable 'pn'. Then it uses the vulnerable 'strcat' function to append a string from 'pn' to 'name' variable.

	char pn[1024]; // Here the program allocates the 1024 bytes
	strcat(pn, name); // Here it uses the strcat function to append a copy of the source string to the destination variable 'name'

The strcat function does not perform any bounds checking for the given string. If we as an attacker provide more than the allocated 1024 bytes in the buffer for the 'pn' variable we can overflow the buffer.
