#!/usr/bin/env python
# Copyright (C) 2004, 2005, 2006, 2011 Paul Boddie <paul@boddie.org.uk>
# Copyright (C) 2010 Braden Thomas <bradenthomas@me.com>
# Copyright (C) 2011 David Drysdale <dmd@lurklurk.org>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import struct
import getopt

import jvmspec
from jvmspec import fqcn
from jvmspec import demangle_method_descriptor
from jvmspec import demangle_field_descriptor
from jvmspec import size_field_descriptor
from classfile import (ClassInfo, FieldRefInfo, MethodRefInfo,
                       DoubleInfo, FieldInfo, MethodInfo,
                       CodeAttributeInfo, ExceptionsAttributeInfo,
                       ClassFile)
from jarfile import jar_classes


class Symbol(object):
    """Class describing a symbol or symbol reference"""

    # Type characters; lowercase for local (=private), uppercase for external
    # (protected/public)
    CLASS = u'C'
    DATA = u'D'
    CODE = u'T'
    # Instance data has no equivalent in C -- fields in dynamically allocated
    # objects are accessed by calculating their offset using the header file
    # definition.  However, Java allows symbolic access to per-object fields,
    # so need to show them in the output.
    INSTANCE_DATA = u'I'

    UNDEFINED = u'U'
    # References in code to other data/code.
    REF_CLASS = u'K'
    REF_DATA = u'F'
    REF_CODE = u'R'
    REF_INSTANCE_DATA = u'J'

    DEF_SYMTYPES = set((CLASS, DATA, CODE, INSTANCE_DATA))
    REF_SYMTYPES = set((REF_CLASS, REF_DATA, REF_CODE, REF_INSTANCE_DATA))

    def __init__(self, value, symtype, jcls, symname, descriptor):
        self.value = value
        self.symtype = symtype
        # Class owning the symbol
        self.jcls = jcls
        # Unqualified name of the symbol.  Non-unique even within a class
        # (method overloading means that the signature is needed for
        # uniqueness)
        self.symname = symname
        # Descriptor of the symbol (None for Classes)
        self.descriptor = descriptor

        if self.symtype.upper() == Symbol.CLASS or self.symtype.upper() == Symbol.REF_CLASS:
            self.unique_name = self.jcls
        else:
            self.unique_name = "%s.%s:%s" % (self.jcls, self.symname, self.descriptor)
            # (don't actually need the :<descriptor> suffix to make fields unique)

    def __hash__(self):
        return hash(self.value) ^ hash(self.symtype) ^ hash(self.unique_name)

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return (self.value == other.value and
                self.symtype == other.symtype and
                self.unique_name == other.unique_name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __unicode__(self):
        if self.value is None:
            intro = u"        "
        else:
            intro = u"%08x" % self.value
        if self.symtype.upper() == Symbol.CLASS or self.symtype.upper() == Symbol.REF_CLASS:
            return u"%s %s %s" % (intro, self.symtype, self.jcls)
        else:
            return u"%s %s %s.%s:%s" % (intro, self.symtype, self.jcls, self.symname, self.descriptor)

    def demangled(self):
        if self.value is None:
            intro = u"        "
        else:
            intro = u"%08x" % self.value
        if self.symtype.upper() == Symbol.CLASS or self.symtype.upper() == Symbol.REF_CLASS:
            return u"%s %s %s" % (intro, self.symtype, self.jcls)
        elif self.symtype.upper() == Symbol.CODE or self.symtype.upper() == Symbol.REF_CODE:
            params, return_type = demangle_method_descriptor(self.descriptor)
            return u"%s %s %s %s.%s(%s)" % (intro, self.symtype, return_type, self.jcls, self.symname, u", ".join(params))
        else:  # field, static or otherwise
            field_type, _ = demangle_field_descriptor(self.descriptor)
            return u"%s %s %s %s.%s" % (intro, self.symtype, field_type, self.jcls, self.symname)


def adjust_visibility(t_code, access_flags):
    if access_flags & jvmspec.PRIVATE:
        return t_code.lower()
    else:
        return t_code.upper()


def findref(jcls, ii):
    """Returns descriptor, class, name for referenced constant"""
    const = jcls.constants[ii - 1]
    if isinstance(const, ClassInfo):
        class_desc = unicode(const)
        if class_desc[0] != u"[":
            # Plain old class name
            return None, fqcn(class_desc), None
        else:
            ii = 0
            while class_desc[ii] == u"[":
                ii += 1
            if class_desc[ii] != u"L":
                # Not interested in arrays of primitive types
                return None, None, None
            else:
                # Array of objects
                return None, fqcn(class_desc), None
    elif isinstance(const, FieldRefInfo):
        return const.get_descriptor(), fqcn(unicode(const.get_class())), const.get_name()
    elif isinstance(const, MethodRefInfo):
        return const.get_descriptor(), fqcn(unicode(const.get_class())), const.get_name()
    else:
        return None, None, None


# We don't need no stinking Visitor pattern
def _FieldInfo_dump(self):
    if self.access_flags & jvmspec.STATIC:
        symtype = Symbol.DATA
    else:
        symtype = Symbol.INSTANCE_DATA
    jcls = fqcn(unicode(self.class_file.this_class))
    symname = unicode(self.class_file.constants[self.name_index - 1])
    fullname = u"%s.%s" % (jcls, symname)
    descriptor = self.get_descriptor()
    return Symbol(size_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1])),
                  adjust_visibility(symtype, self.access_flags),
                  jcls,
                  symname,
                  descriptor)
