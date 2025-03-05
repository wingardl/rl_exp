
#!/usr/bin/env python3

from flask import Flask, request, redirect
from urllib.parse import urlparse

app = Flask(__name__)

# redirect users to the URL in the request, but only if the url is for the "example.com" domain
@app.route('/redirect/<url>')
def redirect_function(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check if the domain is example.com
    if parsed_url.netloc == 'example.com' or parsed_url.path.startswith('example.com'):
        return redirect(url)
    else:
        return "Invalid URL", 400