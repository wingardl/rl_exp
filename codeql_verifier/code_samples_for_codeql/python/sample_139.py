
#!/usr/bin/env python3

import os

super_secret_info = "U2FsdGVkX1/R+WzJcxgvX/Iw=="

super_secret_filename = "secret.txt"

# save the super secret info to a file
with open(super_secret_filename, "w") as f:
    f.write(super_secret_info)

# set restricted permissions on the file
os.chmod(super_secret_filename, 0o000) # set to read-only for owner, no permissions for group and others