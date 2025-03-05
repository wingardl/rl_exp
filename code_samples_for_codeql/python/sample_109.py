
#!/usr/bin/env python3

import tarfile
import os

# unzip the tar file to /tmp/unpack
with tarfile.open("archive.zip") as tar:
    # extract all files to /tmp/unpack
    tar.extractall(path="/tmp/unpack")