FieldInfo.dump = _FieldInfo_dump


def _MethodInfo_dump(self):
    # Find the Code attribute
    size = None
    code_attr = None
    exc_attr = None
    for attr in self.attributes:
        if isinstance(attr, CodeAttributeInfo):
            code_attr = attr
            size = len(attr.code)
        elif isinstance(attr, ExceptionsAttributeInfo):
            exc_attr = attr
    jcls = fqcn(unicode(self.class_file.this_class))
    symname = unicode(self.class_file.constants[self.name_index - 1])
    fullname = u"%s.%s" % (jcls, symname)
    descriptor = self.get_descriptor()
    params, return_type = jvmspec.demangle_method_descriptor(descriptor)
    results = [Symbol(size,
                      adjust_visibility(Symbol.CODE, self.access_flags),
                      jcls,
                      symname,
                      self.get_descriptor())]
    if code_attr is not None:
        results.extend(code_attr.dump())
    if exc_attr is not None:
        results.extend(exc_attr.dump())
    return results
MethodInfo.dump = _MethodInfo_dump


def _CodeAttributeInfo_dump(self):
    results = []
    ii = 0
    while ii < len(self.code):
        opcode = ord(self.code[ii])
        if opcode not in jvmspec.BYTECODES:
            raise Exception("Unknown opcode %d" % opcode)
        op_name, op_size, struct_code, info_types = jvmspec.BYTECODES[opcode]
        assert len(struct_code) == len(info_types)
        if op_name == "tableswitch":
            # expect 0 byte pads to next 4-byte boundary
            num_zeros = (4 - ((ii + 1) % 4)) % 4
            args_offset = ii + 1 + num_zeros
            assert (args_offset % 4) == 0
            default, low, high = struct.unpack(">iii",
                                               self.code[args_offset:args_offset + 12])
            num_offsets = high - low + 1
            op_size = num_zeros + (3 + num_offsets) * 4
            struct_code = num_zeros * "B" + "iii" + num_offsets * "i"
            info_types = num_zeros * "0" + "###" + num_offsets * "o"
        elif op_name == "lookupswitch":
            # expect 0 byte pads to next 4-byte boundary
            num_zeros = (4 - ((ii + 1) % 4)) % 4
            args_offset = ii + 1 + num_zeros
            assert (args_offset % 4) == 0
            default, npairs = struct.unpack(">ii",
                                            self.code[args_offset:args_offset + 8])
            op_size = num_zeros + (2 + 2 * npairs) * 4
            struct_code = num_zeros * "B" + "ii" + npairs * "ii"
            info_types = num_zeros * "0" + "##" + npairs * "#o"
        elif op_name == "wide":
            ii += 1  # move past "wide" opcode
            opcode = ord(self.code[ii])
            if opcode == 132:  # iinc
                op_size = 4
                struct_code = "Hh"
                info_types = "l#"
            else:  # *load, *store or ret
                op_size = 2
                struct_code = "H"
                info_types = "l"
        assert op_size is not None, "Unexpected unknown size for opcode %d" % opcode
        values = struct.unpack(">" + struct_code,
                               self.code[ii + 1: ii + 1 + op_size])
        # Look for instructions that reference data or code
        symtype = None
        if op_name in ("anewarray", "checkcast", "instanceof", "multianewarray", "new"):
            # reference to class, array or interface type
            symtype = Symbol.REF_CLASS
        elif op_name in ("ldc", "ldc_w"):
            # reference to primitive constant, string literal or class
            symtype = Symbol.REF_CLASS
        elif op_name in ("invokeinterface", "invokespecial", "invokestatic", "invokevirtual"):
            # reference to a method
            symtype = Symbol.REF_CODE
        elif op_name in ("getfield", "putfield"):
            # reference to an instance field
            symtype = Symbol.REF_INSTANCE_DATA
        elif op_name in ("getstatic", "putstatic"):
            # reference to a static field
            symtype = Symbol.REF_DATA
        if symtype is not None:
            assert info_types[0] == "c"
            descriptor, jcls, symname = findref(self.class_file, values[0])
            if jcls is not None:
                if symtype == Symbol.REF_DATA or symtype == Symbol.REF_INSTANCE_DATA:
                    results.append(Symbol(None, symtype, jcls, symname, descriptor))
                elif symtype == Symbol.REF_CODE:
                    results.append(Symbol(None, symtype, jcls, symname, descriptor))
                else:  # Symbol.REF_CLASS
                    results.append(Symbol(None, symtype, jcls, jcls, None))
        ii += op_size + 1
    for exc in self.exception_table:
        if exc.catch_type != 0:
            descriptor, jcls, symname = findref(self.class_file, exc.catch_type)
            results.append(Symbol(None, Symbol.REF_CLASS, jcls, jcls, None))
    return results
