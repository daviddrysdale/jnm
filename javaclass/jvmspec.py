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
DESCRIPTOR_TYPE_MAPPING = {"B": "byte",
                           "C": "char",
                           "D": "double",
                           "F": "float",
                           "I": "int",
                           "J": "long",
                           "L": "<class>",  # special
                           "S": "short",
                           "Z": "boolean",
                           "[": "<array>",  # special
                           }

# Map from array type descriptors to type names; JVMSpec 6.newarray
ARRAY_TYPE_MAPPING = {4: "boolean",
                      5: "char",
                      6: "float",
                      7: "double",
                      8: "byte",
                      9: "short",
                      10: "int",
                      11: "long"}

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
    0: ("nop", 0, "", ""),
    1: ("aconst_null", 0, "", ""),
    2: ("iconst_m1", 0, "", ""),
    3: ("iconst_0", 0, "", ""),
    4: ("iconst_1", 0, "", ""),
    5: ("iconst_2", 0, "", ""),
    6: ("iconst_3", 0, "", ""),
    7: ("iconst_4", 0, "", ""),
    8: ("iconst_5", 0, "", ""),
    9: ("lconst_0", 0, "", ""),
    10: ("lconst_1", 0, "", ""),
    11: ("fconst_0", 0, "", ""),
    12: ("fconst_1", 0, "", ""),
    13: ("fconst_2", 0, "", ""),
    14: ("dconst_0", 0, "", ""),
    15: ("dconst_1", 0, "", ""),
    16: ("bipush", 1, "b", "#"),
    17: ("sipush", 2, "h", "#"),
    18: ("ldc", 1, "b", "c"),
    19: ("ldc_w", 2, "H", "c"),
    20: ("ldc2_w", 2, "H", "c"),
    21: ("iload", 1, "B", "l"),
    22: ("lload", 1, "B", "l"),
    23: ("fload", 1, "B", "l"),
    24: ("dload", 1, "B", "l"),
    25: ("aload", 1, "B", "l"),
    26: ("iload_0", 0, "", ""),
    27: ("iload_1", 0, "", ""),
    28: ("iload_2", 0, "", ""),
    29: ("iload_3", 0, "", ""),
    30: ("lload_0", 0, "", ""),
    31: ("lload_1", 0, "", ""),
    32: ("lload_2", 0, "", ""),
    33: ("lload_3", 0, "", ""),
    34: ("fload_0", 0, "", ""),
    35: ("fload_1", 0, "", ""),
    36: ("fload_2", 0, "", ""),
    37: ("fload_3", 0, "", ""),
    38: ("dload_0", 0, "", ""),
    39: ("dload_1", 0, "", ""),
    40: ("dload_2", 0, "", ""),
    41: ("dload_3", 0, "", ""),
    42: ("aload_0", 0, "", ""),
    43: ("aload_1", 0, "", ""),
    44: ("aload_2", 0, "", ""),
    45: ("aload_3", 0, "", ""),
    46: ("iaload", 0, "", ""),
    47: ("laload", 0, "", ""),
    48: ("faload", 0, "", ""),
    49: ("daload", 0, "", ""),
    50: ("aaload", 0, "", ""),
    51: ("baload", 0, "", ""),
    52: ("caload", 0, "", ""),
    53: ("saload", 0, "", ""),
    54: ("istore", 1, "B", "l"),
    55: ("lstore", 1, "B", "l"),
    56: ("fstore", 1, "B", "l"),
    57: ("dstore", 1, "B", "l"),
    58: ("astore", 1, "B", "l"),
    59: ("istore_0", 0, "", ""),
    60: ("istore_1", 0, "", ""),
    61: ("istore_2", 0, "", ""),
    62: ("istore_3", 0, "", ""),
    63: ("lstore_0", 0, "", ""),
    64: ("lstore_1", 0, "", ""),
    65: ("lstore_2", 0, "", ""),
    66: ("lstore_3", 0, "", ""),
    67: ("fstore_0", 0, "", ""),
    68: ("fstore_1", 0, "", ""),
    69: ("fstore_2", 0, "", ""),
    70: ("fstore_3", 0, "", ""),
    71: ("dstore_0", 0, "", ""),
    72: ("dstore_1", 0, "", ""),
    73: ("dstore_2", 0, "", ""),
    74: ("dstore_3", 0, "", ""),
    75: ("astore_0", 0, "", ""),
    76: ("astore_1", 0, "", ""),
    77: ("astore_2", 0, "", ""),
    78: ("astore_3", 0, "", ""),
    79: ("iastore", 0, "", ""),
    80: ("lastore", 0, "", ""),
    81: ("fastore", 0, "", ""),
    82: ("dastore", 0, "", ""),
    83: ("aastore", 0, "", ""),
    84: ("bastore", 0, "", ""),
    85: ("castore", 0, "", ""),
    86: ("sastore", 0, "", ""),
    87: ("pop", 0, "", ""),
    88: ("pop2", 0, "", ""),
    89: ("dup", 0, "", ""),
    90: ("dup_x1", 0, "", ""),
    91: ("dup_x2", 0, "", ""),
    92: ("dup2", 0, "", ""),
    93: ("dup2_x1", 0, "", ""),
    94: ("dup2_x2", 0, "", ""),
    95: ("swap", 0, "", ""),
    96: ("iadd", 0, "", ""),
    97: ("ladd", 0, "", ""),
    98: ("fadd", 0, "", ""),
    99: ("dadd", 0, "", ""),
    100: ("isub", 0, "", ""),
    101: ("lsub", 0, "", ""),
    102: ("fsub", 0, "", ""),
    103: ("dsub", 0, "", ""),
    104: ("imul", 0, "", ""),
    105: ("lmul", 0, "", ""),
    106: ("fmul", 0, "", ""),
    107: ("dmul", 0, "", ""),
    108: ("idiv", 0, "", ""),
    109: ("ldiv", 0, "", ""),
    110: ("fdiv", 0, "", ""),
    111: ("ddiv", 0, "", ""),
    112: ("irem", 0, "", ""),
    113: ("lrem", 0, "", ""),
    114: ("frem", 0, "", ""),
    115: ("drem", 0, "", ""),
    116: ("ineg", 0, "", ""),
    117: ("lneg", 0, "", ""),
    118: ("fneg", 0, "", ""),
    119: ("dneg", 0, "", ""),
    120: ("ishl", 0, "", ""),
    121: ("lshl", 0, "", ""),
    122: ("ishr", 0, "", ""),
    123: ("lshr", 0, "", ""),
    124: ("iushr", 0, "", ""),
    125: ("lushr", 0, "", ""),
    126: ("iand", 0, "", ""),
    127: ("land", 0, "", ""),
    128: ("ior", 0, "", ""),
    129: ("lor", 0, "", ""),
    130: ("ixor", 0, "", ""),
    131: ("lxor", 0, "", ""),
    132: ("iinc", 2, "Bb", "l#"),
    133: ("i2l", 0, "", ""),
    134: ("i2f", 0, "", ""),
    135: ("i2d", 0, "", ""),
    136: ("l2i", 0, "", ""),
    137: ("l2f", 0, "", ""),
    138: ("l2d", 0, "", ""),
    139: ("f2i", 0, "", ""),
    140: ("f2l", 0, "", ""),
    141: ("f2d", 0, "", ""),
    142: ("d2i", 0, "", ""),
    143: ("d2l", 0, "", ""),
    144: ("d2f", 0, "", ""),
    145: ("i2b", 0, "", ""),
    146: ("i2c", 0, "", ""),
    147: ("i2s", 0, "", ""),
    148: ("lcmp", 0, "", ""),
    149: ("fcmpl", 0, "", ""),
    150: ("fcmpg", 0, "", ""),
    151: ("dcmpl", 0, "", ""),
    152: ("dcmpg", 0, "", ""),
    153: ("ifeq", 2, "h", "o"),
    154: ("ifne", 2, "h", "o"),
    155: ("iflt", 2, "h", "o"),
    156: ("ifge", 2, "h", "o"),
    157: ("ifgt", 2, "h", "o"),
    158: ("ifle", 2, "h", "o"),
    159: ("if_icmpeq", 2, "h", "o"),
    160: ("if_icmpne", 2, "h", "o"),
    161: ("if_icmplt", 2, "h", "o"),
    162: ("if_icmpge", 2, "h", "o"),
    163: ("if_icmpgt", 2, "h", "o"),
    164: ("if_icmple", 2, "h", "o"),
    165: ("if_acmpeq", 2, "h", "o"),
    166: ("if_acmpne", 2, "h", "o"),
    167: ("goto", 2, "h", "o"),
    168: ("jsr", 2, "h", "o"),
    169: ("ret", 1, "B", "l"),
    170: ("tableswitch", None, "", ""),  # variable number of arguments
    171: ("lookupswitch", None, "", ""),  # variable number of arguments
    172: ("ireturn", 0, "", ""),
    173: ("lreturn", 0, "", ""),
    174: ("freturn", 0, "", ""),
    175: ("dreturn", 0, "", ""),
    176: ("areturn", 0, "", ""),
    177: ("return", 0, "", ""),
    178: ("getstatic", 2, "H", "c"),
    179: ("putstatic", 2, "H", "c"),
    180: ("getfield", 2, "H", "c"),
    181: ("putfield", 2, "H", "c"),
    182: ("invokevirtual", 2, "H", "c"),
    183: ("invokespecial", 2, "H", "c"),
    184: ("invokestatic", 2, "H", "c"),
    185: ("invokeinterface", 4, "HBB", "c#0"),
    # For historical reasons, opcode value 186 is not used
    187: ("new", 2, "H", "c"),
    188: ("newarray", 1, "B", "a"),
    189: ("anewarray", 2, "H", "c"),
    190: ("arraylength", 0, "", ""),
    191: ("athrow", 0, "", ""),
    192: ("checkcast", 2, "H", "c"),
    193: ("instanceof", 2, "H", "c"),
    194: ("monitorenter", 0, "", ""),
    195: ("monitorexit", 0, "", ""),
    196: ("wide", None, "", ""),  # 3 or 5 arguments, stack changes according to modified element
    197: ("multianewarray", 3, "HB", "c#"),
    198: ("ifnull", 2, "h", "o"),
    199: ("ifnonnull", 2, "h", "o"),
    200: ("goto_w", 4, "i", "o"),
    201: ("jsr_w", 4, "i", "o"),
    # Reserved opcodes; cannot appear in a class file
    # 202: ("breakpoint", None),
    # 254: ("impdep1", None),
    # 255: ("impdep2", None),
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
        modifiers.append("public")
    if ((flags & PRIVATE) != 0):
        modifiers.append("private")
    if ((flags & PROTECTED) != 0):
        modifiers.append("protected")
    if ((flags & STATIC) != 0):
        modifiers.append("static")
    if ((flags & FINAL) != 0):
        modifiers.append("final")
    if ((flags & SYNCHRONIZED) != 0):
        modifiers.append("synchronized")
    if ((flags & VOLATILE) != 0):
        modifiers.append("volatile")
    if ((flags & TRANSIENT) != 0):
        modifiers.append("transient")
    if ((flags & NATIVE) != 0):
        modifiers.append("native")
    if ((flags & INTERFACE) != 0):
        modifiers.append("interface")
    if ((flags & ABSTRACT) != 0):
        modifiers.append("abstract")
    if ((flags & STRICT) != 0):
        modifiers.append("strict")
    return " ".join(modifiers)


