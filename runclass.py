#!/usr/bin/env python

"""
A program to run Java class files.

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

import javaclass.classhook
import java.lang

# NOTE: Simple __this__ package loader to potentially avoid repeated import
# NOTE: issues exposed by test.py.

def load_classes(class_names):

    "Load the classes with the given 'class_names'."

    module = __import__("__this__", globals(), locals(), class_names)
    objs = []
    for class_name in class_names:
        objs.append(getattr(module, class_name))
    return objs

# The more general class loader.

def load_class(class_name):

    "Load the class with the given 'class_name'."

    class_name_parts = class_name.split(".")
    if len(class_name_parts) == 1:
        module = __import__("__this__", globals(), locals(), [class_name])
        obj = getattr(module, class_name)
    else:
        class_module = ".".join(class_name_parts[:-1])
        obj = __import__(class_module, globals(), locals())
        for part in class_name_parts[1:]:
            obj = getattr(obj, part)

    return obj

def run_class(cls, args):
    cls.main([java.lang.String(arg) for arg in args])

if __name__ == "__main__":
    import sys
    cls = load_class(sys.argv[1])
    run_class(cls, sys.argv[2:])

# vim: tabstop=4 expandtab shiftwidth=4
