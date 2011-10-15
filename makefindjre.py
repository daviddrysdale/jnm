#!/usr/bin/env python
import sys
import base64

with open(sys.argv[1], "rb") as f:
    jardata = f.read()
with open(sys.argv[2], "w") as of:
    print >> of, 'FINDJRE_JAR = "%s"' % base64.b64encode(jardata)
