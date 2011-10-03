#!/usr/bin/env python
"""Java class file information, from JVM Spec 3rd edition (draft)

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


# Map from Java field type descriptors to type names; JVMSpec 4.3.2
DESCRIPTOR_TYPE_MAPPING = {u"B": u"byte",
                           u"C": u"char",
                           u"D": u"double",
                           u"F": u"float",
                           u"I": u"int",
                           u"J": u"long",
                           u"L": u"<class>",  # special
                           u"S": u"short",
                           u"Z": u"boolean",
                           u"[": u"<array>",  # special
                           u"V": u"void",  # special; only allowed for return types
                           }
# Map from Java field type descriptors to size of corresponding type; JVMSpec 3.2, 4.3.2
POINTER_SIZE = 8
DESCRIPTOR_SIZE_MAPPING = {u"B": 1,
                           u"C": 1,
                           u"D": 8,
                           u"F": 4,
                           u"I": 4,
                           u"J": 8,
                           u"L": POINTER_SIZE,
                           u"S": 2,
                           u"Z": 4,  # JVMSpec 3.2.4: ints used internally for booleans
                           u"[": 0,  # special
                           u"V": 0,  # special; only allowed for return types
                           }

# Map from array type descriptors to type names; JVMSpec 6.newarray
ARRAY_TYPE_MAPPING = {4: u"boolean",
                      5: u"char",
                      6: u"float",
                      7: u"double",
                      8: u"byte",
                      9: u"short",
                      10: u"int",
                      11: u"long"}

# Java bytecodes; JVMSpec 6, 7
# code: (mnemonic, number of following bytes, struct code for syntax of params, semantic indicator)
# struct code is assumed to be prefixed by ">" (i.e. big-endian)
# semantic indicator:
#    # = immediate number
#    c = index into constant table
#    l = local variable index
#    o = offset
#    a = array type
#    0 = zero value
BYTECODES = {
    0: (u"nop", 0, "", ""),
    1: (u"aconst_null", 0, "", ""),
    2: (u"iconst_m1", 0, "", ""),
    3: (u"iconst_0", 0, "", ""),
    4: (u"iconst_1", 0, "", ""),
    5: (u"iconst_2", 0, "", ""),
    6: (u"iconst_3", 0, "", ""),
    7: (u"iconst_4", 0, "", ""),
    8: (u"iconst_5", 0, "", ""),
    9: (u"lconst_0", 0, "", ""),
    10: (u"lconst_1", 0, "", ""),
    11: (u"fconst_0", 0, "", ""),
    12: (u"fconst_1", 0, "", ""),
    13: (u"fconst_2", 0, "", ""),
    14: (u"dconst_0", 0, "", ""),
    15: (u"dconst_1", 0, "", ""),
    16: (u"bipush", 1, "b", "#"),
    17: (u"sipush", 2, "h", "#"),
    18: (u"ldc", 1, "B", "c"),
    19: (u"ldc_w", 2, "H", "c"),
    20: (u"ldc2_w", 2, "H", "c"),
    21: (u"iload", 1, "B", "l"),
    22: (u"lload", 1, "B", "l"),
    23: (u"fload", 1, "B", "l"),
    24: (u"dload", 1, "B", "l"),
    25: (u"aload", 1, "B", "l"),
    26: (u"iload_0", 0, "", ""),
    27: (u"iload_1", 0, "", ""),
    28: (u"iload_2", 0, "", ""),
    29: (u"iload_3", 0, "", ""),
    30: (u"lload_0", 0, "", ""),
    31: (u"lload_1", 0, "", ""),
    32: (u"lload_2", 0, "", ""),
    33: (u"lload_3", 0, "", ""),
    34: (u"fload_0", 0, "", ""),
    35: (u"fload_1", 0, "", ""),
    36: (u"fload_2", 0, "", ""),
    37: (u"fload_3", 0, "", ""),
    38: (u"dload_0", 0, "", ""),
    39: (u"dload_1", 0, "", ""),
    40: (u"dload_2", 0, "", ""),
    41: (u"dload_3", 0, "", ""),
    42: (u"aload_0", 0, "", ""),
    43: (u"aload_1", 0, "", ""),
    44: (u"aload_2", 0, "", ""),
    45: (u"aload_3", 0, "", ""),
    46: (u"iaload", 0, "", ""),
    47: (u"laload", 0, "", ""),
    48: (u"faload", 0, "", ""),
    49: (u"daload", 0, "", ""),
    50: (u"aaload", 0, "", ""),
    51: (u"baload", 0, "", ""),
    52: (u"caload", 0, "", ""),
    53: (u"saload", 0, "", ""),
    54: (u"istore", 1, "B", "l"),
    55: (u"lstore", 1, "B", "l"),
    56: (u"fstore", 1, "B", "l"),
    57: (u"dstore", 1, "B", "l"),
    58: (u"astore", 1, "B", "l"),
    59: (u"istore_0", 0, "", ""),
    60: (u"istore_1", 0, "", ""),
    61: (u"istore_2", 0, "", ""),
    62: (u"istore_3", 0, "", ""),
    63: (u"lstore_0", 0, "", ""),
    64: (u"lstore_1", 0, "", ""),
    65: (u"lstore_2", 0, "", ""),
    66: (u"lstore_3", 0, "", ""),
    67: (u"fstore_0", 0, "", ""),
    68: (u"fstore_1", 0, "", ""),
    69: (u"fstore_2", 0, "", ""),
    70: (u"fstore_3", 0, "", ""),
    71: (u"dstore_0", 0, "", ""),
    72: (u"dstore_1", 0, "", ""),
    73: (u"dstore_2", 0, "", ""),
    74: (u"dstore_3", 0, "", ""),
    75: (u"astore_0", 0, "", ""),
    76: (u"astore_1", 0, "", ""),
    77: (u"astore_2", 0, "", ""),
    78: (u"astore_3", 0, "", ""),
    79: (u"iastore", 0, "", ""),
    80: (u"lastore", 0, "", ""),
    81: (u"fastore", 0, "", ""),
    82: (u"dastore", 0, "", ""),
    83: (u"aastore", 0, "", ""),
    84: (u"bastore", 0, "", ""),
    85: (u"castore", 0, "", ""),
    86: (u"sastore", 0, "", ""),
    87: (u"pop", 0, "", ""),
    88: (u"pop2", 0, "", ""),
    89: (u"dup", 0, "", ""),
    90: (u"dup_x1", 0, "", ""),
    91: (u"dup_x2", 0, "", ""),
    92: (u"dup2", 0, "", ""),
    93: (u"dup2_x1", 0, "", ""),
    94: (u"dup2_x2", 0, "", ""),
    95: (u"swap", 0, "", ""),
    96: (u"iadd", 0, "", ""),
    97: (u"ladd", 0, "", ""),
    98: (u"fadd", 0, "", ""),
    99: (u"dadd", 0, "", ""),
    100: (u"isub", 0, "", ""),
    101: (u"lsub", 0, "", ""),
    102: (u"fsub", 0, "", ""),
    103: (u"dsub", 0, "", ""),
    104: (u"imul", 0, "", ""),
    105: (u"lmul", 0, "", ""),
    106: (u"fmul", 0, "", ""),
    107: (u"dmul", 0, "", ""),
    108: (u"idiv", 0, "", ""),
    109: (u"ldiv", 0, "", ""),
    110: (u"fdiv", 0, "", ""),
    111: (u"ddiv", 0, "", ""),
    112: (u"irem", 0, "", ""),
    113: (u"lrem", 0, "", ""),
    114: (u"frem", 0, "", ""),
    115: (u"drem", 0, "", ""),
    116: (u"ineg", 0, "", ""),
    117: (u"lneg", 0, "", ""),
    118: (u"fneg", 0, "", ""),
    119: (u"dneg", 0, "", ""),
    120: (u"ishl", 0, "", ""),
    121: (u"lshl", 0, "", ""),
    122: (u"ishr", 0, "", ""),
    123: (u"lshr", 0, "", ""),
    124: (u"iushr", 0, "", ""),
    125: (u"lushr", 0, "", ""),
    126: (u"iand", 0, "", ""),
    127: (u"land", 0, "", ""),
    128: (u"ior", 0, "", ""),
    129: (u"lor", 0, "", ""),
    130: (u"ixor", 0, "", ""),
    131: (u"lxor", 0, "", ""),
    132: (u"iinc", 2, "Bb", "l#"),
    133: (u"i2l", 0, "", ""),
    134: (u"i2f", 0, "", ""),
    135: (u"i2d", 0, "", ""),
    136: (u"l2i", 0, "", ""),
    137: (u"l2f", 0, "", ""),
    138: (u"l2d", 0, "", ""),
    139: (u"f2i", 0, "", ""),
    140: (u"f2l", 0, "", ""),
    141: (u"f2d", 0, "", ""),
    142: (u"d2i", 0, "", ""),
    143: (u"d2l", 0, "", ""),
    144: (u"d2f", 0, "", ""),
    145: (u"i2b", 0, "", ""),
    146: (u"i2c", 0, "", ""),
    147: (u"i2s", 0, "", ""),
    148: (u"lcmp", 0, "", ""),
    149: (u"fcmpl", 0, "", ""),
    150: (u"fcmpg", 0, "", ""),
    151: (u"dcmpl", 0, "", ""),
    152: (u"dcmpg", 0, "", ""),
    153: (u"ifeq", 2, "h", "o"),
    154: (u"ifne", 2, "h", "o"),
    155: (u"iflt", 2, "h", "o"),
    156: (u"ifge", 2, "h", "o"),
    157: (u"ifgt", 2, "h", "o"),
    158: (u"ifle", 2, "h", "o"),
    159: (u"if_icmpeq", 2, "h", "o"),
    160: (u"if_icmpne", 2, "h", "o"),
    161: (u"if_icmplt", 2, "h", "o"),
    162: (u"if_icmpge", 2, "h", "o"),
    163: (u"if_icmpgt", 2, "h", "o"),
    164: (u"if_icmple", 2, "h", "o"),
    165: (u"if_acmpeq", 2, "h", "o"),
    166: (u"if_acmpne", 2, "h", "o"),
    167: (u"goto", 2, "h", "o"),
    168: (u"jsr", 2, "h", "o"),
    169: (u"ret", 1, "B", "l"),
    170: (u"tableswitch", None, "", ""),  # variable number of arguments
    171: (u"lookupswitch", None, "", ""),  # variable number of arguments
    172: (u"ireturn", 0, "", ""),
    173: (u"lreturn", 0, "", ""),
    174: (u"freturn", 0, "", ""),
    175: (u"dreturn", 0, "", ""),
    176: (u"areturn", 0, "", ""),
    177: (u"return", 0, "", ""),
    178: (u"getstatic", 2, "H", "c"),
    179: (u"putstatic", 2, "H", "c"),
    180: (u"getfield", 2, "H", "c"),
    181: (u"putfield", 2, "H", "c"),
    182: (u"invokevirtual", 2, "H", "c"),
    183: (u"invokespecial", 2, "H", "c"),
    184: (u"invokestatic", 2, "H", "c"),
    185: (u"invokeinterface", 4, "HBB", "c#0"),
    # For historical reasons, opcode value 186 is not used
    187: (u"new", 2, "H", "c"),
    188: (u"newarray", 1, "B", "a"),
    189: (u"anewarray", 2, "H", "c"),
    190: (u"arraylength", 0, "", ""),
    191: (u"athrow", 0, "", ""),
    192: (u"checkcast", 2, "H", "c"),
    193: (u"instanceof", 2, "H", "c"),
    194: (u"monitorenter", 0, "", ""),
    195: (u"monitorexit", 0, "", ""),
    196: (u"wide", None, "", ""),  # 3 or 5 arguments, stack changes according to modified element
    197: (u"multianewarray", 3, "HB", "c#"),
    198: (u"ifnull", 2, "h", "o"),
    199: (u"ifnonnull", 2, "h", "o"),
    200: (u"goto_w", 4, "i", "o"),
    201: (u"jsr_w", 4, "i", "o"),
    # Reserved opcodes; cannot appear in a class file
    # 202: (u"breakpoint", None),
    # 254: (u"impdep1", None),
    # 255: (u"impdep2", None),
    }

# Access flags; JVMSpec 4.5
PUBLIC = 0x0001
PRIVATE = 0x0002
PROTECTED = 0x0004
STATIC = 0x0008
FINAL = 0x0010
SUPER = 0x0020
SYNCHRONIZED = 0x0020
VOLATILE = 0x0040
TRANSIENT = 0x0080
NATIVE = 0x0100
INTERFACE = 0x0200
ABSTRACT = 0x0400
STRICT = 0x0800


def access_description(flags):
    modifiers = []
    if ((flags & PUBLIC) != 0):
        modifiers.append(u"public")
    if ((flags & PRIVATE) != 0):
        modifiers.append(u"private")
    if ((flags & PROTECTED) != 0):
        modifiers.append(u"protected")
    if ((flags & STATIC) != 0):
        modifiers.append(u"static")
    if ((flags & FINAL) != 0):
        modifiers.append(u"final")
    if ((flags & SYNCHRONIZED) != 0):
        modifiers.append(u"synchronized")
    if ((flags & VOLATILE) != 0):
        modifiers.append(u"volatile")
    if ((flags & TRANSIENT) != 0):
        modifiers.append(u"transient")
    if ((flags & NATIVE) != 0):
        modifiers.append(u"native")
    if ((flags & INTERFACE) != 0):
        modifiers.append(u"interface")
    if ((flags & ABSTRACT) != 0):
        modifiers.append(u"abstract")
    if ((flags & STRICT) != 0):
        modifiers.append(u"strict")
    return " ".join(modifiers)


def set_pointer_size(size):
    global POINTER_SIZE
    POINTER_SIZE = size
    DESCRIPTOR_SIZE_MAPPING[u"L"] = POINTER_SIZE


def fqcn(s):
    # JVMSpec 4.2
    return s.replace(u"/", u".")


def size_field_descriptor(s):
    """Return the size in bytes of the field described by the given descriptor"""
    ii = 0
    while ii < len(s):
        c = s[ii]
        if c == u"[":
            pass
        elif c in DESCRIPTOR_SIZE_MAPPING:
            return DESCRIPTOR_SIZE_MAPPING[c]
        else:
            raise Exception("Unknown descriptor code %s" % c)
        ii += 1
    raise Exception("Failed to find single field in %s" % s)


def demangle_field_descriptor(s, void_allowed=False):
    """Convert field descriptor to a string describing the field.

    Returns (description, rest)"""
    # JVMSpec 4.3.2
    dim = 0
    ii = 0
    while ii < len(s):
        c = s[ii]
        if c == u"[":
            dim += 1
        elif c == "V" and void_allowed:
            if dim > 0:
                raise Exception("Cannot have array of void")
            return u"void", s[ii + 1:]
        elif c == "L":
            endpoint = s.find(u";", ii)
            if endpoint == -1:
                raise Exception("Failed to find end of classname")
            classname = fqcn(s[ii + 1:endpoint])
            return classname + dim * u"[]", s[endpoint + 1:]
        elif c in DESCRIPTOR_TYPE_MAPPING:
            return DESCRIPTOR_TYPE_MAPPING[c] + dim * u"[]", s[ii + 1:]
        else:
            raise Exception("Unknown descriptor code %s" % c)
        ii += 1
    raise Exception("Failed to find single field in %s" % s)


def demangle_method_descriptor(s):
    """Convert method descriptor to a pair of strings describing parameters and return type."""
    # JVMSpec 4.3.3
    assert s[0] == u"(", "Method descriptor %s should start with (" % s
    s = s[1:]
    params = []
    while s[0] != u")" and len(s) > 0:
        result, s = demangle_field_descriptor(s)
        params.append(result)
    if (len(s) == 0 or s[0] != u")"):
        raise Exception("Method descriptor %s should include )" % s)
    return_type, s = demangle_field_descriptor(s[1:], void_allowed=True)
    assert len(s) == 0, "Unexpected extra text in %s" % s
    return (params, return_type)