CodeAttributeInfo.dump = _CodeAttributeInfo_dump


def _ExceptionsAttributeInfo_dump(self):
    results = []
    for exc_idx in self.exception_index_table:
        descriptor, jcls, name = findref(self.class_file, exc_idx)
        results.append(Symbol(None, Symbol.REF_CLASS, jcls, jcls, None))
    return results
ExceptionsAttributeInfo.dump = _ExceptionsAttributeInfo_dump


_class_parent = {}  # classname: classname for superclass
_class_interfaces = {}  # classname: list of classnames for implemented interfaces


def _ClassFile_dump(self):
    jcls = fqcn(unicode(self.this_class))
    super_class = fqcn(unicode(self.super_class))
    results = [Symbol(self.size, Symbol.CLASS, jcls, jcls, None),
               Symbol(None, Symbol.REF_CLASS, super_class, super_class, None)]
    results.extend([Symbol(None,
                           Symbol.REF_CLASS,
                           fqcn(unicode(interf)),
                           fqcn(unicode(interf)),
                           None) for interf in self.interfaces])
    _class_parent[fqcn(unicode(self.this_class))] = super_class
    _class_interfaces[fqcn(unicode(self.this_class))] = [fqcn(unicode(interf)) for interf in self.interfaces]
    for f in self.fields:
        f_info = f.dump()
        if f_info is not None:
            results.append(f_info)
    for m in self.methods:
        m_info = m.dump()
        if m_info is not None:
            results.extend(m_info)
    return results
ClassFile.dump = _ClassFile_dump


