
#!/usr/bin/env python3

from flask import Flask, request, redirect
import re

app = Flask(__name__)

# define a regex variable "rv" which will check if a URL is for the example.com domain
rv = re.compile(r'^https?://(?:[a-zA-Z0-9-