def fqcn(s):
    # JVMSpec 4.2
    return s.replace("/", ".")


def demangle_field_descriptor(s, void_allowed=False):
    """Convert field descriptor to a string describing the field.

    Returns (description, rest)"""
    # JVMSpec 4.3.2
    dim = 0
    ii = 0
    while ii < len(s):
        c = s[ii]
        if c == "[":
            dim += 1
        elif c == "V" and void_allowed:
            if dim > 0:
                raise Exception("Cannot have array of void")
            return "void", s[ii + 1:]
        elif c == "L":
            endpoint = s.find(";", ii)
            if endpoint == -1:
                raise Exception("Failed to find end of classname")
            classname = fqcn(s[ii + 1:endpoint])
            return classname + dim * "[]", s[endpoint + 1:]
        elif c in DESCRIPTOR_TYPE_MAPPING:
            return DESCRIPTOR_TYPE_MAPPING[c] + dim * "[]", s[ii + 1:]
        else:
            raise Exception("Unknown descriptor code %s" % c)
        ii += 1
    raise Exception("Failed to find single field in %s" % s)


def demangle_method_descriptor(s):
    """Convert method descriptor to a pair of strings describing parameters and return type."""
    # JVMSpec 4.3.3
    if s[0] != "(":
        raise Exception("Method descriptor %s should start with (" % s)
    s = s[1:]
    params = []
    while s[0] != ")" and len(s) > 0:
        result, s = demangle_field_descriptor(s)
        params.append(result)
    if (len(s) == 0 or s[0] != ")"):
        raise Exception("Method descriptor %s should include )" % s)
    return_type, s = demangle_field_descriptor(s[1:], void_allowed=True)
    if len(s) > 0:
        raise Exception("Unexpected extra text in %s" % s)
    return (params, return_type)
