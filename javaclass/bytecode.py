#!/usr/bin/env python

"""
Java bytecode conversion. Specification found at the following URL:
http://java.sun.com/docs/books/vmspec/2nd-edition/html/Instructions2.doc.html

NOTE: Synchronized constructs are not actually supported.

Copyright (C) 2004, 2005, 2006, 2011 Paul Boddie <paul@boddie.org.uk>

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

import classfile
from dis import cmp_op, opname # for access to Python bytecode values and operators
try:
    from dis import opmap
except ImportError:
    opmap = {}
    for i in range(0, len(opname)):
        opmap[opname[i]] = i
from UserDict import UserDict
import new

# Bytecode production classes.

class BytecodeWriter:

    "A Python bytecode writer."

    def __init__(self):

        "Initialise the writer."

        # A stack of loop start instructions corresponding to loop blocks.
        self.loops = []

        # A stack of loop block or exception block start positions.
        self.blocks = []

        # A stack of exception block handler pointers.
        self.exception_handlers = []

        # A list of exception offset details.
        self.exception_offsets = []

        # A dictionary mapping labels to jump instructions referencing such labels.
        self.jumps = {}

        # The output values, including "lazy" subvalues which will need evaluating.
        self.output = []

        # The current Python bytecode instruction position.
        self.position = 0

        # Stack depth estimation.
        self.stack_depth = 0
        self.max_stack_depth = 0

        # Local variable estimation.
        self.max_locals = 0

        # Mapping from values to indexes.
        self.constants = {}

        # Mapping from names to indexes.
        # NOTE: This may be acquired from elsewhere.
        #self.globals = {}

        # Mapping from names to indexes.
        self.names = {}

        # A list of constants used as exception handler return addresses.
        self.constants_for_exceptions = []

        # A list of external names.
        self.external_names = []

    def get_bytecodes(self):

        "Return the list of bytecodes written to the writer."

        output = []
        for element in self.output:
            if isinstance(element, LazySubValue):
                value = element.value
            else:
                value = element
            output.append(value)
        return output

    def get_output(self):

        "Return the output of the writer as a string."

        output = []
        for value in self.get_bytecodes():
            # NOTE: ValueError gets raised for bad values here.
            output.append(chr(value))
        return "".join(output)

    def get_constants(self):

        """
        Return a list of constants with ordering significant to the code
        employing them.
        """

        l = self._get_list(self._invert(self.constants))
        result = []
        for i in l:
            if isinstance(i, LazyValue):
                result.append(i.get_value())
            else:
                result.append(i)
        return result

    #def get_globals(self):
    #    return self._get_list(self._invert(self.globals))

    def get_names(self):

        """
        Return a list of names with ordering significant to the code employing
        them.
        """

        return self._get_list(self._invert(self.names))

    def _invert(self, d):

        """
        Return a new dictionary whose key-to-value mapping is in the inverse of
        that found in 'd'.
        """

        inverted = {}
        for k, v in d.items():
            inverted[v] = k
        return inverted

    def _get_list(self, d):

        """
        Traverse the dictionary 'd' returning a list whose values appear at the
        position denoted by each value's key in 'd'.
        """

        l = []
        for i in range(0, len(d.keys())):
            l.append(d[i])
        return l

    # Administrative methods.

    def update_stack_depth(self, change):

        """
        Given the stated 'change' in stack depth, update the maximum stack depth
        where appropriate.
        """

        self.stack_depth += change
        if self.stack_depth > self.max_stack_depth:
            self.max_stack_depth = self.stack_depth

    def update_locals(self, index):

        """
        Given the stated 'index' of a local variable, update the maximum local
        variable index where appropriate.
        """

        if index > self.max_locals:
            self.max_locals = index

    # Special methods.

    def _write_value(self, value):

        """
        Write the given 'value' at the current output position.
        """

        if isinstance(value, LazyValue):
            # NOTE: Assume a 16-bit value.
            self.output.append(value.values[0])
            self.output.append(value.values[1])
            self.position += 2
        elif value <= 0xffff:
            self.output.append(value & 0xff)
            self.output.append((value & 0xff00) >> 8)
            self.position += 2
        else:
            # NOTE: EXTENDED_ARG not yet supported.
            raise ValueError, value

    def _rewrite_value(self, position, value):

        """
        At the given output 'position', rewrite the given 'value'.
        """

        # NOTE: Assume a 16-bit value.
        if value <= 0xffff:
            self.output[position] = (value & 0xff)
            self.output[position + 1] = ((value & 0xff00) >> 8)
        else:
            # NOTE: EXTENDED_ARG not yet supported.
            raise ValueError, value

    # Higher level methods.

    def use_external_name(self, name):
        # NOTE: Remove array and object indicators.
        self.external_names.append(name)

    def setup_loop(self):
        self.loops.append(self.position)
        self.output.append(opmap["SETUP_LOOP"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def end_loop(self):
        current_loop_start = self.loops.pop()
        current_loop_real_start = self.blocks.pop()
        #print "<", self.blocks, current_loop_real_start
        # Fix the iterator delta.
        # NOTE: Using 3 as the assumed length of the FOR_ITER instruction.
        self.jump_absolute(current_loop_real_start)
        self._rewrite_value(current_loop_real_start + 1, self.position - current_loop_real_start - 3)
        self.pop_block()
        # Fix the loop delta.
        # NOTE: Using 3 as the assumed length of the SETUP_LOOP instruction.
        self._rewrite_value(current_loop_start + 1, self.position - current_loop_start - 3)

    def jump_to_label(self, status, name):
        # Record the instruction using the jump.
        jump_instruction = self.position
        if status is None:
            self.jump_forward()
        elif status:
            self.jump_if_true()
        else:
            self.jump_if_false()
        # Record the following instruction, too.
        if not self.jumps.has_key(name):
            self.jumps[name] = []
        self.jumps[name].append((jump_instruction, self.position))

    def start_label(self, name):
        # Fill in all jump instructions.
        for jump_instruction, following_instruction in self.jumps[name]:
            self._rewrite_value(jump_instruction + 1, self.position - following_instruction)
        del self.jumps[name]

    def load_const_ret(self, value):
        self.constants_for_exceptions.append(value)
        self.load_const(value)

    def ret(self, index):
        self.load_fast(index)

        # Previously, the constant stored on the stack by jsr/jsr_w was stored
        # in a local variable. In the JVM, extracting the value from the local
        # variable and jumping can be done at runtime. In the Python VM, any
        # jump target must be known in advance and written into the bytecode.

        for constant in self.constants_for_exceptions:
            self.dup_top()              # Stack: actual-address, actual-address
            self.load_const(constant)   # Stack: actual-address, actual-address, suggested-address
            self.compare_op("==")       # Stack: actual-address, result
            self.jump_to_label(0, "const")
            self.pop_top()              # Stack: actual-address
            self.pop_top()              # Stack:
            self.jump_absolute(constant)
            self.start_label("const")
            self.pop_top()              # Stack: actual-address

        # NOTE: If we get here, something is really wrong.

        self.pop_top()              # Stack:

    def setup_except(self, target):
        self.blocks.append(self.position)
        self.exception_handlers.append(target)
        #print "-", self.position, target
        self.output.append(opmap["SETUP_EXCEPT"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def setup_finally(self, target):
        self.blocks.append(self.position)
        self.exception_handlers.append(target)
        #print "-", self.position, target
        self.output.append(opmap["SETUP_FINALLY"])
        self.position += 1
        self._write_value(0) # To be filled in later

    def end_exception(self):
        current_exception_start = self.blocks.pop()
        # Convert the "lazy" absolute value.
        current_exception_target = self.exception_handlers.pop()
        # NOTE: Using 3 as the assumed length of the SETUP_* instruction.
        self.exception_offsets.append((current_exception_start + 1, current_exception_target, current_exception_start))

    def end_exceptions(self):
        for position, exception_target, exception_start in self.exception_offsets:
            #print "*", exception_start, exception_target.get_value()
            self._rewrite_value(position, exception_target.get_value() - exception_start - 3)

    def start_handler(self, exc_name, class_file):

        # Where handlers are begun, produce bytecode to test the type of
        # the exception.
        # NOTE: Since RAISE_VARARGS and END_FINALLY are not really documented,
        # NOTE: we store the top of the stack and use it later to trigger the
        # NOTE: magic processes when re-raising.
        self.use_external_name(str(exc_name))

        self.rot_two()                      # Stack: raised-exception, exception
        self.dup_top()                      # Stack: raised-exception, exception, exception
        # Handled exceptions are wrapped before being thrown.
        self.load_global("Exception")       # Stack: raised-exception, exception, exception, Exception
        self.compare_op("exception match")  # Stack: raised-exception, exception, result
        self.jump_to_label(0, "next")
        self.pop_top()                      # Stack: raised-exception, exception
        self.dup_top()                      # Stack: raised-exception, exception, exception
        self.load_attr("args")              # Stack: raised-exception, exception, args
        self.load_const(0)                  # Stack: raised-exception, exception, args, 0
        self.binary_subscr()                # Stack: raised-exception, exception, exception-object
        load_class_name(class_file, str(exc_name), self)
                                            # Stack: raised-exception, exception, exception-object, handled-exception
        self.load_global("isinstance")      # Stack: raised-exception, exception, exception-object, handled-exception, isinstance
        self.rot_three()                    # Stack: raised-exception, exception, isinstance, exception-object, handled-exception
        self.call_function(2)               # Stack: raised-exception, exception, result
        self.jump_to_label(1, "handler")
        self.start_label("next")
        self.pop_top()                      # Stack: raised-exception, exception
        self.rot_two()                      # Stack: exception, raised-exception
        self.end_finally()
        self.start_label("handler")
        self.pop_top()                      # Stack: raised-exception, exception

    # Complicated methods.

    def load_const(self, value):
        self.output.append(opmap["LOAD_CONST"])
        if not self.constants.has_key(value):
            self.constants[value] = len(self.constants.keys())
        self.position += 1
        self._write_value(self.constants[value])
        self.update_stack_depth(1)

    def load_global(self, name):
        self.output.append(opmap["LOAD_GLOBAL"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(1)

    def load_attr(self, name):
        self.output.append(opmap["LOAD_ATTR"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])

    def load_name(self, name):
        self.output.append(opmap["LOAD_NAME"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(1)

    def load_fast(self, index):
        self.output.append(opmap["LOAD_FAST"])
        self.position += 1
        self._write_value(index)
        self.update_stack_depth(1)
        self.update_locals(index)

    def store_attr(self, name):
        self.output.append(opmap["STORE_ATTR"])
        if not self.names.has_key(name):
            self.names[name] = len(self.names.keys())
        self.position += 1
        self._write_value(self.names[name])
        self.update_stack_depth(-1)

    def store_fast(self, index):
        self.output.append(opmap["STORE_FAST"])
        self.position += 1
        self._write_value(index)
        self.update_stack_depth(-1)
        self.update_locals(index)

    def for_iter(self):
        self.blocks.append(self.position)
        #print ">", self.blocks
        self.output.append(opmap["FOR_ITER"])
        self.position += 1
        self._write_value(0) # To be filled in later
        self.update_stack_depth(1)

    def break_loop(self):
        self.output.append(opmap["BREAK_LOOP"])
        self.position += 1
        self.jump_absolute(self.blocks[-1])

    # Normal bytecode generators.

    def get_iter(self):
        self.output.append(opmap["GET_ITER"])
        self.position += 1

    def jump_if_false(self, offset=0):
        self.output.append(opmap["JUMP_IF_FALSE"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_if_true(self, offset=0):
        self.output.append(opmap["JUMP_IF_TRUE"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_forward(self, offset=0):
        self.output.append(opmap["JUMP_FORWARD"])
        self.position += 1
        self._write_value(offset) # May be filled in later

    def jump_absolute(self, address=0):
        self.output.append(opmap["JUMP_ABSOLUTE"])
        self.position += 1
        self._write_value(address) # May be filled in later

    def build_tuple(self, count):
        self.output.append(opmap["BUILD_TUPLE"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-(count - 1))

    def build_list(self, count):
        self.output.append(opmap["BUILD_LIST"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-(count - 1))

    def pop_top(self):
        self.output.append(opmap["POP_TOP"])
        self.position += 1
        self.update_stack_depth(-1)

    def dup_top(self):
        self.output.append(opmap["DUP_TOP"])
        self.position += 1
        self.update_stack_depth(1)

    def dup_topx(self, count):
        self.output.append(opmap["DUP_TOPX"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(count)

    def rot_two(self):
        self.output.append(opmap["ROT_TWO"])
        self.position += 1

    def rot_three(self):
        self.output.append(opmap["ROT_THREE"])
        self.position += 1

    def rot_four(self):
        self.output.append(opmap["ROT_FOUR"])
        self.position += 1

    def call_function(self, count):
        self.output.append(opmap["CALL_FUNCTION"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-count)

    def call_function_var(self, count):
        self.output.append(opmap["CALL_FUNCTION_VAR"])
        self.position += 1
        self._write_value(count)
        self.update_stack_depth(-count-1)

    def binary_subscr(self):
        self.output.append(opmap["BINARY_SUBSCR"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_add(self):
        self.output.append(opmap["BINARY_ADD"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_divide(self):
        self.output.append(opmap["BINARY_DIVIDE"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_multiply(self):
        self.output.append(opmap["BINARY_MULTIPLY"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_modulo(self):
        self.output.append(opmap["BINARY_MODULO"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_subtract(self):
        self.output.append(opmap["BINARY_SUBTRACT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_and(self):
        self.output.append(opmap["BINARY_AND"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_or(self):
        self.output.append(opmap["BINARY_XOR"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_lshift(self):
        self.output.append(opmap["BINARY_LSHIFT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_rshift(self):
        self.output.append(opmap["BINARY_RSHIFT"])
        self.position += 1
        self.update_stack_depth(-1)

    def binary_xor(self):
        self.output.append(opmap["BINARY_XOR"])
        self.position += 1
        self.update_stack_depth(-1)

    def store_subscr(self):
        self.output.append(opmap["STORE_SUBSCR"])
        self.position += 1
        self.update_stack_depth(-3)

    def unary_negative(self):
        self.output.append(opmap["UNARY_NEGATIVE"])
        self.position += 1

    def slice_0(self):
        self.output.append(opmap["SLICE+0"])
        self.position += 1

    def slice_1(self):
        self.output.append(opmap["SLICE+1"])
        self.position += 1

    def compare_op(self, op):
        self.output.append(opmap["COMPARE_OP"])
        self.position += 1
        self._write_value(list(cmp_op).index(op))
        self.update_stack_depth(-1)

    def return_value(self):
        self.output.append(opmap["RETURN_VALUE"])
        self.position += 1
        self.update_stack_depth(-1)

    def raise_varargs(self, count):
        self.output.append(opmap["RAISE_VARARGS"])
        self.position += 1
        self._write_value(count)

    def pop_block(self):
        self.output.append(opmap["POP_BLOCK"])
        self.position += 1

    def end_finally(self):
        self.output.append(opmap["END_FINALLY"])
        self.position += 1

    def unpack_sequence(self, count):
        self.output.append(opmap["UNPACK_SEQUENCE"])
        self.position += 1
        self._write_value(count)

    # Debugging.

    def print_item(self):
        self.output.append(opmap["PRINT_ITEM"])
        self.position += 1

# Utility classes and functions.

class LazyDict(UserDict):
    def __getitem__(self, key):
        if not self.data.has_key(key):
            # NOTE: Assume 16-bit value.
            self.data[key] = LazyValue(2)
        return self.data[key]
    def __setitem__(self, key, value):
        if self.data.has_key(key):
            existing_value = self.data[key]
            if isinstance(existing_value, LazyValue):
                existing_value.set_value(value)
                return
        self.data[key] = value

class LazyValue:
    def __init__(self, nvalues):
        self.values = []
        for i in range(0, nvalues):
            self.values.append(LazySubValue())
    def set_value(self, value):
        # NOTE: Assume at least 16-bit value. No "filling" performed.
        if value <= 0xffff:
            self.values[0].set_value(value & 0xff)
            self.values[1].set_value((value & 0xff00) >> 8)
        else:
            # NOTE: EXTENDED_ARG not yet supported.
            raise ValueError, value
    def get_value(self):
        value = 0
        values = self.values[:]
        for i in range(0, len(values)):
            value = (value << 8) + values.pop().value
        return value

class LazySubValue:
    def __init__(self):
        self.value = 0
    def set_value(self, value):
        self.value = value

def signed(value, limit):

    """
    Return the signed integer from the unsigned 'value', where 'limit' (a value
    one greater than the highest possible positive integer) is used to determine
    whether a negative or positive result is produced.
    """

    d, r = divmod(value, limit)
    if d == 1:
        mask = limit * 2 - 1
        return -1 - (value ^ mask)
    else:
        return value

def signed1(value):
    return signed(value, 0x80)

def signed2(value):
    return signed(value, 0x8000)

def signed4(value):
    return signed(value, 0x80000000)

def load_class_name(class_file, full_class_name, program):
    this_class_name = str(class_file.this_class.get_python_name())
    this_class_parts = this_class_name.split(".")
    class_parts = full_class_name.split(".")

    # Only use the full path if different from this class's path.

    if class_parts[:-1] != this_class_parts[:-1]:
        program.use_external_name(full_class_name)
        program.load_global(class_parts[0])
        for class_part in class_parts[1:]:
            program.load_attr(class_part)   # Stack: classref
    else:
        program.load_global(class_parts[-1])

atypes_to_default_values = {
    4 : 0,      # bool (NOTE: Should be False.)
    5 : u"",    # char
    6 : 0.0,    # float
    7 : 0.0,    # double
    8 : 0,      # byte
    9 : 0,      # short
    10: 0,      # int
    11: 0       # long
}

def get_default_for_atype(atype):
    global atypes_to_default_values
    return atypes_to_default_values.get(atype)

# Bytecode conversion.

class BytecodeReader:

    "A generic Java bytecode reader."

    def __init__(self, class_file):

        """
        Initialise the reader with a 'class_file' containing essential
        information for any bytecode inspection activity.
        """

        self.class_file = class_file
        self.position_mapping = LazyDict()

    def process(self, method, program):

        """
        Process the given 'method' (obtained from the class file), using the
        given 'program' to write translated Python bytecode instructions.
        """

        self.java_position = 0
        self.in_finally = 0
        self.method = method

        # NOTE: Potentially unreliable way of getting necessary information.

        code, exception_table = None, None
        for attribute in method.attributes:
            if isinstance(attribute, classfile.CodeAttributeInfo):
                code, exception_table = attribute.code, attribute.exception_table
                break

        # Where no code was found, write a very simple placeholder routine.
        # This is useful for interfaces and abstract classes.
        # NOTE: Assess the correctness of doing this. An exception should really
        # NOTE: be raised instead.

        if code is None:
            program.load_const(None)
            program.return_value()
            return

        # Produce a structure which permits fast access to exception details.

        exception_block_start = {}
        exception_block_end = {}
        exception_block_handler = {}
        reversed_exception_table = exception_table[:]
        reversed_exception_table.reverse()

        # Later entries have wider coverage than earlier entries.

        for exception in reversed_exception_table:

            # NOTE: Strange case with javac from JDK 1.4 but not JDK 1.3:
            # NOTE: start_pc == handler_pc
            # Merge all finally handlers with the same handler location.

            if exception.catch_type == 0 and exception_block_handler.get(exception.handler_pc, []) != []:

                # Make a new definition.

                new_exception = classfile.ExceptionInfo()
                new_exception.catch_type = exception.catch_type
                new_exception.handler_pc = exception.handler_pc
                new_exception.end_pc = exception.end_pc
                new_exception.start_pc = exception.start_pc

                # Find the previous exception handler definition.
 
                for previous_exception in exception_block_handler[exception.handler_pc][:]:
                    if previous_exception.catch_type == 0:
                        new_exception.end_pc = max(new_exception.end_pc, previous_exception.end_pc)
                        new_exception.start_pc = min(new_exception.start_pc, previous_exception.start_pc)

                        # Remove this exception from the lists.

                        exception_block_handler[previous_exception.handler_pc].remove(previous_exception)
                        exception_block_start[previous_exception.start_pc].remove(previous_exception)
                        exception_block_end[previous_exception.end_pc].remove(previous_exception)
                        break

                # Use the new definition instead.

                exception = new_exception

            # Index start positions.

            if not exception_block_start.has_key(exception.start_pc):
                exception_block_start[exception.start_pc] = []
            exception_block_start[exception.start_pc].append(exception)

            # Index end positions.

            if not exception_block_end.has_key(exception.end_pc):
                exception_block_end[exception.end_pc] = []
            exception_block_end[exception.end_pc].append(exception)

            # Index handler positions.

            if not exception_block_handler.has_key(exception.handler_pc):
                exception_block_handler[exception.handler_pc] = []
            exception_block_handler[exception.handler_pc].append(exception)

        # Process each instruction in the code.

        while self.java_position < len(code):
            self.position_mapping[self.java_position] = program.position

            # Insert exception handling constructs.

            block_starts = exception_block_start.get(self.java_position, [])
            for exception in block_starts:

                # Note that the absolute position is used.

                if exception.catch_type == 0:
                    program.setup_finally(self.position_mapping[exception.handler_pc])
                else:
                    program.setup_except(self.position_mapping[exception.handler_pc])

            if block_starts:
                self.in_finally = 0

            # Insert exception handler details.
            # NOTE: Ensure that pop_block is reachable by possibly inserting it at the start of finally handlers.
            # NOTE: Insert a check for the correct exception at the start of each handler.

            for exception in exception_block_handler.get(self.java_position, []):
                program.end_exception()
                if exception.catch_type == 0:
                    self.in_finally = 1
                else:
                    program.start_handler(self.class_file.constants[exception.catch_type - 1].get_python_name(), self.class_file)

            # Process the bytecode at the current position.

            bytecode = ord(code[self.java_position])
            mnemonic, number_of_arguments = self.java_bytecodes[bytecode]
            number_of_arguments = self.process_bytecode(mnemonic, number_of_arguments, code, program)
            next_java_position = self.java_position + 1 + number_of_arguments

            # Insert exception block end details.

            for exception in exception_block_end.get(next_java_position, []):

                # NOTE: Insert jump beyond handlers.
                # NOTE: program.jump_forward/absolute(...)
                # NOTE: Insert end finally at end of handlers as well as where "ret" occurs.

                if exception.catch_type != 0:
                    program.pop_block()

            # Only advance the JVM position after sneaking in extra Python
            # instructions.

            self.java_position = next_java_position

        # Tidy up exceptions.

        program.end_exceptions()

    def process_bytecode(self, mnemonic, number_of_arguments, code, program):

        """
        Process a bytecode instruction with the given 'mnemonic' and
        'number_of_arguments'. The 'code' parameter contains the full method
        code so that argument data can be inspected. The 'program' parameter is
        used to produce a Python translation of the instruction.
        """

        if number_of_arguments is not None:
            arguments = [ord(b) for b in code[self.java_position + 1:self.java_position + 1 + number_of_arguments]]

            # Call the handler.

            getattr(self, mnemonic)(arguments, program)
            return number_of_arguments
        else:
            # Call the handler.

            return getattr(self, mnemonic)(code[self.java_position+1:], program)

    java_bytecodes = {
        # code : (mnemonic, number of following bytes, change in stack)
        0 : ("nop", 0),
        1 : ("aconst_null", 0),
        2 : ("iconst_m1", 0),
        3 : ("iconst_0", 0),
        4 : ("iconst_1", 0),
        5 : ("iconst_2", 0),
        6 : ("iconst_3", 0),
        7 : ("iconst_4", 0),
        8 : ("iconst_5", 0),
        9 : ("lconst_0", 0),
        10 : ("lconst_1", 0),
        11 : ("fconst_0", 0),
        12 : ("fconst_1", 0),
        13 : ("fconst_2", 0),
        14 : ("dconst_0", 0),
        15 : ("dconst_1", 0),
        16 : ("bipush", 1),
        17 : ("sipush", 2),
        18 : ("ldc", 1),
        19 : ("ldc_w", 2),
        20 : ("ldc2_w", 2),
        21 : ("iload", 1),
        22 : ("lload", 1),
        23 : ("fload", 1),
        24 : ("dload", 1),
        25 : ("aload", 1),
        26 : ("iload_0", 0),
        27 : ("iload_1", 0),
        28 : ("iload_2", 0),
        29 : ("iload_3", 0),
        30 : ("lload_0", 0),
        31 : ("lload_1", 0),
        32 : ("lload_2", 0),
        33 : ("lload_3", 0),
        34 : ("fload_0", 0),
        35 : ("fload_1", 0),
        36 : ("fload_2", 0),
        37 : ("fload_3", 0),
        38 : ("dload_0", 0),
        39 : ("dload_1", 0),
        40 : ("dload_2", 0),
        41 : ("dload_3", 0),
        42 : ("aload_0", 0),
        43 : ("aload_1", 0),
        44 : ("aload_2", 0),
        45 : ("aload_3", 0),
        46 : ("iaload", 0),
        47 : ("laload", 0),
        48 : ("faload", 0),
        49 : ("daload", 0),
        50 : ("aaload", 0),
        51 : ("baload", 0),
        52 : ("caload", 0),
        53 : ("saload", 0),
        54 : ("istore", 1),
        55 : ("lstore", 1),
        56 : ("fstore", 1),
        57 : ("dstore", 1),
        58 : ("astore", 1),
        59 : ("istore_0", 0),
        60 : ("istore_1", 0),
        61 : ("istore_2", 0),
        62 : ("istore_3", 0),
        63 : ("lstore_0", 0),
        64 : ("lstore_1", 0),
        65 : ("lstore_2", 0),
        66 : ("lstore_3", 0),
        67 : ("fstore_0", 0),
        68 : ("fstore_1", 0),
        69 : ("fstore_2", 0),
        70 : ("fstore_3", 0),
        71 : ("dstore_0", 0),
        72 : ("dstore_1", 0),
        73 : ("dstore_2", 0),
        74 : ("dstore_3", 0),
        75 : ("astore_0", 0),
        76 : ("astore_1", 0),
        77 : ("astore_2", 0),
        78 : ("astore_3", 0),
        79 : ("iastore", 0),
        80 : ("lastore", 0),
        81 : ("fastore", 0),
        82 : ("dastore", 0),
        83 : ("aastore", 0),
        84 : ("bastore", 0),
        85 : ("castore", 0),
        86 : ("sastore", 0),
        87 : ("pop", 0),
        88 : ("pop2", 0),
        89 : ("dup", 0),
        90 : ("dup_x1", 0),
        91 : ("dup_x2", 0),
        92 : ("dup2", 0),
        93 : ("dup2_x1", 0),
        94 : ("dup2_x2", 0),
        95 : ("swap", 0),
        96 : ("iadd", 0),
        97 : ("ladd", 0),
        98 : ("fadd", 0),
        99 : ("dadd", 0),
        100 : ("isub", 0),
        101 : ("lsub", 0),
        102 : ("fsub", 0),
        103 : ("dsub", 0),
        104 : ("imul", 0),
        105 : ("lmul", 0),
        106 : ("fmul", 0),
        107 : ("dmul", 0),
        108 : ("idiv", 0),
        109 : ("ldiv", 0),
        110 : ("fdiv", 0),
        111 : ("ddiv", 0),
        112 : ("irem", 0),
        113 : ("lrem", 0),
        114 : ("frem", 0),
        115 : ("drem", 0),
        116 : ("ineg", 0),
        117 : ("lneg", 0),
        118 : ("fneg", 0),
        119 : ("dneg", 0),
        120 : ("ishl", 0),
        121 : ("lshl", 0),
        122 : ("ishr", 0),
        123 : ("lshr", 0),
        124 : ("iushr", 0),
        125 : ("lushr", 0),
        126 : ("iand", 0),
        127 : ("land", 0),
        128 : ("ior", 0),
        129 : ("lor", 0),
        130 : ("ixor", 0),
        131 : ("lxor", 0),
        132 : ("iinc", 2),
        133 : ("i2l", 0),
        134 : ("i2f", 0),
        135 : ("i2d", 0),
        136 : ("l2i", 0),
        137 : ("l2f", 0),
        138 : ("l2d", 0),
        139 : ("f2i", 0),
        140 : ("f2l", 0),
        141 : ("f2d", 0),
        142 : ("d2i", 0),
        143 : ("d2l", 0),
        144 : ("d2f", 0),
        145 : ("i2b", 0),
        146 : ("i2c", 0),
        147 : ("i2s", 0),
        148 : ("lcmp", 0),
        149 : ("fcmpl", 0),
        150 : ("fcmpg", 0),
        151 : ("dcmpl", 0),
        152 : ("dcmpg", 0),
        153 : ("ifeq", 2),
        154 : ("ifne", 2),
        155 : ("iflt", 2),
        156 : ("ifge", 2),
        157 : ("ifgt", 2),
        158 : ("ifle", 2),
        159 : ("if_icmpeq", 2),
        160 : ("if_icmpne", 2),
        161 : ("if_icmplt", 2),
        162 : ("if_icmpge", 2),
        163 : ("if_icmpgt", 2),
        164 : ("if_icmple", 2),
        165 : ("if_acmpeq", 2),
        166 : ("if_acmpne", 2),
        167 : ("goto", 2),
        168 : ("jsr", 2),
        169 : ("ret", 1),
        170 : ("tableswitch", None), # variable number of arguments
        171 : ("lookupswitch", None), # variable number of arguments
        172 : ("ireturn", 0),
        173 : ("lreturn", 0),
        174 : ("freturn", 0),
        175 : ("dreturn", 0),
        176 : ("areturn", 0),
        177 : ("return_", 0),
        178 : ("getstatic", 2),
        179 : ("putstatic", 2),
        180 : ("getfield", 2),
        181 : ("putfield", 2),
        182 : ("invokevirtual", 2),
        183 : ("invokespecial", 2),
        184 : ("invokestatic", 2),
        185 : ("invokeinterface", 4),
        187 : ("new", 2),
        188 : ("newarray", 1),
        189 : ("anewarray", 2),
        190 : ("arraylength", 0),
        191 : ("athrow", 0),
        192 : ("checkcast", 2),
        193 : ("instanceof", 2),
        194 : ("monitorenter", 0),
        195 : ("monitorexit", 0),
        196 : ("wide", None), # 3 or 5 arguments, stack changes according to modified element
        197 : ("multianewarray", 3),
        198 : ("ifnull", 2),
        199 : ("ifnonnull", 2),
        200 : ("goto_w", 4),
        201 : ("jsr_w", 4),
        }

class BytecodeDisassembler(BytecodeReader):

    "A Java bytecode disassembler."

    bytecode_methods = [spec[0] for spec in BytecodeReader.java_bytecodes.values()]

    def __getattr__(self, name):
        if name in self.bytecode_methods:
            print "%5s %s" % (self.java_position, name),
            return self.generic
        else:
            raise AttributeError, name

    def generic(self, arguments, program):
        print arguments

    def lookupswitch(self, code, program):
        print "%5s lookupswitch" % (self.java_position,),
        d, r = divmod(self.java_position + 1, 4)
        to_boundary = (4 - r) % 4
        code = code[to_boundary:]
        default = classfile.s4(code[0:4])
        npairs = classfile.s4(code[4:8])
        print default, npairs
        return to_boundary + 8 + npairs * 8

    def tableswitch(self, code, program):
        print "%5s tableswitch" % (self.java_position,),
        d, r = divmod(self.java_position + 1, 4)
        to_boundary = (4 - r) % 4
        code = code[to_boundary:]
        default = classfile.s4(code[0:4])
        low = classfile.s4(code[4:8])
        high = classfile.s4(code[8:12])
        print default, low, high
        return to_boundary + 12 + (high - low + 1) * 4

class BytecodeDisassemblerProgram:
    position = 0
    def setup_except(self, target):
        print "(setup_except %s)" % target
    def setup_finally(self, target):
        print "(setup_finally %s)" % target
    def end_exception(self):
        print "(end_exception)"
    def end_exceptions(self):
        print "(end_exceptions)"
    def start_handler(self, exc_name, class_file):
        print "(start_handler %s)" % exc_name
    def pop_block(self):
        print "(pop_block)"
    def load_const(self, const):
        print "(load_const %s)" % const
    def return_value(self):
        print "(return_value)"

class BytecodeTranslator(BytecodeReader):

    "A Java bytecode translator which uses a Python bytecode writer."

    def aaload(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_subscr()

    def aastore(self, arguments, program):
        # NOTE: No type checking performed.
        # Stack: arrayref, index, value
        program.rot_three() # Stack: value, arrayref, index
        program.store_subscr()

    def aconst_null(self, arguments, program):
        program.load_const(None)

    def aload(self, arguments, program):
        program.load_fast(arguments[0])

    def aload_0(self, arguments, program):
        program.load_fast(0)

    def aload_1(self, arguments, program):
        program.load_fast(1)

    def aload_2(self, arguments, program):
        program.load_fast(2)

    def aload_3(self, arguments, program):
        program.load_fast(3)

    def anewarray(self, arguments, program):
        # NOTE: Does not raise NegativeArraySizeException.
        # NOTE: Not using the index to type the list/array.
        index = (arguments[0] << 8) + arguments[1]
        type_name = self.class_file.constants[index - 1].get_python_name()
        default_value = classfile.get_default_for_type(type_name)
        self._newarray(program, type_name)

    def _newarray(self, program, default_value):
        program.build_list(0)               # Stack: count, list
        program.rot_two()                   # Stack: list, count
        program.setup_loop()
        program.load_global("range")
        program.load_const(0)               # Stack: list, count, range, 0
        program.rot_three()                 # Stack: list, 0, count, range
        program.rot_three()                 # Stack: list, range, 0, count
        program.call_function(2)            # Stack: list, range_list
        program.get_iter()                  # Stack: list, iter
        program.for_iter()                  # Stack: list, iter, value
        program.pop_top()                   # Stack: list, iter
        program.rot_two()                   # Stack: iter, list
        program.dup_top()                   # Stack: iter, list, list
        program.load_attr("append")         # Stack: iter, list, append
        program.load_const(default_value)   # Stack: iter, list, append, default
        program.call_function(1)            # Stack: iter, list, default
        program.pop_top()                   # Stack: iter, list
        program.rot_two()                   # Stack: list, iter
        program.end_loop()                  # Back to for_iter above

    def areturn(self, arguments, program):
        program.return_value()

    def arraylength(self, arguments, program):
        program.load_global("len")  # Stack: arrayref, len
        program.rot_two()           # Stack: len, arrayref
        program.call_function(1)

    def astore(self, arguments, program):
        program.store_fast(arguments[0])

    def astore_0(self, arguments, program):
        program.store_fast(0)

    def astore_1(self, arguments, program):
        program.store_fast(1)

    def astore_2(self, arguments, program):
        program.store_fast(2)

    def astore_3(self, arguments, program):
        program.store_fast(3)

    def athrow(self, arguments, program):
        # NOTE: NullPointerException not raised where null/None is found on the stack.
        # If this instruction appears in a finally handler, use end_finally instead.
        if self.in_finally:
            program.end_finally()
        else:
            # Wrap the exception in a Python exception.
            program.load_global("Exception")    # Stack: objectref, Exception
            program.rot_two()                   # Stack: Exception, objectref
            program.call_function(1)            # Stack: exception
            program.raise_varargs(1)
            # NOTE: This seems to put another object on the stack.

    baload = aaload
    bastore = aastore

    def bipush(self, arguments, program):
        program.load_const(signed1(arguments[0]))

    caload = aaload
    castore = aastore

    def checkcast(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.use_external_name(target_name)
        program.dup_top()                   # Stack: objectref, objectref
        program.load_const(None)            # Stack: objectref, objectref, None
        program.compare_op("is")            # Stack: objectref, result
        program.jump_to_label(1, "next")
        program.pop_top()                   # Stack: objectref
        program.dup_top()                   # Stack: objectref, objectref
        program.load_global("isinstance")   # Stack: objectref, objectref, isinstance
        program.rot_two()                   # Stack: objectref, isinstance, objectref
        load_class_name(self.class_file, target_name, program)
        program.call_function(2)            # Stack: objectref, result
        program.jump_to_label(1, "next")
        program.pop_top()                   # Stack: objectref
        program.pop_top()                   # Stack:
        program.use_external_name("java.lang.ClassCastException")
        load_class_name(self.class_file, "java.lang.ClassCastException", program)
        program.call_function(0)            # Stack: exception
        # Wrap the exception in a Python exception.
        program.load_global("Exception")    # Stack: exception, Exception
        program.rot_two()                   # Stack: Exception, exception
        program.call_function(1)            # Stack: exception
        program.raise_varargs(1)
        # NOTE: This seems to put another object on the stack.
        program.start_label("next")
        program.pop_top()                   # Stack: objectref

    def d2f(self, arguments, program):
        pass

    def d2i(self, arguments, program):
        program.load_global("int")  # Stack: value, int
        program.rot_two()           # Stack: int, value
        program.call_function(1)    # Stack: result

    d2l = d2i # Preserving Java semantics

    def dadd(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_add()

    daload = aaload
    dastore = aastore

    def dcmpg(self, arguments, program):
        # NOTE: No type checking performed.
        program.compare_op(">")

    def dcmpl(self, arguments, program):
        # NOTE: No type checking performed.
        program.compare_op("<")

    def dconst_0(self, arguments, program):
        program.load_const(0.0)

    def dconst_1(self, arguments, program):
        program.load_const(1.0)

    def ddiv(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_divide()

    dload = aload
    dload_0 = aload_0
    dload_1 = aload_1
    dload_2 = aload_2
    dload_3 = aload_3

    def dmul(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_multiply()

    def dneg(self, arguments, program):
        # NOTE: No type checking performed.
        program.unary_negative()

    def drem(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_modulo()

    dreturn = areturn
    dstore = astore
    dstore_0 = astore_0
    dstore_1 = astore_1
    dstore_2 = astore_2
    dstore_3 = astore_3

    def dsub(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_subtract()

    def dup(self, arguments, program):
        program.dup_top()

    def dup_x1(self, arguments, program):
        # Ignoring computational type categories.
        program.dup_top()
        program.rot_three()

    def dup_x2(self, arguments, program):
        # Ignoring computational type categories.
        program.dup_top()
        program.rot_four()

    dup2 = dup # Ignoring computational type categories
    dup2_x1 = dup_x1 # Ignoring computational type categories
    dup2_x2 = dup_x2 # Ignoring computational type categories

    def f2d(self, arguments, program):
        pass # Preserving Java semantics

    def f2i(self, arguments, program):
        program.load_global("int")  # Stack: value, int
        program.rot_two()           # Stack: int, value
        program.call_function(1)    # Stack: result

    f2l = f2i # Preserving Java semantics
    fadd = dadd
    faload = daload
    fastore = dastore
    fcmpg = dcmpg
    fcmpl = dcmpl
    fconst_0 = dconst_0
    fconst_1 = dconst_1

    def fconst_2(self, arguments, program):
        program.load_const(2.0)

    fdiv = ddiv
    fload = dload
    fload_0 = dload_0
    fload_1 = dload_1
    fload_2 = dload_2
    fload_3 = dload_3
    fmul = dmul
    fneg = dneg
    frem = drem
    freturn = dreturn
    fstore = dstore
    fstore_0 = dstore_0
    fstore_1 = dstore_1
    fstore_2 = dstore_2
    fstore_3 = dstore_3
    fsub = dsub

    def getfield(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name))

    def getstatic(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()

        # Get the class name instead of the fully qualified name.

        full_class_name = target.get_class().get_python_name()
        program.use_external_name(full_class_name)
        load_class_name(self.class_file, full_class_name, program)
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name))

    def goto(self, arguments, program):
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        program.jump_absolute(self.position_mapping[java_absolute])

    def goto_w(self, arguments, program):
        offset = signed4((arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3])
        java_absolute = self.java_position + offset
        program.jump_absolute(self.position_mapping[java_absolute])

    def i2b(self, arguments, program):
        pass

    def i2c(self, arguments, program):
        pass

    def i2d(self, arguments, program):
        program.load_global("float")    # Stack: value, float
        program.rot_two()               # Stack: float, value
        program.call_function(1)        # Stack: result

    i2f = i2d # Not distinguishing between float and double

    def i2l(self, arguments, program):
        pass # Preserving Java semantics

    def i2s(self, arguments, program):
        pass # Not distinguishing between int and short

    iadd = fadd
    iaload = faload

    def iand(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_and()

    iastore = fastore

    def iconst_m1(self, arguments, program):
        program.load_const(-1)

    def iconst_0(self, arguments, program):
        program.load_const(0)

    def iconst_1(self, arguments, program):
        program.load_const(1)

    def iconst_2(self, arguments, program):
        program.load_const(2)

    def iconst_3(self, arguments, program):
        program.load_const(3)

    def iconst_4(self, arguments, program):
        program.load_const(4)

    def iconst_5(self, arguments, program):
        program.load_const(5)

    idiv = fdiv

    def _if_xcmpx(self, arguments, program, op):
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        program.compare_op(op)
        program.jump_to_label(0, "next") # skip if false
        program.pop_top()
        program.jump_absolute(self.position_mapping[java_absolute])
        program.start_label("next")
        program.pop_top()

    def if_acmpeq(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "is")

    def if_acmpne(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "is not")

    def if_icmpeq(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "==")

    def if_icmpne(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "!=")

    def if_icmplt(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "<")

    def if_icmpge(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, ">=")

    def if_icmpgt(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, ">")

    def if_icmple(self, arguments, program):
        # NOTE: No type checking performed.
        self._if_xcmpx(arguments, program, "<=")

    def ifeq(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "==")

    def ifne(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "!=")

    def iflt(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "<")

    def ifge(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, ">=")

    def ifgt(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, ">")

    def ifle(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(0)
        self._if_xcmpx(arguments, program, "<=")

    def ifnonnull(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(None)
        self._if_xcmpx(arguments, program, "is not")

    def ifnull(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_const(None)
        self._if_xcmpx(arguments, program, "is")

    def iinc(self, arguments, program):
        # NOTE: No type checking performed.
        program.load_fast(arguments[0])
        program.load_const(arguments[1])
        program.binary_add()
        program.store_fast(arguments[0])

    iload = fload
    iload_0 = fload_0
    iload_1 = fload_1
    iload_2 = fload_2
    iload_3 = fload_3
    imul = fmul
    ineg = fneg

    def instanceof(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.use_external_name(target_name)
        program.load_global("isinstance")   # Stack: objectref, isinstance
        program.rot_two()                   # Stack: isinstance, objectref
        load_class_name(self.class_file, target_name, program)
        program.call_function(2)            # Stack: result

    def _invoke(self, target_name, program):
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_attr(str(target_name)) # Stack: tuple, method
        program.rot_two()                   # Stack: method, tuple
        program.call_function_var(0)        # Stack: result

    def invokeinterface(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        # NOTE: "count" == nargs + 1, apparently.
        count = arguments[2] - 1
        target_name = self.class_file.constants[index - 1].get_python_name()
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        program.rot_two()                   # Stack: tuple, objectref
        # NOTE: The interface information is not used to discover the correct
        # NOTE: method.
        self._invoke(target_name, program)

    def invokespecial(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        original_name = target.get_name()
        target_name = target.get_python_name()

        # Get the number of parameters from the descriptor.

        count = len(target.get_descriptor()[0])

        # First, we build a tuple of the reference and arguments.

        program.build_tuple(count + 1)          # Stack: tuple

        # Get the class name instead of the fully qualified name.
        # NOTE: Not bothering with Object initialisation.

        full_class_name = target.get_class().get_python_name()
        if full_class_name not in ("java.lang.Object", "java.lang.Exception"):
            program.use_external_name(full_class_name)
            load_class_name(self.class_file, full_class_name, program)
            self._invoke(target_name, program)

        # Remove Python None return value.

        if str(original_name) == "<init>":
            program.pop_top()

    def invokestatic(self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()

        # Get the number of parameters from the descriptor.

        count = len(target.get_descriptor()[0])

        # Stack: arg1, arg2, ...

        program.build_tuple(count)              # Stack: tuple

        # Use the class to provide access to static methods.
        # Get the class name instead of the fully qualified name.

        full_class_name = target.get_class().get_python_name()
        if full_class_name not in ("java.lang.Object", "java.lang.Exception"):
            program.use_external_name(full_class_name)
            load_class_name(self.class_file, full_class_name, program)
            self._invoke(target_name, program)

    def invokevirtual (self, arguments, program):
        # NOTE: This implementation does not perform the necessary checks for
        # NOTE: signature-based polymorphism.
        # NOTE: Java rules not specifically obeyed.
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()
        # Get the number of parameters from the descriptor.
        count = len(target.get_descriptor()[0])
        # Stack: objectref, arg1, arg2, ...
        program.build_tuple(count)          # Stack: objectref, tuple
        program.rot_two()                   # Stack: tuple, objectref
        self._invoke(target_name, program)

    def ior(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_or()

    irem = frem
    ireturn = freturn

    def ishl(self, arguments, program):
        # NOTE: No type checking performed.
        # NOTE: Not verified.
        program.binary_lshift()

    def ishr(self, arguments, program):
        # NOTE: No type checking performed.
        # NOTE: Not verified.
        program.binary_rshift()

    istore = fstore
    istore_0 = fstore_0
    istore_1 = fstore_1
    istore_2 = fstore_2
    istore_3 = fstore_3
    isub = fsub
    iushr = ishr # Ignoring distinctions between arithmetic and logical shifts

    def ixor(self, arguments, program):
        # NOTE: No type checking performed.
        program.binary_xor()

    def jsr(self, arguments, program):
        offset = signed2((arguments[0] << 8) + arguments[1])
        java_absolute = self.java_position + offset
        # Store the address of the next instruction.
        program.load_const_ret(self.position_mapping[self.java_position + 3])
        program.jump_absolute(self.position_mapping[java_absolute])

    def jsr_w(self, arguments, program):
        offset = signed4((arguments[0] << 24) + (arguments[1] << 16) + (arguments[2] << 8) + arguments[3])
        java_absolute = self.java_position + offset
        # Store the address of the next instruction.
        program.load_const_ret(self.position_mapping[self.java_position + 5])
        program.jump_absolute(self.position_mapping[java_absolute])

    l2d = i2d
    l2f = i2f

    def l2i(self, arguments, program):
        pass # Preserving Java semantics

    ladd = iadd
    laload = iaload
    land = iand
    lastore = iastore

    def lcmp(self, arguments, program):
        # NOTE: No type checking performed.
        program.dup_topx(2)                 # Stack: value1, value2, value1, value2
        program.compare_op(">")             # Stack: value1, value2, result
        program.jump_to_label(0, "equals")
        # True - produce result and branch.
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(1)               # Stack: 1
        program.jump_to_label(None, "next")
        # False - test equality.
        program.start_label("equals")
        program.pop_top()                   # Stack: value1, value2
        program.dup_topx(2)                 # Stack: value1, value2, value1, value2
        program.compare_op("==")            # Stack: value1, value2, result
        program.jump_to_label(0, "less")
        # True - produce result and branch.
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(0)               # Stack: 0
        program.jump_to_label(None, "next")
        # False - produce result.
        program.start_label("less")
        program.pop_top()                   # Stack: value1, value2
        program.pop_top()                   # Stack: value1
        program.pop_top()                   # Stack:
        program.load_const(-1)              # Stack: -1
        program.start_label("next")

    lconst_0 = iconst_0
    lconst_1 = iconst_1

    def ldc(self, arguments, program):
        const = self.class_file.constants[arguments[0] - 1]
        if isinstance(const, classfile.StringInfo):
            program.use_external_name("java.lang.String")
            program.load_global("java")
            program.load_attr("lang")
            program.load_attr("String")
            program.load_const(const.get_value())
            program.call_function(1)
        else:
            program.load_const(const.get_value())

    def ldc_w(self, arguments, program):
        const = self.class_file.constants[(arguments[0] << 8) + arguments[1] - 1]
        if isinstance(const, classfile.StringInfo):
            program.use_external_name("java.lang.String")
            program.load_global("java")
            program.load_attr("lang")
            program.load_attr("String")
            program.load_const(const.get_value())
            program.call_function(1)
        else:
            program.load_const(const.get_value())

    ldc2_w = ldc_w
    ldiv = idiv
    lload = iload
    lload_0 = iload_0
    lload_1 = iload_1
    lload_2 = iload_2
    lload_3 = iload_3
    lmul = imul
    lneg = ineg

    def lookupswitch(self, code, program):

        # Find the offset to the next 4 byte boundary in the code.

        d, r = divmod(self.java_position + 1, 4)
        to_boundary = (4 - r) % 4

        # Get the pertinent arguments.

        code = code[to_boundary:]
        default = classfile.s4(code[0:4])
        npairs = classfile.s4(code[4:8])

        # Process the pairs.
        # NOTE: This is not the most optimal implementation.

        pair_index = 8
        for pair in range(0, npairs):
            match = classfile.u4(code[pair_index:pair_index+4])
            offset = classfile.s4(code[pair_index+4:pair_index+8])
            # Calculate the branch target.
            java_absolute = self.java_position + offset
            # Generate branching code.
            program.dup_top()                                           # Stack: key, key
            program.load_const(match)                                   # Stack: key, key, match
            program.compare_op("==")                                    # Stack: key, result
            program.jump_to_label(0, "end")
            program.pop_top()                                           # Stack: key
            program.pop_top()                                           # Stack:
            program.jump_absolute(self.position_mapping[java_absolute])
            # Generate the label for the end of the branching code.
            program.start_label("end")
            program.pop_top()                                           # Stack: key
            # Update the index.
            pair_index += 8

        # Generate the default.

        java_absolute = self.java_position + default
        program.jump_absolute(self.position_mapping[java_absolute])
        return pair_index + to_boundary

    lor = ior
    lrem = irem
    lreturn = ireturn
    lshl = ishl
    lshr = ishr
    lstore = istore
    lstore_0 = istore_0
    lstore_1 = istore_1
    lstore_2 = istore_2
    lstore_3 = istore_3
    lsub = isub
    lushr = iushr
    lxor = ixor

    def monitorenter(self, arguments, program):
        # NOTE: To be implemented.
        pass

    def monitorexit(self, arguments, program):
        # NOTE: To be implemented.
        pass

    def multianewarray(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        dimensions = arguments[2]
        # Stack: count1, ..., countN-1, countN
        type_name = self.class_file.constants[index - 1].get_python_name()
        default_value = classfile.get_default_for_type(type_name)
        self._newarray(program, default_value)  # Stack: count1, ..., countN-1, list
        for dimension in range(1, dimensions):
            program.rot_two()               # Stack: count1, ..., list, countN-1
            program.build_list(0)           # Stack: count1, ..., list, countN-1, new-list
            program.rot_three()             # Stack: count1, ..., new-list, list, countN-1
            program.setup_loop()
            program.load_const(0)           # Stack: count1, ..., new-list, list, countN-1, 0
            program.rot_two()               # Stack: count1, ..., new-list, list, 0, countN-1
            program.load_global("range")    # Stack: count1, ..., new-list, list, 0, countN-1, range
            program.rot_three()             # Stack: count1, ..., new-list, list, range, 0, countN-1
            program.call_function(2)        # Stack: count1, ..., new-list, list, range-list
            program.get_iter()              # Stack: count1, ..., new-list, list, iter
            program.for_iter()              # Stack: count1, ..., new-list, list, iter, value
            program.pop_top()               # Stack: count1, ..., new-list, list, iter
            program.rot_three()             # Stack: count1, ..., iter, new-list, list
            program.slice_0()               # Stack: count1, ..., iter, new-list, list[:]
            program.dup_top()               # Stack: count1, ..., iter, new-list, list[:], list[:]
            program.rot_three()             # Stack: count1, ..., iter, list[:], new-list, list[:]
            program.rot_two()               # Stack: count1, ..., iter, list[:], list[:], new-list
            program.dup_top()               # Stack: count1, ..., iter, list[:], list[:], new-list, new-list
            program.load_attr("append")     # Stack: count1, ..., iter, list[:], list[:], new-list, append
            program.rot_three()             # Stack: count1, ..., iter, list[:], append, list[:], new-list
            program.rot_three()             # Stack: count1, ..., iter, list[:], new-list, append, list[:]
            program.call_function(1)        # Stack: count1, ..., iter, list[:], new-list, None
            program.pop_top()               # Stack: count1, ..., iter, list[:], new-list
            program.rot_two()               # Stack: count1, ..., iter, new-list, list[:]
            program.rot_three()             # Stack: count1, ..., list[:], iter, new-list
            program.rot_three()             # Stack: count1, ..., new-list, list[:], iter
            program.end_loop()              # Stack: count1, ..., new-list, list[:], iter
            program.pop_top()               # Stack: count1, ..., new-list

    def new(self, arguments, program):
        # This operation is considered to be the same as the calling of the
        # initialisation method of the given class with no arguments.

        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.use_external_name(target_name)

        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.load_global("object")
        program.load_attr("__new__")
        load_class_name(self.class_file, target_name, program)
        program.call_function(1)

    def newarray(self, arguments, program):
        # NOTE: Does not raise NegativeArraySizeException.
        # NOTE: Not completely using the arguments to type the list/array.
        atype = arguments[0]
        default_value = get_default_for_atype(atype)
        self._newarray(program, default_value)

    def nop(self, arguments, program):
        pass

    def pop(self, arguments, program):
        program.pop_top()

    pop2 = pop # ignoring Java stack value distinctions

    def putfield(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target_name = self.class_file.constants[index - 1].get_python_name()
        program.rot_two()
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.store_attr(str(target_name))

    def putstatic(self, arguments, program):
        index = (arguments[0] << 8) + arguments[1]
        target = self.class_file.constants[index - 1]
        target_name = target.get_python_name()

        # Get the class name instead of the fully qualified name.

        full_class_name = target.get_class().get_python_name()
        program.use_external_name(full_class_name)
        load_class_name(self.class_file, full_class_name, program)
        # NOTE: Using the string version of the name which may contain incompatible characters.
        program.store_attr(str(target_name))

    def ret(self, arguments, program):
        program.ret(arguments[0])
        # Indicate that the finally handler is probably over.
        # NOTE: This is seemingly not guaranteed.
        self.in_finally = 0

    def return_(self, arguments, program):
        program.load_const(None)
        program.return_value()

    saload = laload
    sastore = lastore

    def sipush(self, arguments, program):
        program.load_const(signed2((arguments[0] << 8) + arguments[1]))

    def swap(self, arguments, program):
        program.rot_two()

    def tableswitch(self, code, program):

        # Find the offset to the next 4 byte boundary in the code.

        d, r = divmod(self.java_position + 1, 4)
        to_boundary = (4 - r) % 4

        # Get the pertinent arguments.

        code = code[to_boundary:]
        default = classfile.s4(code[0:4])
        low = classfile.s4(code[4:8])
        high = classfile.s4(code[8:12])

        # Process the jump entries.
        # NOTE: This is not the most optimal implementation.

        jump_index = 12
        for jump in range(low, high + 1):
            offset = classfile.s4(code[jump_index:jump_index + 4])

            # Calculate the branch target.

            java_absolute = self.java_position + offset

            # Generate branching code.

            program.dup_top()                                           # Stack: key, key
            program.load_const(jump)                                    # Stack: key, key, jump
            program.compare_op("==")                                    # Stack: key, result
            program.jump_to_label(0, "end")
            program.pop_top()                                           # Stack: key
            program.pop_top()                                           # Stack:
            program.jump_absolute(self.position_mapping[java_absolute])

            # Generate the label for the end of the branching code.

            program.start_label("end")
            program.pop_top()                                           # Stack: key

            # Update the index.

            jump_index += 4

        # Generate the default.

        java_absolute = self.java_position + default
        program.jump_absolute(self.position_mapping[java_absolute])
        return jump_index + to_boundary

    def wide(self, code, program):
        # NOTE: To be implemented.
        raise NotImplementedError, "wide"

def disassemble(class_file, method):
    disassembler = BytecodeDisassembler(class_file)
    disassembler.process(method, BytecodeDisassemblerProgram())
    return disassembler

class ClassTranslator:

    """
    A class which provides a wrapper around a class file and the means to
    translate the represented class into a Python class.
    """

    def __init__(self, class_file):

        "Initialise the object with the given 'class_file'."

        self.class_file = class_file
        self.filename = ""

        for attribute in self.class_file.attributes:
            if isinstance(attribute, classfile.SourceFileAttributeInfo):
                self.filename = str(attribute.get_name())

    def translate_method(self, method):

        "Translate the given 'method' - an object obtained from the class file."

        translator = BytecodeTranslator(self.class_file)
        writer = BytecodeWriter()
        try:
            translator.process(method, writer)
        except:
            print "Translation error in", str(self.class_file.this_class.get_name()), str(method.get_name())
            disassemble(self.class_file, method)
            raise
        return translator, writer

    def make_method(self, real_method_name, methods, global_names):

        """
        Make a dispatcher method with the given 'real_method_name', providing
        dispatch to the supplied type-sensitive 'methods', accessing the given
        'global_names' where necessary, and storing the new method in the
        class's namespace.
        """

        if real_method_name == "<init>":
            method_name = "__init__"
        else:
            method_name = real_method_name

        # Where only one method exists, just make an alias.

        if len(methods) == 1:
            method, fn = methods[0]
            self.namespace[method_name] = fn
            return

        # Write a simple bytecode dispatching mechanism.

        program = BytecodeWriter()

        # Remember whether any of the methods are static.
        # NOTE: This should be an all or nothing situation.

        method_is_static = 0

        # NOTE: The code below should use dictionary-based dispatch for better performance.

        for method, fn in methods:
            method_is_static = real_method_name != "<init>" and method_is_static or \
                classfile.has_flags(method.access_flags, [classfile.STATIC])

            if method_is_static:
                program.load_fast(0)                # Stack: arguments
            else:
                program.load_fast(1)                # Stack: arguments

            program.setup_loop()
            program.load_const(1)                   # Stack: arguments, 1

            if method_is_static:
                program.store_fast(1)               # Stack: arguments (found = 1)
            else:
                program.store_fast(2)               # Stack: arguments (found = 1)

            # Emit a list of parameter types.

            descriptor_types = method.get_descriptor()[0]
            for descriptor_type in descriptor_types:
                base_type, object_type, array_type = descriptor_type
                python_type = classfile.descriptor_base_type_mapping[base_type]
                if python_type == "instance":
                    # NOTE: This will need extending.
                    python_type = object_type
                program.load_global(python_type)    # Stack: arguments, type, ...
            program.build_list(len(descriptor_types))
                                                    # Stack: arguments, types
            # Make a map of arguments and types.
            program.load_const(None)                # Stack: arguments, types, None
            program.rot_three()                     # Stack: None, arguments, types
            program.build_tuple(3)                  # Stack: tuple
            program.load_global("map")              # Stack: tuple, map
            program.rot_two()                       # Stack: map, tuple
            program.call_function_var(0)            # Stack: list (mapping arguments to types)
            # Loop over each pair.
            program.get_iter()                      # Stack: iter
            program.for_iter()                      # Stack: iter, (argument, type)
            program.unpack_sequence(2)              # Stack: iter, type, argument
            program.dup_top()                       # Stack: iter, type, argument, argument
            program.load_const(None)                # Stack: iter, type, argument, argument, None
            program.compare_op("is")                # Stack: iter, type, argument, result
            # Missing argument?
            program.jump_to_label(0, "present")
            program.pop_top()                       # Stack: iter, type, argument
            program.pop_top()                       # Stack: iter, type
            program.pop_top()                       # Stack: iter
            program.load_const(0)                   # Stack: iter, 0

            if method_is_static:
                program.store_fast(1)               # Stack: iter (found = 0)
            else:
                program.store_fast(2)               # Stack: iter (found = 0)

            program.break_loop()
            # Argument was present.
            program.start_label("present")
            program.pop_top()                       # Stack: iter, type, argument
            program.rot_two()                       # Stack: iter, argument, type
            program.dup_top()                       # Stack: iter, argument, type, type
            program.load_const(None)                # Stack: iter, argument, type, type, None
            program.compare_op("is")                # Stack: iter, argument, type, result
            # Missing parameter type?
            program.jump_to_label(0, "present")
            program.pop_top()                       # Stack: iter, argument, type
            program.pop_top()                       # Stack: iter, argument
            program.pop_top()                       # Stack: iter
            program.load_const(0)                   # Stack: iter, 0

            if method_is_static:
                program.store_fast(1)               # Stack: iter (found = 0)
            else:
                program.store_fast(2)               # Stack: iter (found = 0)

            program.break_loop()
            # Parameter was present.
            program.start_label("present")
            program.pop_top()                       # Stack: iter, argument, type
            program.build_tuple(2)                  # Stack: iter, (argument, type)
            program.load_global("isinstance")       # Stack: iter, (argument, type), isinstance
            program.rot_two()                       # Stack: iter, isinstance, (argument, type)
            program.call_function_var(0)            # Stack: iter, result
            program.jump_to_label(1, "match")
            program.pop_top()                       # Stack: iter
            program.load_const(0)                   # Stack: iter, 0

            if method_is_static:
                program.store_fast(1)               # Stack: iter (found = 0)
            else:
                program.store_fast(2)               # Stack: iter (found = 0)

            program.break_loop()
            # Argument type and parameter type matched.
            program.start_label("match")
            program.pop_top()                       # Stack: iter
            program.end_loop()                      # Stack:
            # If all the parameters matched, call the method.

            if method_is_static:
                program.load_fast(1)                # Stack: match
            else:
                program.load_fast(2)                # Stack: match

            program.jump_to_label(0, "failed")
            # All the parameters matched.
            program.pop_top()                       # Stack:

            if method_is_static:
                program.load_fast(0)                # Stack: arguments
                program.load_global(str(self.class_file.this_class.get_python_name()))
                                                    # Stack: arguments, class
            else:
                program.load_fast(1)                # Stack: arguments
                program.load_fast(0)                # Stack: arguments, self

            program.load_attr(str(method.get_python_name()))
                                                    # Stack: arguments, method
            program.rot_two()                       # Stack: method, arguments
            program.call_function_var(0)            # Stack: result
            program.return_value()
            # Try the next method if arguments or parameters were missing or incorrect.
            program.start_label("failed")
            program.pop_top()                       # Stack:

        # Raise an exception if nothing matched.
        # NOTE: Improve this.

        program.load_const("No matching method")
        program.raise_varargs(1)
        program.load_const(None)
        program.return_value()

        # Add the code as a method in the namespace.
        # NOTE: One actual parameter, flags as 71 apparently means that a list
        # NOTE: parameter is used in a method.

        if method_is_static:
            nargs = 0
        else:
            nargs = 1
        nlocals = program.max_locals + 1

        code = new.code(nargs, nlocals, program.max_stack_depth, 71, program.get_output(),
            tuple(program.get_constants()), tuple(program.get_names()), tuple(self.make_varnames(nlocals, method_is_static)),
            self.filename, method_name, 0, "")
        fn = new.function(code, global_names)

        if method_is_static:
            fn = staticmethod(fn)

        self.namespace[method_name] = fn

    def process(self, global_names):

        """
        Process the class, storing it in the 'global_names' dictionary provided.
        Return a list of external names referenced by the class's methods.
        """

        self.namespace = {}

        # Make the fields.

        for field in self.class_file.fields:
            if classfile.has_flags(field.access_flags, [classfile.STATIC]):
                field_name = str(field.get_python_name())
                self.namespace[field_name] = None

        # Make the methods.

        self.real_methods = {}
        external_names = []

        for method in self.class_file.methods:
            real_method_name = str(method.get_name())
            method_name = str(method.get_python_name())
            translator, writer = self.translate_method(method)

            # Add external names to the master list.

            for external_name in writer.external_names:
                if external_name not in external_names:
                    external_names.append(external_name)

            # Fix up special class initialisation methods and static methods.

            method_is_static = real_method_name != "<init>" and classfile.has_flags(method.access_flags, [classfile.STATIC])
            if method_is_static:
                nargs = len(method.get_descriptor()[0])
            else:
                nargs = len(method.get_descriptor()[0]) + 1
            nlocals = writer.max_locals + 1
            flags = 67

            # NOTE: Add line number table later.

            code = new.code(nargs, nlocals, writer.max_stack_depth, flags, writer.get_output(),
                tuple(writer.get_constants()), tuple(writer.get_names()),
                tuple(self.make_varnames(nlocals, method_is_static)), self.filename, method_name, 0, "")

            # NOTE: May need more globals.

            fn = new.function(code, global_names)

            # Fix up special class initialisation methods and static methods.

            if method_is_static:
                fn = staticmethod(fn)

            # Remember the real method name and the corresponding methods produced.

            if not self.real_methods.has_key(real_method_name):
                self.real_methods[real_method_name] = []
            self.real_methods[real_method_name].append((method, fn))

            # Add the method to the class's namespace.

            self.namespace[method_name] = fn

        # Add the base classes as external names, if appropriate.

        external_names += [class_.get_python_name() for class_ in self.get_base_class_references()]

        return external_names

    def get_class(self, global_names, classes):

        """
        Get the Python class representing the underlying Java class, using the
        given 'global_names' to define dispatcher methods.
        """

        # Define superclasses.

        bases = self.get_base_classes(classes)

        # Define method dispatchers.

        for real_method_name, methods in self.real_methods.items():
            if real_method_name != "<clinit>":
                self.make_method(real_method_name, methods, global_names)

        # Use only the last part of the fully qualified name.

        full_class_name = str(self.class_file.this_class.get_python_name())
        class_name = full_class_name.split(".")[-1]
        cls = new.classobj(class_name, bases, self.namespace)
        global_names[cls.__name__] = cls

        return cls

    def get_base_class_references(self):
        class_names = []
        if self.class_file.super_class is not None:
            class_names.append(self.class_file.super_class)
        class_names += self.class_file.interfaces
        return class_names

    def get_base_classes(self, classes):

        """
        Identify the superclass, obtaining it from the given 'classes'
        dictionary. Return a tuple containing all base classes (usually a single
        element tuple).
        """

        base_classes = []

        for class_ in self.get_base_class_references():
            base_classes.append(self._get_class(class_, classes))

        return tuple(base_classes)

    def _get_class(self, class_, classes):
        class_name = str(class_.get_name())
        try:
            return classes[class_name]
        except KeyError:
            raise AttributeError, "Cannot find Java class '%s'" % class_name

    def make_varnames(self, nlocals, method_is_static=0):

        """
        A utility method which invents variable names for the given number -
        'nlocals' - of local variables in a method. Returns a list of such
        variable names.

        If the optional 'method_is_static' is set to true, do not use "self" as
        the first argument name.
        """

        if method_is_static:
            l = ["cls"]
        else:
            l = ["self"]
        for i in range(1, nlocals):
            l.append("_l%s" % i)
        return l[:nlocals]

# Test functions, useful for tracing generated bytecode operations.

def _map(*args):
    print args
    return apply(__builtins__.map, args)

def _isinstance(*args):
    print args
    return apply(__builtins__.isinstance, args)

if __name__ == "__main__":
    import sys
    import dis
    import java.lang
    global_names = globals()
    #global_names["isinstance"] = _isinstance
    #global_names["map"] = _map
    for filename in sys.argv[1:]:
        f = open(filename, "rb")
        c = classfile.ClassFile(f.read())
        translator = ClassTranslator(c)
        external_names = translator.process(global_names)
        cls = translator.get_class(global_names)

# vim: tabstop=4 expandtab shiftwidth=4
