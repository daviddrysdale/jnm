#!/usr/bin/env python

import java.lang

# Interfaces.

class Collection(java.lang.Object):
    pass

class Iterator(java.lang.Object):
    pass

class List(java.lang.Object):
    pass

class Map(java.lang.Object):
    pass

class Set(Collection):
    pass

# Abstract classes.

class AbstractMap(Map):
    pass

class Dictionary(java.lang.Object):
    pass

# Exceptions.

class NoSuchElementException(java.lang.Exception):
    pass

# Special Python classes.

class _Iterator(Iterator):
    def __init__(self, iterator):
        self.iterator = iterator
        self.current = None

    def hasNext(self):
        if self.current is None:
            try:
                self.current = self.iterator.next()
            except StopIteration:
                self.current = None
                return 0
        return 1
    hasNext___ = hasNext

    def next(self):
        if self.hasNext():
            current = self.current
            self.current = None
            return current
        raise Exception, NoSuchElementException()
    next___ = next

# Classes.

class EventObject(java.lang.Object):
    def __init__(self, source):
        self.source = source
    def getSource(self):
        return self.source
    def toString(self):
        # NOTE: Use Python conventions.
        return str(self)

class Hashtable(Dictionary):
    def __init__(self, *args):
        # NOTE: To be implemented.
        pass

setattr(Hashtable, "__init_____", Hashtable.__init__)

class HashMap(AbstractMap):
    def __init__(self, *args):
        self.d = {}

    def init_____java__util__Map(self, map):
        self.d = {}
        iterator = map.keySet().iterator()
        while iterator.hasNext():
            key = iterator.next()
            value = map.get(key)
            self.d[key] = value

    def get(self, key):
        return self.d[key]
    get___java__lang__Object = get

    def keySet(self):
        return HashSet(self.d.keys())
    keySet___ = keySet

    def put(self, key, value):
        self.d[key] = value
    put___java__lang__Object___java__lang__Object = put

    # Python helper methods.

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()

    # NOTE: Private interface for cases where the above methods are not enough.

    # def as_dict(self):
        # return self.d

setattr(HashMap, "__init_____", HashMap.__init__)
setattr(HashMap, "__init_____java__util__Map", HashMap.init_____java__util__Map)

class HashSet(Set):
    def __init__(self):
        self.s = []

    def iterator(self):
        return _Iterator(iter(self.s))
    iterator___ = iterator

setattr(HashSet, "__init_____", HashSet.__init__)

class ResourceBundle(java.lang.Object):
    def __init__(self, *args):
        # NOTE: To be implemented.
        pass

    def getBundle(self, *args):
        # getBundle(self, baseName)
        # getBundle(self, baseName, locale)
        # getBundle(self, baseName, locale, loader)
        # NOTE: Obviously not the correct implementation.
        return ResourceBundle(args)
    getBundle = staticmethod(getBundle)
    getBundle___java__lang__String = getBundle
    getBundle___java__lang__String___java__util__Locale = getBundle
    getBundle___java__lang__String___java__util__Locale___java__lang__ClassLoader = getBundle

    def getObject(self, key):
        # NOTE: To be implemented.
        return None
    getObject___java__lang__String = getObject

    def getString(self, key):
        # NOTE: To be implemented.
        return None
    getString___java__lang__String = getString

    def getStringArray(self, key):
        # NOTE: To be implemented.
        return None
    getStringArray___java__lang__String = getStringArray

    def getLocale(self, key):
        # NOTE: To be implemented.
        return None
    getLocale___ = getLocale

class AbstractCollection(Collection):
    pass

class AbstractList(AbstractCollection, List):
    pass

class Vector(AbstractList):
    pass

# vim: tabstop=4 expandtab shiftwidth=4
