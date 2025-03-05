
#!/usr/bin/env python3

from flask import Flask, request, redirect
from urllib.parse import urlparse

app = Flask(__name__)

# redirect users to the URL in the request, but only if the url is for the "example.com" domain
@app.route('/redirect/<url>')
def redirect_function(url):
    # parse the URL
    parsed_url = urlparse(url)
    # check if the domain is example.com
    if parsed_url.netloc.endswith('.example.com') or parsed_url.netloc == 'example.com':
        return redirect(url)
    else:
        return redirect('https://example.com/403')