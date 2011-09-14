#!/usr/bin/env python

from java._object import Object, NullPointerException, IndexOutOfBoundsException, Exception as _Exception

class InputStream(Object):
    def __init__(self, stream):
        # NOTE: Python-only method.
        self.stream = stream
    def read___(self):
        s = self.stream.read(1)
        if s != "":
            return -1
        else:
            return ord(s)
    def read____B__array_(self, b, off=0, length=None):
        if b is None:
            raise Exception, NullPointerException()
        if len(b) == 0:
            return 0
        if length is None:
            length = len(b)
        elif length + off > len(b):
            raise Exception, IndexOutOfBoundsException()
        s = self.stream.read(length)
        if s == "":
            return -1
        for i in range(0, length):
            b[i + off] = s[i]
        return len(s)
    read____B__array_____I_____I_ = read____B__array_ 
    def skip(self, n):
        number = 0
        for i in range(0, n):
            s = self.stream.read(1)
            if s == "":
                break
            number += 1
        return number
    skip____L_ = skip
    def available(self):
        raise NotImplementedError, "available"
    available___ = available
    def close(self):
        self.stream.close()
    close___ = close
    def mark(self, readlimit):
        raise NotImplementedError, "mark"
    mark___ = mark
    def reset(self):
        raise NotImplementedError, "reset"
    reset___ = reset
    def markSupported(self):
        raise NotImplementedError, "markSupported"
    markSupported___ = markSupported

class IOException(_Exception):
    def __init__(self, *args):
        self.args = args

setattr(IOException, "__init_____", IOException.__init__)
setattr(IOException, "__init_____java__lang__String", IOException.__init__)

class OutputStream(Object):
    def write(self, b, *args):
        raise NotImplementedError, "write"
    write___java__lang__String = write
    def flush(self):
        raise NotImplementedError, "flush"
    flush___ = flush
    def close(self):
        raise NotImplementedError, "close"
    close___ = close

class FilterOutputStream(OutputStream):
    def __init__(self, out):
        self.out = out
    def write(self, value, *args):
        if args:
            start, length = args
            self.out.write(value[start:start+length])
        else:
            self.out.write(value)
    write___java__lang__String = write
    write___java__lang__String____I_____I_ = write
    def flush(self):
        self.out.flush()
    flush___ = flush
    def close(self):
        self.out.close()
    close___ = close

setattr(FilterOutputStream, "__init_____java__io__OutputStream", FilterOutputStream.__init__)

class PrintStream(FilterOutputStream):
    def init__out(self, out):
        FilterOutputStream.__init__(self, out)
    def init__out_autoFlush(self, out, autoFlush):
        FilterOutputStream.__init__(self, out)
        self.autoFlush = autoFlush
    def checkError(self):
        # NOTE: Implement properly.
        self.flush()
    checkError___ = checkError
    def close(self):
        self.flush()
        FilterOutputStream.close(self)
    close___ = close
    def flush(self):
        FilterOutputStream.flush(self)
    flush___ = flush
    def print_(self, obj, ending=""):
        # NOTE: Check for arrays.
        if isinstance(obj, list):
            for i in obj:
                self.print_(i, ending)
        else:
            # NOTE: Using Python string conversion.
            FilterOutputStream.write(self, unicode(obj) + ending)
    print____Z_ = print_
    print____C_ = print_
    print____C__array_ = print_
    print____D_ = print_
    print____F_ = print_
    print____I_ = print_
    print____L_ = print_
    print___java__lang__Object = print_
    print___java__lang__String = print_

    def println(self, obj):
        self.print_(obj, "\n")
    println____Z_ = println
    println____C_ = println
    println____C__array_ = println
    println____D_ = println
    println____F_ = println
    println____I_ = println
    println____L_ = println
    println___java__lang__Object = println
    println___java__lang__String = println

    # NOTE: To be completed.

setattr(PrintStream, "__init_____java__io__OutputStream", PrintStream.init__out)
setattr(PrintStream, "__init_____java__io__OutputStream____Z_", PrintStream.init__out_autoFlush)

# vim: tabstop=4 expandtab shiftwidth=4
