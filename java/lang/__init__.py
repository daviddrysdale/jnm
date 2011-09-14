#!/usr/bin/env python

import os
import sys
from java._object import *
import java.io

class Character(Object):
    def __init__(self, value):
        raise NotImplementedError, "__init__"

    def charValue(self):
        raise NotImplementedError, "charValue"
    charValue___ = charValue

    def hashCode(self):
        raise NotImplementedError, "hashCode"
    hashCode___ = hashCode

    def equals(self, anObject):
        raise NotImplementedError, "equals"
    equals___java__lang__Object = equals

    def toString(self):
        raise NotImplementedError, "toString"
    toString___ = toString

    def isLowerCase(self, ch):
        raise NotImplementedError, "isLowerCase"
    isLowerCase____C_ = staticmethod(isLowerCase)

    def isUpperCase(self, ch):
        raise NotImplementedError, "isUpperCase"
    isUpperCase____C_ = staticmethod(isUpperCase)

    def isTitleCase(self, ch):
        raise NotImplementedError, "isTitleCase"
    isTitleCase____C_ = staticmethod(isTitleCase)

    def isDigit(self, ch):
        raise NotImplementedError, "isDigit"
    isDigit____C_ = staticmethod(isDigit)

    def isDefined(self, ch):
        raise NotImplementedError, "isDefined"
    isDefined____C_ = staticmethod(isDefined)

    def isLetter(self, ch):
        raise NotImplementedError, "isLetter"
    isLetter____C_ = staticmethod(isLetter)

    def isLetterOrDigit(self, ch):
        raise NotImplementedError, "isLetterOrDigit"
    isLetterOrDigit____C_ = staticmethod(isLetterOrDigit)

    def isJavaLetter(self, ch):
        raise NotImplementedError, "isJavaLetter"
    isJavaLetter____C_ = staticmethod(isJavaLetter)

    def isJavaLetterOrDigit(self, ch):
        raise NotImplementedError, "isJavaLetterOrDigit"
    isJavaLetterOrDigit____C_ = staticmethod(isJavaLetterOrDigit)

    def isJavaIdentifierStart(self, ch):
        raise NotImplementedError, "isJavaIdentifierStart"
    isJavaIdentifierStart____C_ = staticmethod(isJavaIdentifierStart)

    def isJavaIdentifierPart(self, ch):
        raise NotImplementedError, "isJavaIdentifierPart"
    isJavaIdentifierPart____C_ = staticmethod(isJavaIdentifierPart)

    def isUnicodeIdentifierStart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierStart"
    isUnicodeIdentifierStart____C_ = staticmethod(isUnicodeIdentifierStart)

    def isUnicodeIdentifierPart(self, ch):
        raise NotImplementedError, "isUnicodeIdentifierPart"
    isUnicodeIdentifierPart____C_ = staticmethod(isUnicodeIdentifierPart)

    def isIdentifierIgnorable(self, ch):
        raise NotImplementedError, "isIdentifierIgnorable"
    isIdentifierIgnorable____C_ = staticmethod(isIdentifierIgnorable)

    def toLowerCase(self, ch):
        raise NotImplementedError, "toLowerCase"
    toLowerCase____C_ = staticmethod(toLowerCase)

    def toUpperCase(self, ch):
        raise NotImplementedError, "toUpperCase"
    toUpperCase____C_ = staticmethod(toUpperCase)

    def toTitleCase(self, ch):
        raise NotImplementedError, "toTitleCase"
    toTitleCase____C_ = staticmethod(toTitleCase)

    def digit(self, ch, radix):
        raise NotImplementedError, "digit"
    digit____C_____I_ = staticmethod(digit)

    def getNumericValue(self, ch):
        raise NotImplementedError, "getNumericValue"
    getNumericValue____C_ = staticmethod(getNumericValue)

    def isSpace(self, ch):
        raise NotImplementedError, "isSpace"
    isSpace____C_ = staticmethod(isSpace)

    def isSpaceChar(self, ch):
        raise NotImplementedError, "isSpaceChar"
    isSpaceChar____C_ = staticmethod(isSpaceChar)

    def isWhitespace(self, ch):
        raise NotImplementedError, "isWhitespace"
    isWhitespace____C_ = staticmethod(isWhitespace)

    def isISOControl(self, ch):
        raise NotImplementedError, "isISOControl"
    isISOControl____C_ = staticmethod(isISOControl)

    def getType(self, ch):
        raise NotImplementedError, "getType"
    getType____C_ = staticmethod(getType)

    def forDigit(self, ch, radix):
        raise NotImplementedError, "forDigit"
    forDigit____C_____I_ = staticmethod(forDigit)

    def compareTo(self, *args):
        # compareTo(self, anotherCharacter)
        # compareTo(self, o)
        raise NotImplementedError, "compareTo"
    compareTo____C_ = compareTo
    compareTo___java__lang__Object = compareTo

