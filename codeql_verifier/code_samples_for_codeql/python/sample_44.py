
#!/usr/bin/env python3

import tarfile
import os

# unzip the tar file to /tmp/unpack
with tarfile.open("archive.zip") as tar:
    tar.extractall(path="/tmp/unpack")