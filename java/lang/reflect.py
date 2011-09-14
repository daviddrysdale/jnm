#!/usr/bin/env python

import java.lang

class Class(java.lang.Object):
    def __init__(self, obj):
        self.obj = obj

    def getMethod(self, name, parameterTypes):

        """
        Find the method on this class with the given 'name' and
        'parameterTypes'. Return a Method object.

        Note that this implementation remembers which object was used to obtain
        this class. This allows the Method objects to be called in Python.
        """

        # Build the Python name.

        types = []
        for parameterType in parameterTypes:
            types.append("__".join(parameterType.split(".")))
        method_name = unicode(name) + "___" + "___".join(types)

        # Either return a Method object or raise the appropriate exception.
        try:
            return Method(getattr(self.obj, method_name))
        except AttributeError:
            raise Exception, java.lang.NoSuchMethodException(name)

    getMethod___java__lang__String___java__lang__Class_array_ = getMethod

class Method(java.lang.Object):
    def __init__(self, method):
        self.method = method

    def __call__(self, *args):
        return self.method(*args)

# vim: tabstop=4 expandtab shiftwidth=4