setattr(Character, "__init____C_", Character.__init__)

class Class(Object):
    def forName(className):
        parts = unicode(className).split(".")
        obj = __import__(".".join(parts[:-1]), globals(), {}, [])
        for part in parts[1:]:
            obj = getattr(obj, part)
        return obj

    forName___java__lang__String = staticmethod(forName)
    # NOTE: To be enhanced.
    forName___java__lang__String____Z____java__lang__ClassLoader = staticmethod(forName)

class ClassLoader(Object):
    pass

class Integer(Object):
    def init_int(self, i):
        self.i = i

    def init_String(self, s):
        self.i = int(s.value)

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], int):
            self.init_int(args[0])
        elif len(args) == 1 and isinstance(args[0], String):
            self.init_String(args[0])

    def toString(self):
        return String(str(self.i))
    toString___ = toString

setattr(Integer, "__init______I_", Integer.init_int)
setattr(Integer, "__init_____java__lang__String", Integer.init_String)

class String(Object):

    # NOTE: This method should not be needed, really.
    def __str__(self):
        return self.value.encode("utf-8")

    def __unicode__(self):
        return self.value

    def init_empty(self):
        "__init__(self)"
        self.value = u""

    def init_String(self, obj):
        "__init__(self, original)"
        self.value = obj.value

        # __init__(self, value)
        # __init__(self, value, offset, count)
        # __init__(self, ascii, hibyte, offset, count)
        # __init__(self, ascii, hibyte)
        # __init__(self, bytes, offset, length, enc)
        # __init__(self, bytes, enc)
        # __init__(self, bytes, offset, length)
        # __init__(self, bytes)
        # __init__(self, buffer)

    def __init__(self, *args):

        "Python string initialisation only."

        if len(args) == 0:
            self.init_empty()
        elif len(args) == 1 and isinstance(args[0], str):
            self.value = unicode(args[0])
        elif len(args) == 1 and isinstance(args[0], unicode):
            self.value = args[0]
        elif len(args) == 1 and isinstance(args[0], String):
            self.init_String(args[0])

    def length(self):
        return len(self.value)
    length___ = length

    def charAt(self, index):
        return ord(self.value[index])
    charAt____I_ = charAt

    def getChars(self, srcBegin, srcEnd, dst, dstBegin):
        raise NotImplementedError, "getChars"
    getChars____I_____I_____C__array_____I_ = getChars

    def getBytes(self, *args):
        # void getBytes(self, srcBegin, srcEnd, dst, dstBegin)
        # byte[] getBytes(self, enc)
        # byte[] getBytes(self)
        raise NotImplementedError, "getBytes"
    getBytes___ = getBytes
    getBytes____I_____I_____B__array_____I_ = getBytes

    def equals(self, anObject):
        return isinstance(anObject, self.__class__) and self.value == anObject.value
    equals___java__lang__Object = equals

    def compareTo(self, obj):
        if self.value < obj.value:
            return -1
        elif self.value == obj.value:
            return 0
        else:
            return 1
    compareTo___java__lang__String = compareTo

    # NOTE: Comparator defined using private classes. This implementation just
    # NOTE: uses Python's lower method.
    def compareToIgnoreCase(self, str):
        value = self.value.lower()
        value2 = str.value.lower()
        if value < value2:
            return -1
        elif value == value2:
            return 0
        else:
            return 1
    compareToIgnoreCase___java__lang__String = compareToIgnoreCase

    # NOTE: Comparator defined using private classes. This implementation just
    # NOTE: uses Python's lower method.
    def equalsIgnoreCase(self, anotherString):
        value = self.value.lower()
        value2 = anotherString.value.lower()
        return value == value2
    equalsIgnoreCase___java__lang__String = equalsIgnoreCase

    def regionMatches(self, *args):
        # regionMatches(self, toffset, other, ooffset, len)
        # regionMatches(self, ignoreCase, toffset, other, ooffset, len)
        raise NotImplementedError, "regionMatches"

    def startsWith(self, *args):
        # startsWith(self, prefix, toffset)
        # startsWith(self, prefix)
        raise NotImplementedError, "startsWith"

    def endsWith(self, suffix):
        raise NotImplementedError, "endsWith"

    def hashCode(self):
        raise NotImplementedError, "hashCode"

    def indexOf____I_(self, ch):
        return self.value.find(chr(ch))

    def indexOf____I_____I_(self, ch, fromIndex):
        return self.value.find(chr(ch), fromIndex)

    def indexOf___java__lang__String___(self, str):
        return self.value.find(str.value)

    def indexOf___java__lang__String____I_(self, str, fromIndex):
        return self.value.find(str.value, fromIndex)

    def lastIndexOf(self, *args):
        # lastIndexOf(self, ch)
        # lastIndexOf(self, ch, fromIndex)
        # lastIndexOf(self, str)
        # lastIndexOf(self, str, fromIndex)
        raise NotImplementedError, "lastIndexOf"

    def substring(self, *args):
        # substring(self, beginIndex)
        # substring(self, beginIndex, endIndex)
        raise NotImplementedError, "substring"

    def concat(self, str):
        raise NotImplementedError, "concat"

    def replace(self, oldChar, newChar):
        raise NotImplementedError, "replace"

    def toLowerCase(self, *args):
        # toLowerCase(self, locale)
        # toLowerCase(self)
        raise NotImplementedError, "toLowerCase"

    def toUpperCase(self, *args):
        # toUpperCase(self, locale)
        # toUpperCase(self)
        raise NotImplementedError, "toUpperCase"

    def trim(self):
        raise NotImplementedError, "trim"

    def toString(self):
        return self

    def toCharArray(self):
        raise NotImplementedError, "toCharArray"

    def valueOf(self, *args):
        # valueOf(self, obj)
        # valueOf(self, data)
        # valueOf(self, data, offset, count)
        # valueOf(self, b)
        # valueOf(self, c)
        # valueOf(self, l)
        # valueOf(self, f)
        # valueOf(self, d)
        raise NotImplementedError, "valueOf"
    valueOf = staticmethod(valueOf)

    def copyValueOf(self, *args):
        # copyValueOf(self, data, offset, count)
        # copyValueOf(self, data)
        raise NotImplementedError, "copyValueOf"
    copyValueOf = staticmethod(copyValueOf)

    def intern(self):
        raise NotImplementedError, "intern"