# Filter functions; take a list of 3-tuples (jarfile, classfile, symbol)
def resolve_class(symlist):
    """Remove duplicate symbol info and resolve internal references within each class"""
    # Remove duplicates and track definitions
    deduped = []
    # Each of the following maps from (jarfile, classfile) to a map of name: symbol
    seen = {}
    fields = {}
    methods = {}
    classes = {}
    for jarfile, classfile, syminfo in symlist:
        jcls = (jarfile, classfile)
        if jcls not in seen:
            seen[jcls] = set()
            fields[jcls] = {}
            methods[jcls] = {}
            classes[jcls] = {}
        if syminfo not in seen[jcls]:
            seen[jcls].add(syminfo)
            deduped.append((jarfile, classfile, syminfo))
            if syminfo.symtype.upper() == Symbol.CLASS:
                classes[jcls][syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.DATA:
                fields[jcls][syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.INSTANCE_DATA:
                fields[jcls][syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.CODE:
                methods[jcls][syminfo.unique_name] = syminfo

    # Remove references where there is a matching definition
    resolved = []
    for jarfile, classfile, syminfo in deduped:
        jcls = (jarfile, classfile)
        if (syminfo.symtype.upper() == Symbol.REF_CLASS and
            syminfo.unique_name in classes[jcls]):
            pass
        elif (syminfo.symtype.upper() == Symbol.REF_DATA and
              syminfo.unique_name in fields[jcls]):
            pass
        elif (syminfo.symtype.upper() == Symbol.REF_INSTANCE_DATA and
              syminfo.unique_name in fields[jcls]):
            pass
        elif (syminfo.symtype.upper() == Symbol.REF_CODE and
              syminfo.unique_name in methods[jcls]):
            pass
        else:
            resolved.append((jarfile, classfile, syminfo))
        # Within the scope of a single class, a reference to a field or
        # method of that class may be unresolved, because the field or
        # method is inherited.  We have no way of determining which
        # of the superclass + implemented interfaces the reference comes
        # from.
        #  - Instance fields have to come from a superclass
        #  - Static fields can come from a superclass, or an interface if
        #    they are const
        #  - Methods can come from either a superclass or an interface.
        # So leave the reference as <this_class>.<name>
    return resolved


def find_owner_superclass_interfaces(symbols, syminfo):
    if syminfo.unique_name in symbols:
        return symbols[syminfo.unique_name]
    if syminfo.jcls == "java.lang.Object":
        return None
    potentials = [_class_parent.get(syminfo.jcls, "java.lang.Object")]
    potentials.extend(_class_interfaces.get(syminfo.jcls, []))
    for potential in potentials:
        parent_syminfo = Symbol(syminfo.value,
                                syminfo.symtype,
                                potential,
                                syminfo.symname,
                                syminfo.descriptor)
        parent_resolve = find_owner_superclass_interfaces(symbols, parent_syminfo)
        if parent_resolve is not None:
            return parent_resolve
    return None


def find_owner_superclass(symbols, syminfo):
    if syminfo.unique_name in symbols:
        return symbols[syminfo.unique_name]
    if _class_parent.get(syminfo.jcls, "java.lang.Object") == "java.lang.Object":
        return None
    parent_syminfo = Symbol(syminfo.value,
                            syminfo.symtype,
                            _class_parent[syminfo.jcls],
                            syminfo.symname,
                            syminfo.descriptor)
    return find_owner_field(symbols, parent_syminfo)


def find_owner_field(fields, syminfo):
    assert syminfo.symtype == Symbol.REF_INSTANCE_DATA
    return find_owner_superclass(fields, syminfo)


def find_owner_static_field(fields, syminfo):
    assert syminfo.symtype == Symbol.REF_DATA
    return find_owner_superclass_interfaces(fields, syminfo)


def find_owner_method(methods, syminfo):
    assert syminfo.symtype == Symbol.REF_CODE
    return find_owner_superclass_interfaces(methods, syminfo)


# Filter functions; take a list of 3-tuples (jarfile, classfile, symbol)
def resolve_all(symlist):
    """Remove duplicate symbol info and resolve internal references across all classes"""
    seen = set()
    fields = {}
    methods = {}
    classes = {}
    # Remove duplicates and track definitions
    deduped = []
    for jarfile, classfile, syminfo in symlist:
        if syminfo not in seen:
            seen.add(syminfo)
            deduped.append((jarfile, classfile, syminfo))
            if syminfo.symtype.upper() == Symbol.CLASS:
                classes[syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.DATA:
                fields[syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.INSTANCE_DATA:
                fields[syminfo.unique_name] = syminfo
            elif syminfo.symtype.upper() == Symbol.CODE:
                methods[syminfo.unique_name] = syminfo

    # Remove references where there is a matching definition
    resolved = []
    for jarfile, classfile, syminfo in deduped:
        sym_resolved = False
        if syminfo.symtype.upper() == Symbol.REF_CLASS:
            if syminfo.unique_name in classes:
                sym_resolved = True
        elif syminfo.symtype.upper() == Symbol.REF_DATA:
            if find_owner_static_field(fields, syminfo) is not None:
                sym_resolved = True
        elif syminfo.symtype.upper() == Symbol.REF_INSTANCE_DATA:
            if find_owner_field(fields, syminfo) is not None:
                sym_resolved = True
        elif syminfo.symtype.upper() == Symbol.REF_CODE:
            if find_owner_method(methods, syminfo) is not None:
                sym_resolved = True

        if not sym_resolved:
            resolved.append((jarfile, classfile, syminfo))
    return resolved


def remove_defined(symlist):
    return [sym for sym in symlist if sym[2].symtype.upper() not in Symbol.DEF_SYMTYPES]


def remove_undefined(symlist):
    return [sym for sym in symlist if sym[2].symtype.upper() in Symbol.DEF_SYMTYPES]


def remove_private(symlist):
    return [sym for sym in symlist if sym[2].symtype.isupper()]

# All filter functions in the order they should be applied
ALL_FILTER_FNS = (resolve_class, resolve_all, remove_private, remove_defined, remove_undefined)


# Sort functions; take a list of 3-tuples (jarfile, classfile, symbol)
def alphabetic_sort(symlist):
    return sorted(symlist, key=lambda x: x[2].symname)


def numeric_sort(symlist):
    return sorted(symlist, key=lambda x: x[2].value)


def noop_sort(symlist):
    return symlist


def reverse_sort(symlist):
    symlist.reverse()
    return symlist


# Display functions
def normal_display(jarfile, filename, sym, current):
    return unicode(sym)


def prepend_filename(jarfile, filename, sym, current):
    if jarfile is None:
        return u"%s:%s" % (filename, current)
    else:
        return u"%s:%s:%s" % (jarfile, filename, current)


def name_only(jarfile, filename, sym, current):
    return u"%s" % sym.name


def demangle(jarfile, filename, sym, current):
    return sym.demangled()

# All the display functions, in the order they should be applied
ALL_DISPLAY_FNS = (name_only, normal_display, demangle, prepend_filename)


class _Opts(object):
    # short option, long option, help messsage, filter function, sort function, display function
    OPT_INFO = (("h", "help", "show this help", None, None, None),)

    def __init__(self, message):
        self.message = message
        self.filters = set()
        self.sorts = []
        self.displays = set()

    def short_opts(self):
        return dict([("-%s" % optinfo[0], optinfo) for optinfo in self.OPT_INFO])

    def long_opts(self):
        return dict([("--%s" % optinfo[1], optinfo) for optinfo in self.OPT_INFO])

    def all_opts(self):
        return dict(self.short_opts().items() + self.long_opts().items())

    def usage(self, err):
        """Print usage message"""
        print >> sys.stderr, self.message
        print >> sys.stderr, "Options:"
        for optinfo in self.OPT_INFO:
            if len(optinfo[0]) > 0:
                print >> sys.stderr, "   -%s/--%-16s : %s" % (optinfo[0], optinfo[1], optinfo[2])
            else:
                print >> sys.stderr, "   --%-19s : %s" % (optinfo[1], optinfo[2])
        sys.exit(err)

    def process(self, symlist):
        # Apply filters in order
        for filter in ALL_FILTER_FNS:
            if filter in self.filters:
                symlist = filter(symlist)
        # Special case -- pull reverse_sort to the end
        if reverse_sort in self.sorts:
            self.sorts.remove(reverse_sort)
            self.sorts.append(reverse_sort)
        # Apply sorts in order.
        for sortfn in self.sorts:
            symlist = sortfn(symlist)
        return symlist

    def display(self, jarfile, filename, sym):
        # Apply display functions in order
        result = None
        for dispfn in ALL_DISPLAY_FNS:
            if dispfn in self.displays:
                result = dispfn(jarfile, filename, sym, result)
        return result

    def process_opt(self, opt, arg):
        class_opts = self.all_opts()
        if opt in ("-h", "--help"):
            self.usage(0)
            return True
        elif opt in class_opts:
            optinfo = class_opts[opt]
            if optinfo[3] is not None:
                self.filters.add(optinfo[3])
            if optinfo[4] is not None:
                self.sorts.append(optinfo[4])
            if optinfo[5] is not None:
                self.displays.add(optinfo[5])
            return True
        else:
            return False

    def getopts(self, argv):
        try:
            opts, args = getopt.getopt(argv,
                                       "".join([optinfo[0] for optinfo in self.OPT_INFO]),
                                       [optinfo[1] for optinfo in self.OPT_INFO])
        except getopt.GetoptError:
            self.usage(2)
        for opt, arg in opts:
            if self.process_opt(opt, arg):
                pass
            else:
                print >> sys.stderr, "Unknown option %s" % opt
                self.usage(1)
        return args
