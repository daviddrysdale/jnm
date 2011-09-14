#!/usr/bin/env python

import java.lang

class FilterOutputStream(java.lang.Object):
    def __init__(self, out):
        self.out = out
    def write(self, value, *args):
        if args:
            start, length = args
            self.out.write(value[start:start+length])
        else:
            self.out.write(value)
    def flush(self):
        self.out.flush()
    def close(self):
        self.out.close()

class InputStream(java.lang.Object):
    def read(self, *args):
        raise NotImplementedError, "read"
    def skip(self, n):
        raise NotImplementedError, "skip"
    def available(self):
        raise NotImplementedError, "available"
    def close(self):
        raise NotImplementedError, "close"
    def mark(self, readlimit):
        raise NotImplementedError, "mark"
    def reset(self):
        raise NotImplementedError, "reset"
    def markSupported(self):
        raise NotImplementedError, "markSupported"

class MessageFormat(java.lang.Object):
    def __init__(self, pattern):
        self.pattern = pattern

    def applyPattern(self, pattern):
        self.pattern = pattern
    applyPattern___java__lang__String = applyPattern

    def equals(self, obj):
        return self == obj
    equals___java__lang__Object = equals

    def format(self, *args):
        raise NotImplementedError, "format"
    format___java__lang__Object_array____java__lang__StringBuffer___java__text__FieldPosition = format
    format___java__lang__Object___java__lang__StringBuffer___java__text__FieldPosition = format

    def format__static(pattern, arguments):
        mf = MessageFormat(pattern)
        # NOTE: To be implemented.
        return ""
    format___java__lang__String___java__lang__Object_array_ = staticmethod(format__static)

    def getFormats(self):
        raise NotImplementedError, "getFormats"
    getFormats___ = getFormats

    def getLocale(self):
        raise NotImplementedError, "getLocale"
    getLocale___ = getLocale
    
setattr(MessageFormat, "__init_____java__lang__String", MessageFormat.__init__)

class OutputStream(java.lang.Object):
    def write(self, b, *args):
        raise NotImplementedError, "write"
    def flush(self):
        raise NotImplementedError, "flush"
    def close(self):
        raise NotImplementedError, "close"

# vim: tabstop=4 expandtab shiftwidth=4