setattr(String, "__init_____", String.init_empty)
setattr(String, "__init_____java__lang__String", String.init_String)

class StringBuffer(Object):

    "Used when adding String objects."

    def __unicode__(self):
        return u"".join(self.buffer)

    def __str__(self):
        unicode(self).encode("utf-8")

    def init_empty(self):
        self.buffer = []

    def init_int(self, length):
        self.buffer = []

    def init_String(self, s):
        self.buffer = [unicode(s)]

    def __init__(self, *args):
        if len(args) == 0:
            self.init_empty()
        elif len(args) == 1 and isinstance(args[0], int):
            self.init_int(args[0])
        elif len(args) == 1 and isinstance(args[0], String):
            self.init_String(args[0])

    def append(self, s):
        sb = StringBuffer(String(unicode(self) + unicode(s)))
        return sb
    append____Z_ = append
    append____C_ = append
    append____C__array_ = append
    append____C__array_____I_____I_ = append
    append____D_ = append
    append____F_ = append
    append____I_ = append
    append____J_ = append
    append___java__lang__Object = append
    append___java__lang__String = append

    def toString(self):
        return String("".join(self.buffer))
    toString___ = toString

setattr(StringBuffer, "__init_____", StringBuffer.init_empty)
setattr(StringBuffer, "__init______I_", StringBuffer.init_int)
setattr(StringBuffer, "__init_____java__lang__String", StringBuffer.init_String)

class System(Object):
    # NOTE: Fix this - circular import nonsense!
    in_ = java.io.InputStream(sys.stdin)
    out = java.io.PrintStream(sys.stdout)
    err = java.io.PrintStream(sys.stderr)

    def getProperty___java__lang__String(key):
        try:
            return os.environ[key]
        except KeyError:
            return None

    getProperty___java__lang__String = staticmethod(getProperty___java__lang__String)

setattr(System, "in", System.in_)

# vim: tabstop=4 expandtab shiftwidth=4
