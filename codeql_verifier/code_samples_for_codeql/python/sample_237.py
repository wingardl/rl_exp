
#!/usr/bin/env python3

from flask import Flask, request, redirect
from urllib.parse import urlparse

app = Flask(__name__)

# redirect users to the URL in the request, but only if the url is for the "example.com" domain
@app.route('/redirect/<url>')
def redirect_function(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split(':')[0]
    if domain == 'example.com':
        return redirect(url)
    else:
        return redirect('https://example.com/redirect-not-allowed')

if __name__ == '__main__':
    app.run(debug=True)