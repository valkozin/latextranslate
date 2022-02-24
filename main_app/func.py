import hashlib
from datetime import datetime
import os

def hash_upload(instance, filename):
    fname, ext = os.path.splitext(filename)
    md5_hash = hashlib.md5()
    now = datetime.now()
    md5_hash.update(filename.encode('utf-8') + now.strftime("%m/%d/%Y, %H:%M:%S").encode('utf-8'))
    return "documents/{0}{1}".format(md5_hash.hexdigest(), ext)
