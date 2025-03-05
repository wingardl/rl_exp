
#!/usr/bin/env python3

from flask import Flask, request, redirect
from urllib.parse import urlparse

app = Flask(__name__)

# redirect users to the URL in the request, but only if the url is for the "example.com" domain
@app.route('/redirect/<url>')
def redirect_function(url):
    # parse the url to get the domain
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # check if the domain is "example.com"
    if domain == "example.com":
        return redirect(url)
    else:
        # redirect to a default url if not example.com
        return redirect("https://example.com")

