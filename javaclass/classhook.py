#!/usr/bin/env python

"""
An import hook for class files.

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

import ihooks # for the import machinery
import os, glob # for getting suitably-named files
from imp import PY_SOURCE, PKG_DIRECTORY, C_BUILTIN # import machinery magic
import classfile, bytecode # Java class support
import zipfile # for Java archive inspection
import sys

# NOTE: Arbitrary constants pulled from thin air.

JAVA_PACKAGE = 20041113
JAVA_CLASS = 20041114
JAVA_ARCHIVE = 20041115

class ClassHooks(ihooks.Hooks):

    "A filesystem hooks class providing information about supported files."

    def get_suffixes(self):

        "Return the recognised suffixes."

        return [("", "r", JAVA_PACKAGE), (os.extsep + "jar", "r", JAVA_ARCHIVE)] + ihooks.Hooks.get_suffixes(self)

    def path_isdir(self, x, archive=None):

        "Return whether 'x' is a directory in the given 'archive'."

        if archive is None:
            return ihooks.Hooks.path_isdir(self, x)

        return self._get_dirname(x) in archive.namelist()

    def _get_dirname(self, x):

        """
        Return the directory name for 'x'.
        In zip files, the presence of "/" seems to indicate a directory.
        """

        if x.endswith("/"):
            return x
        else:
            return x + "/"

    def listdir(self, x, archive=None):

        "Return the contents of the directory 'x' in the given 'archive'."

        if archive is None:
            return ihooks.Hooks.listdir(self, x)

        x = self._get_dirname(x)
        l = []
        for path in archive.namelist():

            # Find out if the path is within the given directory.

            if path != x and path.startswith(x):

                # Get the path below the given directory.

                subpath = path[len(x):]

                # Find out whether the path is an object in the current directory.

                if subpath.count("/") == 0 or subpath.count("/") == 1 and subpath.endswith("/"):
                    l.append(subpath)

        return l

    def matching(self, dir, extension, archive=None):

        """
        Return the matching files in the given directory 'dir' having the given
        'extension' within the given 'archive'. Produce a list containing full
        paths as opposed to simple filenames.
        """

        if archive is None:
            return glob.glob(self.path_join(dir, "*" + extension))

        dir = self._get_dirname(dir)
        l = []
        for path in self.listdir(dir, archive):
            if path.endswith(extension):
                l.append(self.path_join(dir, path))
        return l

    def read(self, filename, archive=None):

        """
        Return the contents of the file with the given 'filename' in the given
        'archive'.
        """

        if archive is None:
            f = open(filename, "rb")
            s = f.read()
            f.close()
            return s
        return archive.read(filename)

class ClassLoader(ihooks.ModuleLoader):

    "A class providing support for searching directories for supported files."

    def find_module(self, name, path=None):

        """
        Find the module with the given 'name', using the given 'path' to locate
        it. Note that ModuleLoader.find_module is almost sufficient, but does
        not provide enough support for "package unions" where the root of a
        package hierarchy may appear in several places.

        Return a list of locations (each being the "stuff" data structure used
        by load_module); this replaces the single "stuff" value or None returned
        by ModuleLoader.find_module.
        """

        if path is None:
            path = [None] + self.default_path()

        found_locations = []

        for dir in path:
            stuff = self.find_module_in_dir(name, dir)
            if stuff:
                found_locations.append(stuff)

        return found_locations

    def find_module_in_dir(self, name, dir, allow_packages=1):

        """
        Find the module with the given 'name' in the given directory 'dir'.
        Since Java packages/modules are directories containing class files,
        return the required information tuple only when the path constructed
        from 'dir' and 'name' refers to a directory containing class files.
        """

        result = ihooks.ModuleLoader.find_module_in_dir(self, name, dir, allow_packages)
        if result is not None:
            return result

        # An archive may be opened.

        archive = None

        # Provide a special name for the current directory.

        if name == "__this__":
            if dir == None:
                return (None, ".", ("", "", JAVA_PACKAGE))
            else:
                return None

        # Where no directory is given, return failure immediately.

        elif dir is None:
            return None

        # Detect archives.

        else:
            archive, archive_path, path = self._get_archive_and_path(dir, name)


        if self._find_module_at_path(path, archive):
            if archive is not None:
                return (archive, archive_path + ":" + path, (os.extsep + "jar", "r", JAVA_ARCHIVE))
            else:
                return (None, path, ("", "", JAVA_PACKAGE))
        else:
            return None

    def _get_archive_and_path(self, dir, name):
        parts = dir.split(":")
        archive_path = parts[0]

        # Archives may include an internal path, but will in any case have
        # a primary part ending in .jar.

        if archive_path.endswith(os.extsep + "jar"):
            archive = zipfile.ZipFile(archive_path, "r")
            path = self.hooks.path_join(":".join(parts[1:]), name)

        # Otherwise, produce a filesystem-based path.

        else:
            archive = None
            path = self.hooks.path_join(dir, name)

        return archive, archive_path, path

    def _get_path_in_archive(self, path):
        parts = path.split(":")
        if len(parts) == 1:
            return parts[0]
        else:
            return ":".join(parts[1:])

    def _find_module_at_path(self, path, archive):
        if self.hooks.path_isdir(path, archive):

            # Look for classes in the directory.

            if len(self.hooks.matching(path, os.extsep + "class", archive)) != 0:
                return 1

            # Otherwise permit importing where directories containing classes exist.

            for filename in self.hooks.listdir(path, archive):
                pathname = self.hooks.path_join(path, filename)
                result = self._find_module_at_path(pathname, archive)
                if result is not None:
                    return result

        return 0

    def load_module(self, name, stuff):

        """
        Load the module with the given 'name', with a list of 'stuff' items,
        each of which describes the location of the module and is a tuple of the
        form (file, filename, (suffix, mode, data type)).

        Return a module object or raise an ImportError if a problem occurred in
        the import operation.

        Note that the 'stuff' parameter is a list and not a single item as in
        ModuleLoader.load_module. This should still work, however, since the
        find_module method produces such a list.
        """

        #print "load_module", name
        module = self._not_java_module(name, stuff)
        if module is not None:
            return module

        if not hasattr(self, "loaded_classes"):
            self.loaded_classes = {}
            top_level = 1
        else:
            top_level = 0

        main_module = self._load_module(name, stuff)

        # Initialise the loaded classes.

        if top_level:
            self._init_classes()
            delattr(self, "loaded_classes")

        return main_module

    def _not_java_module(self, name, stuff):

        "Detect non-Java modules."

        for stuff_item in stuff:
            archive, filename, info = stuff_item
            suffix, mode, datatype = info
            if datatype not in (JAVA_PACKAGE, JAVA_ARCHIVE):
                return ihooks.ModuleLoader.load_module(self, name, stuff_item)

        return None

    def _load_module(self, name, stuff):

        # Set up the module.
        # A union of all locations is placed in the module's path.

        external_names = []
        module = self.hooks.add_module(name)
        module.__path__ = [item_filename for (item_archive, item_filename, item_info) in stuff]

        # Prepare a dictionary of globals.

        global_names = module.__dict__
        global_names["__builtins__"] = __builtins__

        # Just go into each package and find the class files.

        classes = {}
        for stuff_item in stuff:

            # Extract the details, delegating loading responsibility to the
            # default loader where appropriate.
            # NOTE: Should we not be using some saved loader remembered upon
            # NOTE: installation?

            archive, filename, info = stuff_item
            suffix, mode, datatype = info

            # Get the real filename.

            filename = self._get_path_in_archive(filename)

            # Load the class files.

            for class_filename in self.hooks.matching(filename, os.extsep + "class", archive):
                s = self.hooks.read(class_filename, archive)
                class_file = classfile.ClassFile(s)
                #print "Translating", str(class_file.this_class.get_name())
                translator = bytecode.ClassTranslator(class_file)
                external_names += translator.process(global_names)

                # Record the classes found under the current module.

                self.loaded_classes[str(class_file.this_class.get_name())] = module, translator

        # Return modules used by external names.

        external_module_names = self._get_external_module_names(external_names, name)

        # Repeatedly load classes from referenced modules.

        for module_name in external_module_names:
            new_module = __import__(module_name, global_names)
            global_names[module_name.split(".")[0]] = new_module

        return module

    def _get_external_module_names(self, names, current_module_name):
        groups = self._get_names_grouped_by_module(names)
        if groups.has_key(""):
            del groups[""]

        # NOTE: Could filter out the current module and all parent modules.
        # NOTE:
        # NOTE: current_module_parts = current_module_name.split(".")
        # NOTE: while len(current_module_parts) > 0:
        # NOTE:     try:
        # NOTE:         del groups[".".join(current_module_parts)]
        # NOTE:     except KeyError:
        # NOTE:         pass
        # NOTE:     del current_module_parts[-1]

        try:
            del groups[".".join(current_module_name)]
        except KeyError:
            pass

        return groups.keys()

    def _get_names_grouped_by_module(self, names):
        groups = {}
        for name in names:
            module_name, class_name = self._get_module_and_class_names(name)
            if not groups.has_key(module_name):
                groups[module_name] = []
            groups[module_name].append(class_name)
        return groups

    def _get_module_and_class_names(self, full_name):
        full_name_parts = full_name.split(".")
        class_name = full_name_parts[-1]
        module_name = ".".join(full_name_parts[:-1])
        return module_name, class_name

    def _init_classes(self):

        # Order the classes according to inheritance.

        init_order = []
        for class_name, (module, translator) in self.loaded_classes.items():

            # Insert the base classes before any mention of the current class.

            for base_class in translator.get_base_class_references():
                base_class_name = str(base_class.get_name())
                if base_class_name not in init_order:
                    if class_name not in init_order:
                        init_order.append(base_class_name)
                    else:
                        index = init_order.index(class_name)
                        init_order.insert(index, base_class_name)

            if class_name not in init_order:
                init_order.append(class_name)

        # Create the classes.

        real_classes = {}
        real_classes_index = []
        for class_name in init_order:
            try:
                module, translator = self.loaded_classes[class_name]
                global_names = module.__dict__
                if not real_classes.has_key(module):
                    real_classes[module] = []
                real_class = translator.get_class(global_names, real_classes)
                real_classes[class_name].append(real_class)
                real_classes_index.append((module, real_class))
            except KeyError:
                # NOTE: Should be a non-Java class.
                pass

        # Finally, call __clinit__ methods for all relevant classes.

        for module, cls in real_classes_index:
            if hasattr(cls, "__clinit__"):
                global_names = module.__dict__
                eval(cls.__clinit__.func_code, global_names)

ihooks.ModuleImporter(loader=ClassLoader(hooks=ClassHooks())).install()

# vim: tabstop=4 expandtab shiftwidth=4
