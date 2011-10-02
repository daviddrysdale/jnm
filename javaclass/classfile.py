#!/usr/bin/env python

"""
Java class file decoder. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/ClassFile.doc.html

Copyright (C) 2004, 2005, 2006, 2011 Paul Boddie <paul@boddie.org.uk>
Copyright (C) 2010 Braden Thomas <bradenthomas@me.com>
Copyright (C) 2011 David Drysdale <dmd@lurklurk.org>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct

from jvmspec import *


# Utility functions.
def u1(data):
    return struct.unpack(">B", data[0:1])[0]


def u2(data):
    return struct.unpack(">H", data[0:2])[0]


def s2(data):
    return struct.unpack(">h", data[0:2])[0]


def u4(data):
    return struct.unpack(">L", data[0:4])[0]


def s4(data):
    return struct.unpack(">l", data[0:4])[0]


def s8(data):
    return struct.unpack(">q", data[0:8])[0]


def f4(data):
    return struct.unpack(">f", data[0:4])[0]


def f8(data):
    return struct.unpack(">d", data[0:8])[0]


def su1(value):
    return struct.pack(">B", value)


def su2(value):
    return struct.pack(">H", value)


def ss2(value):
    return struct.pack(">h", value)


def su4(value):
    return struct.pack(">L", value)


def ss4(value):
    return struct.pack(">l", value)


def ss8(value):
    return struct.pack(">q", value)


def sf4(value):
    return struct.pack(">f", value)


def sf8(value):
    return struct.pack(">d", value)


def has_flags(flags, desired):
    desired_flags = reduce(lambda a, b: a | b, desired, 0)
    return (flags & desired_flags) == desired_flags


class NameAndTypeUtils(object):
    def get_field_descriptor(self):
        if self.name_and_type_index != 0:
            return self.class_file.constants[self.name_and_type_index - 1].get_field_descriptor()
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

    def get_method_descriptor(self):
        if self.name_and_type_index != 0:
            return self.class_file.constants[self.name_and_type_index - 1].get_method_descriptor()
        else:
            # Some name indexes are zero to indicate special conditions.
            return None

    def get_class(self):
        return self.class_file.constants[self.class_index - 1]

# Symbol parsing.


def get_method_descriptor(s):
    assert(s[0] == "(")
    params = []
    s = s[1:]
    while s[0] != ")":
        parameter_descriptor, s = _get_parameter_descriptor(s)
        params.append(parameter_descriptor)
    if s[1] != "V":
        return_type, s = _get_field_type(s[1:])
    else:
        return_type, s = None, s[1:]
    return params, return_type


def get_field_descriptor(s):
    return _get_field_type(s)[0]


def _get_parameter_descriptor(s):
    return _get_field_type(s)


def _get_component_type(s):
    return _get_field_type(s)


def _get_field_type(s):
    base_type, s = _get_base_type(s)
    object_type = None
    array_type = None
    if base_type == "L":
        object_type, s = _get_object_type(s)
    elif base_type == "[":
        array_type, s = _get_array_type(s)
    return (base_type, object_type, array_type), s


def _get_base_type(s):
    if len(s) > 0:
        return s[0], s[1:]
    else:
        return None, s


def _get_object_type(s):
    if len(s) > 0:
        s_end = s.find(";")
        assert(s_end != -1)
        return s[:s_end], s[(s_end + 1):]
    else:
        return None, s


def _get_array_type(s):
    if len(s) > 0:
        return _get_component_type(s)
    else:
        return None, s


def safe(s):
    if s.find(">") != -1:
        return '"%s"' % s
    else:
        return s


# Constant information.
class ConstantInfo(object):
    TAG = -1


class ClassInfo(ConstantInfo):
    TAG = 7

    def init(self, data, class_file):
        self.class_file = class_file
        self.name_index = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return su2(self.name_index)

    def __str__(self):
        return str(self.class_file.constants[self.name_index - 1])


class RefInfo(ConstantInfo, NameAndTypeUtils):
    def init(self, data, class_file):
        self.class_file = class_file
        self.class_index = u2(data[0:2])
        self.name_and_type_index = u2(data[2:4])
        return data[4:]

    def serialize(self):
        return su2(self.class_index) + su2(self.name_and_type_index)

    def __str__(self):
        return ("%s.%s" %
                (str(self.class_file.constants[self.class_index - 1]),
                 str(self.class_file.constants[self.name_and_type_index - 1])))


class FieldRefInfo(RefInfo):
    TAG = 9

    def get_descriptor(self):
        return RefInfo.get_field_descriptor(self)


class MethodRefInfo(RefInfo):
    TAG = 10

    def get_descriptor(self):
        return RefInfo.get_method_descriptor(self)


class InterfaceMethodRefInfo(MethodRefInfo):
    TAG = 11


class NameAndTypeInfo(ConstantInfo):
    TAG = 12

    def init(self, data, class_file):
        self.class_file = class_file
        self.name_index = u2(data[0:2])
        self.descriptor_index = u2(data[2:4])
        return data[4:]

    def serialize(self):
        return su2(self.name_index) + su2(self.descriptor_index)

    def get_field_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

    def get_method_descriptor(self):
        return get_method_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

    def __str__(self):
        return ("%s:%s" % (safe(str(self.class_file.constants[self.name_index - 1])),
                           safe(str(self.class_file.constants[self.descriptor_index - 1]))))


class Utf8Info(ConstantInfo):
    TAG = 1

    def init(self, data, class_file):
        self.class_file = class_file
        self.length = u2(data[0:2])
        self.bytes = data[2:2 + self.length]
        return data[2 + self.length:]

    def serialize(self):
        return su2(self.length) + self.bytes

    def __str__(self):
        return self.bytes

    def __unicode__(self):
        return unicode(self.bytes, "utf-8")

    def get_value(self):
        return str(self)


class StringInfo(ConstantInfo):
    TAG = 8

    def init(self, data, class_file):
        self.class_file = class_file
        self.string_index = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return su2(self.string_index)

    def __str__(self):
        return str(self.class_file.constants[self.string_index - 1])

    def __unicode__(self):
        return unicode(self.class_file.constants[self.string_index - 1])

    def get_value(self):
        return str(self)


class SmallNumInfo(ConstantInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.bytes = data[0:4]
        return data[4:]

    def serialize(self):
        return self.bytes


class IntegerInfo(SmallNumInfo):
    TAG = 3

    def get_value(self):
        return s4(self.bytes)


class FloatInfo(SmallNumInfo):
    TAG = 4

    def get_value(self):
        return f4(self.bytes)


class LargeNumInfo(ConstantInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.high_bytes = data[0:4]
        self.low_bytes = data[4:8]
        return data[8:]

    def serialize(self):
        return self.high_bytes + self.low_bytes


class LongInfo(LargeNumInfo):
    TAG = 5

    def get_value(self):
        return s8(self.high_bytes + self.low_bytes)


class DoubleInfo(LargeNumInfo):
    TAG = 6

    def get_value(self):
        return f8(self.high_bytes + self.low_bytes)

CONSTANT_INFO_CLASSES = (ClassInfo, FieldRefInfo, MethodRefInfo, InterfaceMethodRefInfo,
                         StringInfo, IntegerInfo, FloatInfo, LongInfo, DoubleInfo,
                         NameAndTypeInfo, Utf8Info)
CONSTANT_INFO_TAG_MAP = dict([(cls.TAG, cls) for cls in CONSTANT_INFO_CLASSES])

# Other information.
# Objects of these classes are generally aware of the class they reside in.


class ItemInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.access_flags = u2(data[0:2])
        self.name_index = u2(data[2:4])
        self.descriptor_index = u2(data[4:6])
        self.attributes, data = self.class_file._get_attributes(data[6:])
        return data

    def serialize(self):
        od = su2(self.access_flags) + su2(self.name_index) + su2(self.descriptor_index)
        od += self.class_file._serialize_attributes(self.attributes)
        return od


class FieldInfo(ItemInfo):
    def get_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))


class MethodInfo(ItemInfo):
    def get_descriptor(self):
        return get_method_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))


class AttributeInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.info = data[4:4 + self.attribute_length]
        return data[4 + self.attribute_length:]

    def serialize(self):
        return su4(self.attribute_length) + self.info

# NOTE: Decode the different attribute formats.


class SourceFileAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.sourcefile_index = u2(data[4:6])
        return data[6:]

    def serialize(self):
        return su4(self.attribute_length) + su2(self.sourcefile_index)


class ConstantValueAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.constant_value_index = u2(data[4:6])
        assert((4 + self.attribute_length) == 6)
        return data[(4 + self.attribute_length):]

    def get_value(self):
        return self.class_file.constants[self.constant_value_index - 1].get_value()

    def serialize(self):
        return su4(self.attribute_length) + su2(self.constant_value_index)


class CodeAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.max_stack = u2(data[4:6])
        self.max_locals = u2(data[6:8])
        self.code_length = u4(data[8:12])
        end_of_code = 12 + self.code_length
        self.code = data[12:end_of_code]
        self.exception_table_length = u2(data[end_of_code:end_of_code + 2])
        self.exception_table = []
        data = data[end_of_code + 2:]
        for i in range(0, self.exception_table_length):
            exception = ExceptionInfo()
            data = exception.init(data, class_file)
            self.exception_table.append(exception)
        self.attributes, data = self.class_file._get_attributes(data)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(self.max_stack) + su2(self.max_locals) + su4(self.code_length) + self.code
        od += su2(self.exception_table_length)
        od += "".join([e.serialize() for e in self.exception_table])
        od += self.class_file._serialize_attributes(self.attributes)
        return od


class ExceptionsAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.number_of_exceptions = u2(data[4:6])
        self.exception_index_table = []
        index = 6
        for i in range(0, self.number_of_exceptions):
            self.exception_index_table.append(u2(data[index:index + 2]))
            index += 2
        return data[index:]

    def get_exception(self, i):
        exception_index = self.exception_index_table[i]
        return self.class_file.constants[exception_index - 1]

    def serialize(self):
        od = su4(self.attribute_length) + su2(self.number_of_exceptions)
        od += "".join([su2(ei) for ei in self.exception_index_table])
        return od


class InnerClassesAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.number_of_classes = u2(data[4:6])
        self.classes = []
        data = data[6:]
        for i in range(0, self.number_of_classes):
            inner_class = InnerClassInfo()
            data = inner_class.init(data, self.class_file)
            self.classes.append(inner_class)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(self.number_of_classes)
        od += "".join([c.serialize() for c in self.classes])
        return od


class SyntheticAttributeInfo(AttributeInfo):
    pass


class LineNumberAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.line_number_table_length = u2(data[4:6])
        self.line_number_table = []
        data = data[6:]
        for i in range(0, self.line_number_table_length):
            line_number = LineNumberInfo()
            data = line_number.init(data, class_file)
            self.line_number_table.append(line_number)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(self.line_number_table_length)
        od += "".join([ln.serialize() for ln in self.line_number_table])
        return od


class LocalVariableAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.local_variable_table_length = u2(data[4:6])
        self.local_variable_table = []
        data = data[6:]
        for i in range(0, self.local_variable_table_length):
            local_variable = LocalVariableInfo()
            data = local_variable.init(data, self.class_file)
            self.local_variable_table.append(local_variable)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(self.local_variable_table_length)
        od += "".join([lv.serialize() for lv in self.local_variable_table])
        return od


class LocalVariableTypeAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        local_variable_type_table_length = u2(data[4:6])
        data = data[6:]
        self.local_variable_type_table = []
        for i in range(0, local_variable_type_table_length):
            local_variable = LocalVariableInfo()
            data = local_variable.init(data, self.class_file)
            self.local_variable_type_table.append(local_variable)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(len(self.local_variable_type_table))
        od += "".join([lv.serialize() for lv in self.local_variable_type_table])
        return od


class DeprecatedAttributeInfo(AttributeInfo):
    pass


class VerificationTypeInfo(object):
    def __init__(self, tag):
        self.tag = tag

    def init(self, data, class_file):
        self.class_file = class_file
        tag = u1(data[0:1])
        assert(tag == self.tag)
        return data[1:]

    def serialize(self):
        return su1(self.tag)


class TopVariableInfo(VerificationTypeInfo):
    TAG = 0


class IntegerVariableInfo(VerificationTypeInfo):
    TAG = 1


class FloatVariableInfo(VerificationTypeInfo):
    TAG = 2


class DoubleVariableInfo(VerificationTypeInfo):
    TAG = 3


class LongVariableInfo(VerificationTypeInfo):
    TAG = 4


class NullVariableInfo(VerificationTypeInfo):
    TAG = 5


class UninitializedThisVariableInfo(VerificationTypeInfo):
    TAG = 6


class ObjectVariableInfo(VerificationTypeInfo):
    TAG = 7

    def init(self, data, class_file):
        data = super(ObjectVariableInfo, self).init(data, class_file)
        self.cpool_index = u2(data)
        return data[2:]

    def serialize(self):
        return super(ObjectVariableInfo, self).serialize() + su2(self.cpool_index)


class UninitializedVariableInfo(VerificationTypeInfo):
    TAG = 8

    def init(self, data, class_file):
        data = super(UninitializedVariableInfo, self).init(data, class_file)
        self.offset = u2(data)
        return data[2:]

    def serialize(self):
        return super(UninitializedVariableInfo, self).serialize() + su2(self.offset)

VARIABLE_INFO_CLASSES = (TopVariableInfo, IntegerVariableInfo, FloatVariableInfo, DoubleVariableInfo,
                         LongVariableInfo, NullVariableInfo, UninitializedThisVariableInfo,
                         ObjectVariableInfo, UninitializedVariableInfo)
VARIABLE_INFO_TAG_MAP = dict([(cls.TAG, cls) for cls in VARIABLE_INFO_CLASSES])


class UnknownVariableInfo(Exception):
    pass


def create_verification_type_info(data):
    # Does not consume data, just does lookahead
    tag = u1(data[0:1])
    if tag in VARIABLE_INFO_TAG_MAP:
        return VARIABLE_INFO_TAG_MAP[tag](tag)
    else:
        raise UnknownVariableInfo(tag)


class StackMapFrame(object):
    def __init__(self, frame_type):
        self.frame_type = frame_type

    def init(self, data, class_file):
        self.class_file = class_file
        frame_type = u1(data[0:1])
        assert(frame_type == self.frame_type)
        return data[1:]

    def serialize(self):
        return su1(self.frame_type)


class SameFrame(StackMapFrame):
    TYPE_LOWER = 0
    TYPE_UPPER = 63


class SameLocals1StackItemFrame(StackMapFrame):
    TYPE_LOWER = 64
    TYPE_UPPER = 127

    def init(self, data, class_file):
        data = super(SameLocals1StackItemFrame, self).init(data, class_file)
        self.offset_delta = self.frame_type - 64
        self.stack = [create_verification_type_info(data)]
        return self.stack[0].init(data, class_file)

    def serialize(self):
        return super(SameLocals1StackItemFrame, self).serialize() + self.stack[0].serialize()


class SameLocals1StackItemFrameExtended(StackMapFrame):
    TYPE_LOWER = 247
    TYPE_UPPER = 247

    def init(self, data, class_file):
        data = super(SameLocals1StackItemFrameExtended, self).init(data, class_file)
        self.offset_delta = u2(data[0:2])
        data = data[2:]
        self.stack = [create_verification_type_info(data)]
        return self.stack[0].init(data, class_file)

    def serialize(self):
        return super(SameLocals1StackItemFrameExtended, self).serialize() + su2(self.offset_delta) + self.stack[0].serialize()


class ChopFrame(StackMapFrame):
    TYPE_LOWER = 248
    TYPE_UPPER = 250

    def init(self, data, class_file):
        data = super(ChopFrame, self).init(data, class_file)
        self.offset_delta = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return super(ChopFrame, self).serialize() + su2(self.offset_delta)


class SameFrameExtended(StackMapFrame):
    TYPE_LOWER = 251
    TYPE_UPPER = 251

    def init(self, data, class_file):
        data = super(SameFrameExtended, self).init(data, class_file)
        self.offset_delta = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return super(SameFrameExtended, self).serialize() + su2(self.offset_delta)


class AppendFrame(StackMapFrame):
    TYPE_LOWER = 252
    TYPE_UPPER = 254

    def init(self, data, class_file):
        data = super(AppendFrame, self).init(data, class_file)
        self.offset_delta = u2(data[0:2])
        data = data[2:]
        num_locals = self.frame_type - 251
        self.locals = []
        for ii in xrange(num_locals):
            info = create_verification_type_info(data)
            data = info.init(data, class_file)
            self.locals.append(info)
        return data

    def serialize(self):
        od = super(AppendFrame, self).serialize() + su2(self.offset_delta)
        od += "".join([l.serialize() for l in self.locals])
        return od


class FullFrame(StackMapFrame):
    TYPE_LOWER = 255
    TYPE_UPPER = 255

    def init(self, data, class_file):
        data = super(FullFrame, self).init(data, class_file)
        self.offset_delta = u2(data[0:2])
        num_locals = u2(data[2:4])
        data = data[4:]
        self.locals = []
        for ii in xrange(num_locals):
            info = create_verification_type_info(data)
            data = info.init(data, class_file)
            self.locals.append(info)
        num_stack_items = u2(data[0:2])
        data = data[2:]
        self.stack = []
        for ii in xrange(num_stack_items):
            stack_item = create_verification_type_info(data)
            data = stack_item.init(data, class_file)
            self.stack.append(stack_item)
        return data

    def serialize(self):
        od = super(FullFrame, self).serialize() + su2(self.offset_delta) + su2(len(self.locals))
        od += "".join([l.serialize() for l in self.locals])
        od += su2(len(self.stack))
        od += "".join([s.serialize() for s in self.stack])
        return od

FRAME_CLASSES = (SameFrame, SameLocals1StackItemFrame, SameLocals1StackItemFrameExtended,
                 ChopFrame, SameFrameExtended, AppendFrame, FullFrame)


class UnknownStackFrame(Exception):
    pass


def create_stack_frame(data):
    # Does not consume data, just does lookahead
    frame_type = u1(data[0:1])
    for cls in FRAME_CLASSES:
        if frame_type >= cls.TYPE_LOWER and frame_type <= cls.TYPE_UPPER:
            return cls(frame_type)
    raise UnknownStackFrame(frame_type)


class StackMapTableAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        num_entries = u2(data[4:6])
        self.entries = []
        data = data[6:]
        for i in range(0, num_entries):
            frame = create_stack_frame(data)
            data = frame.init(data, class_file)
            self.entries.append(frame)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(len(self.entries))
        od += "".join([e.serialize() for e in self.entries])
        return od


class EnclosingMethodAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.class_index = u2(data[4:6])
        self.method_index = u2(data[6:8])
        return data[8:]

    def serialize(self):
        return su4(self.attribute_length) + su2(self.class_index) + su2(self.method_index)


class SignatureAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.signature_index = u2(data[4:6])
        return data[6:]

    def serialize(self):
        return su4(self.attribute_length) + su2(self.signature_index)


class SourceDebugExtensionAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        self.debug_extension = data[4:(4 + self.attribute_length)]
        return data[(4 + self.attribute_length):]

    def serialize(self):
        return su4(self.attribute_length) + self.debug_extension


class ElementValue(object):
    def __init__(self, tag):
        self.tag = tag

    def init(self, data, class_file):
        self.class_file = class_file
        tag = chr(u1(data[0:1]))
        assert(tag == self.tag)
        return data[1:]

    def serialize(self):
        return su1(ord(self.tag))


class ConstValue(ElementValue):
    def init(self, data, class_file):
        data = super(ConstValue, self).init(data, class_file)
        self.const_value_index = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return super(ConstValue, self).serialize() + su2(self.const_value_index)


class EnumConstValue(ElementValue):
    def init(self, data, class_file):
        data = super(EnumConstValue, self).init(data, class_file)
        self.type_name_index = u2(data[0:2])
        self.const_name_index = u2(data[2:4])
        return data[4:]

    def serialize(self):
        return super(EnumConstValue, self).serialize() + su2(self.type_name_index) + su2(self.const_name_index)


class ClassInfoValue(ElementValue):
    def init(self, data, class_file):
        data = super(ClassInfoValue, self).init(data, class_file)
        self.class_info_index = u2(data[0:2])
        return data[2:]

    def serialize(self):
        return super(ClassInfoValue, self).serialize() + su2(self.class_info_index)


class AnnotationValue(ElementValue):
    def init(self, data, class_file):
        data = super(AnnotationValue, self).init(data, class_file)
        self.annotation_value = Annotation()
        return self.annotation_value.init(data, class_file)

    def serialize(self):
        return super(AnnotationValue, self).serialize() + self.annotation_value.serialize()


class ArrayValue(ElementValue):
    def init(self, data, class_file):
        data = super(ArrayValue, self).init(data, class_file)
        num_values = u2(data[0:2])
        data = data[2:]
        self.values = []
        for ii in xrange(num_values):
            element_value = create_element_value(data)
            data = element_value.init(data, class_file)
            self.values.append(element_value)
        return data

    def serialize(self):
        od = super(ArrayValue, self).serialize() + su2(len(self.values))
        od += "".join([v.serialize() for v in self.values])
        return od


class UnknownElementValue:
    pass


def create_element_value(data):
    tag = chr(u1(data[0:1]))
    if tag in ('B', 'C', 'D', 'F', 'I', 'J', 'S', 'Z', 's'):
        return ConstValue(tag)
    elif tag == 'e':
        return EnumConstValue(tag)
    elif tag == 'c':
        return ClassInfoValue(tag)
    elif tag == '@':
        return AnnotationValue(tag)
    elif tag == '[':
        return ArrayValue(tag)
    else:
        raise UnknownElementValue(tag)


class Annotation(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.type_index = u2(data[0:2])
        num_element_value_pairs = u2(data[2:4])
        data = data[4:]
        self.element_value_pairs = []
        for ii in xrange(num_element_value_pairs):
            element_name_index = u2(data[0:2])
            data = data[2:]
            element_value = create_element_value(data)
            data = element_value.init(data, class_file)
            self.element_value_pairs.append((element_name_index, element_value))
        return data

    def serialize(self):
        od = su2(self.type_index) + su2(len(self.element_value_pairs))
        od += "".join([su2(evp[0]) + evp[1].serialize() for evp in self.element_value_pairs])
        return od


class RuntimeAnnotationsAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        num_annotations = u2(data[4:6])
        data = data[6:]
        self.annotations = []
        for ii in xrange(num_annotations):
            annotation = Annotation()
            data = annotation.init(data, class_file)
            self.annotations.append(annotation)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su2(len(self.annotations))
        od += "".join([a.serialize() for a in self.annotations])
        return od


class RuntimeVisibleAnnotationsAttributeInfo(RuntimeAnnotationsAttributeInfo):
    pass


class RuntimeInvisibleAnnotationsAttributeInfo(RuntimeAnnotationsAttributeInfo):
    pass


class RuntimeParameterAnnotationsAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        num_parameters = u1(data[4:5])
        data = data[5:]
        self.parameter_annotations = []
        for ii in xrange(num_parameters):
            num_annotations = u2(data[0:2])
            data = data[2:]
            annotations = []
            for jj in xrange(num_annotations):
                annotation = Annotation()
                data = annotation.init(data, class_file)
                annotations.append(annotation)
            self.parameter_annotations.append(annotations)
        return data

    def serialize(self):
        od = su4(self.attribute_length) + su1(len(self.parameter_annotations))
        for pa in self.parameter_annotations:
            od += su2(len(pa))
            od += "".join([a.serialize() for a in pa])
        return od


class RuntimeVisibleParameterAnnotationsAttributeInfo(RuntimeParameterAnnotationsAttributeInfo):
    pass


class RuntimeInvisibleParameterAnnotationsAttributeInfo(RuntimeParameterAnnotationsAttributeInfo):
    pass


class AnnotationDefaultAttributeInfo(AttributeInfo):
    def init(self, data, class_file):
        self.class_file = class_file
        self.attribute_length = u4(data[0:4])
        data = data[4:]
        self.default_value = create_element_value(data)
        return self.default_value.init(data, class_file)

    def serialize(self):
        return su4(self.attribute_length) + self.default_value.serialize()


# Child classes of the attribute information classes.

class ExceptionInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.start_pc = u2(data[0:2])
        self.end_pc = u2(data[2:4])
        self.handler_pc = u2(data[4:6])
        self.catch_type = u2(data[6:8])
        return data[8:]

    def serialize(self):
        return su2(self.start_pc) + su2(self.end_pc) + su2(self.handler_pc) + su2(self.catch_type)


class InnerClassInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.inner_class_info_index = u2(data[0:2])
        self.outer_class_info_index = u2(data[2:4])
        self.inner_name_index = u2(data[4:6])
        self.inner_class_access_flags = u2(data[6:8])
        return data[8:]

    def serialize(self):
        return su2(self.inner_class_info_index) + su2(self.outer_class_info_index) + su2(self.inner_name_index) + su2(self.inner_class_access_flags)


class LineNumberInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.start_pc = u2(data[0:2])
        self.line_number = u2(data[2:4])
        return data[4:]

    def serialize(self):
        return su2(self.start_pc) + su2(self.line_number)


class LocalVariableInfo(object):
    def init(self, data, class_file):
        self.class_file = class_file
        self.start_pc = u2(data[0:2])
        self.length = u2(data[2:4])
        self.name_index = u2(data[4:6])
        self.descriptor_index = u2(data[6:8])
        self.index = u2(data[8:10])
        return data[10:]

    def get_descriptor(self):
        return get_field_descriptor(unicode(self.class_file.constants[self.descriptor_index - 1]))

    def serialize(self):
        return su2(self.start_pc) + su2(self.length) + su2(self.name_index) + su2(self.descriptor_index) + su2(self.index)


class UnknownTag(Exception):
    pass


class UnknownAttribute(Exception):
    pass

ATTR_NAMES_TO_CLASS = {"SourceFile": SourceFileAttributeInfo,
                       "ConstantValue": ConstantValueAttributeInfo,
                       "Code": CodeAttributeInfo,
                       "Exceptions": ExceptionsAttributeInfo,
                       "InnerClasses": InnerClassesAttributeInfo,
                       "Synthetic": SyntheticAttributeInfo,
                       "LineNumberTable": LineNumberAttributeInfo,
                       "LocalVariableTable": LocalVariableAttributeInfo,
                       "Deprecated": DeprecatedAttributeInfo,
                       # Java SE 1.6, class file >= 50.0, VMSpec v3 s4.7.4
                       "StackMapTable": StackMapTableAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.7
                       "EnclosingMethod": EnclosingMethodAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.9
                       "Signature": SignatureAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.11
                       "SourceDebugExtension": SourceDebugExtensionAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.14
                       "LocalVariableTypeTable": LocalVariableTypeAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.16
                       "RuntimeVisibleAnnotations": RuntimeVisibleAnnotationsAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.17
                       "RuntimeInvisibleAnnotations": RuntimeInvisibleAnnotationsAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.18
                       "RuntimeVisibleParameterAnnotations": RuntimeVisibleParameterAnnotationsAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.19
                       "RuntimeInvisibleParameterAnnotations": RuntimeInvisibleParameterAnnotationsAttributeInfo,
                       # Java SE 1.5, class file >= 49.0, VMSpec v3  s4.7.20
                       "AnnotationDefault": AnnotationDefaultAttributeInfo}


class ClassFile(object):
    "A class representing a Java class file."

    def __init__(self, s):

        """
        Process the given string 's', populating the object with the class
        file's details.
        """

        self.attribute_class_to_index = None
        self.sourcefile_attribute = None
        magic = u4(s[0:])
        if magic != 0xCAFEBABE:
            raise UnknownAttribute(magic)
        self.minorv, self.majorv = u2(s[4:]), u2(s[6:])
        self.constants, s = self._get_constants(s[8:])
        self.access_flags, s = self._get_access_flags(s)
        self.this_class, s = self._get_this_class(s)
        self.super_class, s = self._get_super_class(s)
        self.interfaces, s = self._get_interfaces(s)
        self.fields, s = self._get_fields(s)
        self.methods, s = self._get_methods(s)
        self.attributes, s = self._get_attributes(s)

    def serialize(self):
        od = su4(0xCAFEBABE) + su2(self.minorv) + su2(self.majorv)
        od += self._serialize_constants()
        od += self._serialize_access_flags()
        od += self._serialize_this_class()
        od += self._serialize_super_class()
        od += self._serialize_interfaces()
        od += self._serialize_fields()
        od += self._serialize_methods()
        od += self._serialize_attributes(self.attributes)
        return od

    def _encode_const(self, c):
        od = ''
        if isinstance(c, ConstantInfo):
            od += su1(c.TAG)
        else:
            return od
        od += c.serialize()
        return od

    def _decode_const(self, s):
        tag = u1(s[0:1])
        if tag in CONSTANT_INFO_TAG_MAP:
            cls = CONSTANT_INFO_TAG_MAP[tag]
            const = cls()
        else:
            raise UnknownTag(tag)

        # Initialise the constant object.
        s = const.init(s[1:], self)
        return const, s

    def _get_constants_from_table(self, count, s):
        l = []
        # Have to skip certain entries specially.
        i = 1
        while i < count:
            c, s = self._decode_const(s)
            l.append(c)
            # Add a blank entry after "large" entries.
            if isinstance(c, LargeNumInfo):
                l.append(None)
                i += 1
            i += 1
        return l, s

    def _get_items_from_table(self, cls, number, s):
        l = []
        for i in range(0, number):
            f = cls()
            s = f.init(s, self)
            l.append(f)
        return l, s

    def _get_methods_from_table(self, number, s):
        return self._get_items_from_table(MethodInfo, number, s)

    def _get_fields_from_table(self, number, s):
        return self._get_items_from_table(FieldInfo, number, s)

    def _get_attribute_from_table(self, s):
        attribute_name_index = u2(s[0:2])
        constant_name = self.constants[attribute_name_index - 1].bytes
        if constant_name in ATTR_NAMES_TO_CLASS:
            attribute = ATTR_NAMES_TO_CLASS[constant_name]()
        else:
            raise UnknownAttribute(constant_name)
        s = attribute.init(s[2:], self)
        return attribute, s

    def _get_attributes_from_table(self, number, s):
        attributes = []
        for i in range(0, number):
            attribute, s = self._get_attribute_from_table(s)
            attributes.append(attribute)
            if isinstance(attribute, SourceFileAttributeInfo):
                self.sourcefile_attribute = attribute
        return attributes, s

    def _get_constants(self, s):
        count = u2(s[0:2])
        return self._get_constants_from_table(count, s[2:])

    def _serialize_constants(self):
        return su2(len(self.constants) + 1) + "".join([self._encode_const(c) for c in self.constants])

    def _get_access_flags(self, s):
        return u2(s[0:2]), s[2:]

    def _serialize_access_flags(self):
        return su2(self.access_flags)

    def _get_this_class(self, s):
        index = u2(s[0:2])
        return self.constants[index - 1], s[2:]

    def _serialize_this_class(self):
        return su2(self.constants.index(self.this_class) + 1)

    def _serialize_super_class(self):
        return su2(self.constants.index(self.super_class) + 1)

    def _get_super_class(self, s):
        index = u2(s[0:2])
        if index != 0:
            return self.constants[index - 1], s[2:]
        else:
            return None, s[2:]

    def _get_interfaces(self, s):
        interfaces = []
        number = u2(s[0:2])
        s = s[2:]
        for i in range(0, number):
            index = u2(s[0:2])
            interfaces.append(self.constants[index - 1])
            s = s[2:]
        return interfaces, s

    def _serialize_interfaces(self):
        return su2(len(self.interfaces)) + "".join([su2(self.constants.index(interf) + 1) for interf in self.interfaces])

    def _get_fields(self, s):
        number = u2(s[0:2])
        return self._get_fields_from_table(number, s[2:])

    def _serialize_fields(self):
        od = su2(len(self.fields))
        od += "".join([f.serialize() for f in self.fields])
        return od

    def _get_attributes(self, s):
        number = u2(s[0:2])
        return self._get_attributes_from_table(number, s[2:])

    def _serialize_attributes(self, attrs):
        od = su2(len(attrs))
        if len(attrs) == 0:
            return od
        if self.attribute_class_to_index == None:
            self.attribute_class_to_index = {}
            index = 0
            for c in self.constants:
                index += 1
                if isinstance(c, Utf8Info) and str(c) in ATTR_NAMES_TO_CLASS.keys():
                    self.attribute_class_to_index[ATTR_NAMES_TO_CLASS[str(c)]] = index
        for attribute in attrs:
            for (classtype, name_index) in self.attribute_class_to_index.iteritems():
                if isinstance(attribute, classtype):
                    od += su2(name_index)
                    break
            od += attribute.serialize()
        return od

    def _get_methods(self, s):
        number = u2(s[0:2])
        return self._get_methods_from_table(number, s[2:])

    def _serialize_methods(self):
        od = su2(len(self.methods))
        od += "".join([m.serialize() for m in self.methods])
        return od


if __name__ == "__main__":
    import sys
    f = open(sys.argv[1], "rb")
    in_data = f.read()
    c = ClassFile(in_data)
    f.close()
    out_data = c.serialize()
    assert(in_data == out_data)
