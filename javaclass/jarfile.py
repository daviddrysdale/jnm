import os
import zipfile

import classfile


def jar_classes(filename):
    """Return a list of the classes in a jar file.

    Each entry is a 2-tuple of (filename, ClassFile)"""
    zf = zipfile.ZipFile(filename, "r")
    classes = []
    for info in zf.infolist():
        _, ext = os.path.splitext(info.filename)
        if ext == ".class":
            in_data = zf.open(info).read()
            jc = classfile.ClassFile(in_data)
            classes.append((info.filename, jc))
    zf.close()
    return classes

if __name__ == "__main__":
    import sys
    for name in sys.argv[1:]:
        jclasses = jar_classes(name)
        for filename, jc in jclasses:
            print filename
