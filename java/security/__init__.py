#!/usr/bin/env python

import java.lang

class AccessControlContext(java.lang.Object):
    def __init__(self):
        # NOTE: Python-only method.
        self.acc = None
        self.combiner = None
        self.context = None
    def init__acc_combiner(self, acc, combiner):
        self.acc = acc
        self.combiner = combiner
        self.context = None
    def init__context(self, context):
        self.acc = None
        self.combiner = None
        self.context = context
    def checkPermission(self, perm):
        # NOTE: Implement properly.
        pass
    checkPermission___java__security__Permission = checkPermission
    def equals(self, obj):
        return self.context == obj.context
    equals___java__lang__Object = equals
    def getDomainCombiner(self):
        return self.combiner
    getDomainCombiner___java__security__DomainCombiner = getDomainCombiner
    def hashCode(self):
        # NOTE: Using Python hash function.
        return hash(self)
    hashCode___ = hashCode

setattr(AccessControlContext, "__init_____java__security__AccessControlContext___java__security__DomainCombiner",
    AccessControlContext.init__acc_combiner)
setattr(AccessControlContext, "__init_____java__security__ProtectionDomain_array_", AccessControlContext.init__context)

class AccessController(java.lang.Object):
    def checkPermission(perm):
        # NOTE: Implement properly.
        pass
    checkPermission___java__security__Permission = staticmethod(checkPermission)
    def doPrivileged(action, context=None):
        # NOTE: Implement properly.
        return action.run___()
    doPrivileged___java__security__PrivilegedAction = staticmethod(doPrivileged)
    doPrivileged___java__security__PrivilegedAction___java__security__AccessControlContext = staticmethod(doPrivileged)
    def getContext():
        # NOTE: Implement properly.
        return AccessControlContext()

class SecureClassLoader(java.lang.ClassLoader):
    pass

# vim: tabstop=4 expandtab shiftwidth=4
