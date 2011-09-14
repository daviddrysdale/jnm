#!/usr/bin/env python

"Special module used to avoid circular imports."

class Object(object):
    def getClass(self):
        import java.lang.reflect
        return java.lang.reflect.Class(self)
    getClass___ = getClass

# NOTE: Establish a better exception hierarchy.

class Error(Object):
    def __init__(self, *args):
        self.args = args

setattr(Error, "__init_____", Error.__init__)
setattr(Error, "__init_____java__lang__String", Error.__init__)

class Exception(Object):
    def __init__(self, *args):
        self.args = args

setattr(Exception, "__init_____", Exception.__init__)
setattr(Exception, "__init_____java__lang__String", Exception.__init__)

class IndexOutOfBoundsException(Exception):
    pass

setattr(IndexOutOfBoundsException, "__init_____", IndexOutOfBoundsException.__init__)
setattr(IndexOutOfBoundsException, "__init_____java__lang__String", IndexOutOfBoundsException.__init__)

class IllegalArgumentException(Exception):
    pass

setattr(IllegalArgumentException, "__init_____", IllegalArgumentException.__init__)
setattr(IllegalArgumentException, "__init_____java__lang__String", IllegalArgumentException.__init__)

class NoSuchMethodException(Exception):
    pass

setattr(NoSuchMethodException, "__init_____", NoSuchMethodException.__init__)
setattr(NoSuchMethodException, "__init_____java__lang__String", NoSuchMethodException.__init__)

class NullPointerException(Exception):
    pass

setattr(NullPointerException, "__init_____", NullPointerException.__init__)
setattr(NullPointerException, "__init_____java__lang__String", NullPointerException.__init__)

class SecurityException(Exception):
    pass

setattr(SecurityException, "__init_____", SecurityException.__init__)
setattr(SecurityException, "__init_____java__lang__String", SecurityException.__init__)

# vim: tabstop=4 expandtab shiftwidth=4
