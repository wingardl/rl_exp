
#!/usr/bin/env python3

import tarfile
import os

# unzip the tar file to /tmp/unpack
with tarfile.open("archive.zip") as tar:
    os.makedirs('/tmp/unpack', exist_ok=True)
    tar.extractall(path='/tmp/unpack')