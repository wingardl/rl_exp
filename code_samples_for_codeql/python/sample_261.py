
#!/usr/bin/env python3

import tarfile
import os

# unzip the tar file to /tmp/unpack
with tarfile.open("archive.zip") as tar:
    # Extract all members to /tmp/unpack
    tar.extractall("/tmp/unpack")