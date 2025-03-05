
#!/usr/bin/env python3

from flask import Flask, request, redirect
import re

app = Flask(__name__)

# define a regex variable "rv" which will check if a URL is for the example.com domain
rv = re.compile(r'^https?://(www[0-9]*\.)?example\.com(/.*)?(\?.*)?$', re.IGNORECASE)

@app.route('/some/path')
def safe(request):
    target = request.args.get('target', '')
    if rv.match(target):
        return redirect(target)
    else:
        return redirect("/")

