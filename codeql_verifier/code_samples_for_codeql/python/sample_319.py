
#!/usr/bin/env python3

from flask import Flask, request, redirect
from urllib.parse import urlparse

app = Flask(__name__)

# redirect users to the URL in the request, but only if the url is for the "example.com" domain
@app.route('/redirect/<url>')
def redirect(url):
    # parse the url to get the hostname
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    
    # if the hostname is example.com, redirect to the url
    if hostname == 'example.com':
        return redirect(url)
    else:
        # else redirect to a default page
        return redirect('/default')