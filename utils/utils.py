import hashlib


def calc_md5(filepath):
    with open(filepath, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(4096)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()
    

def get_full_path(basedir, basename):
    md5hash, ext = basename.split(".") 
    return "{}/{}/{}/{}".format(basedir, ext, md5hash[:2], basename)
