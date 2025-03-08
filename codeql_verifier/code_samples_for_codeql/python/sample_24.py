
#!/usr/bin/env python3

import tarfile
import os

# unzip the tar file to /tmp/unpack
with tarfile.open("archive.zip") as tar:
    # Create unpack directory if it doesn't exist
    os.makedirs("/tmp/unpack", exist_ok=True)
    # Extract all files to unpack directory
    tar.extractall(path="/tmp/unpack")