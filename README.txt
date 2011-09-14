This file contains some information on the essential concepts and principles
involved in the use of this software.

Installation
------------

To build the software, perhaps as part of a packaging process, you can run the
following command:

  python setup.py build

To directly install the software in a system-wide location, you can run the
following command:

  python setup.py install

The installation adds the java and javaclass packages to your site-packages
directory and the runclass.py program to the same bin directory that python
resides in. However, it is arguably preferable to make an operating system
package for the software and use the system's package manager to install and
potentially uninstall the software.

Testing
-------

It should be possible to just run the test.py program and see the results:

  python test.py

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for javaclass at the time of release is:

http://www.boddie.org.uk/python/javaclass.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt, docs/lgpl-3.0.txt and docs/gpl-3.0.txt for more information.

Dependencies
------------

Python              Tested with Python 2.3, although javaclass.classfile
                    should work on any recent Python 2.x release.

A Java toolchain    Tested with whichever Sun JDK for Java release was current
                    in 2005. ;-)

Class Search Paths
------------------

Java classes belonging to packages are located using sys.path or PYTHONPATH
in the same way that they would be located using the Java classpath (or
CLASSPATH environment variable). Thus, the rules for locating package
classes are as follows:

 * Classes residing within plain directories which represent a package
   hierarchy can be accessed by putting the parent directory of the top of
   the package hierarchy on the PYTHONPATH (or sys.path). For example, a
   package called mypackage, represented by a directory of the same name at
   /home/java/classes/mypackage, would be made accessible by adding the
   /home/java/classes directory to the PYTHONPATH.

 * Classes residing within .jar files can be accessed by putting the path to
   each .jar file on the PYTHONPATH. For example, a package called
   mypackage, represented by a file located at /home/java/lib/mypackage.jar,
   would be made accessible by adding the /home/java/lib/mypackage.jar file
   to the PYTHONPATH.

Note that classes not belonging to a package cannot be accessed via such
search paths and are made available using a special module (see "Non-package
Classes" below).

Importing Classes
-----------------

In Python, the following statement should be enough to enable Java class
import:

  import javaclass.classhook

(Other modules reside in the javaclass package, so it is possible to access
them without changing Python's import mechanisms, should such modification
be undesirable or unnecessary.)

Importing Non-package Classes
-----------------------------

Classes which do not belong to a package are only accessible when residing
in the current working directory of any program attempting to use them. Such
classes will not be made available automatically, but must be imported from
a special module called __this__.

 * Usage of the "import __this__" statement will cause all classes in the
   current directory to be made available within the __this__ module.

 * Usage of the "from __this__ import" construct will cause all classes in
   the current directory to be processsed, but only named classes will be
   made available in the global namespace unless "*" was specified (which
   will, as usual, result in all such classes being made available).

Running Java Classes
--------------------

Java classes with a public, static main method can be run directly using the
runclass.py program.

  * Free-standing classes (ie. not belonging to packages) can be run from
    the directory in which they reside. For example, suitable classes in the
    tests directory would be run as follows:

    cd tests
    runclass.py MainTest hello world

  * Classes residing in packages can be run by ensuring that the packages
    are registered on the PYTHONPATH (see "Class Search Paths" above). Then,
    the testpackage.MainTest class (for example) would be run as follows:

    runclass.py testpackage.MainTest hello world

Accessing Python Libraries from Java
------------------------------------

To wrap Python libraries for use with Java, skeleton classes need to be
compiled corresponding to each of the wrapped classes. Each of the methods
in the skeleton classes can be empty (or return any permissible value) since
the only purpose they serve is to provide the Java compiler with information
about the Python libraries.

  1. Compile the skeleton classes:

     javac examples/Tkinter/tkjava/*.java

  2. Compile the Java classes which use the wrapped Python libraries:

     javac -classpath examples/Tkinter examples/Tkinter/Application.java

  3. Run the wrap.py tool on the directory where the skeleton class files
     reside, providing the name of the Python package or module being
     wrapped. This converts the directory into a Python package:

     python tools/wrap.py examples/Tkinter/tkjava Tkinter

     Since the Java class files, if left in the processed directory, would
     be detected and imported using the special import hook, and since this
     would result in two conflicting implementations being imported (with
     possibly the non-functional Java classes being made available instead
     of the generated wrapper classes), the wrap.py tool removes all
     processed class files, leaving only Python source files in the
     processed directory.

  4. The Java classes which use the wrapped Python libraries can now be
     imported and used as described above. The wrapper package (tkjava in
     the above example) needs to reside in sys.path or PYTHONPATH, as must
     the wrapped library (Tkinter in the above example).

     cd examples/Tkinter
     runclass.py Application

Issues
------

Fix the class initialisation so that non-Java classes (and already imported
classes) are obtained. Prevent re-entry into module importing for modules
already being imported (if this is not handled already by the Python import
mechanisms).

Implement better importing mechanisms so that circular module dependencies
can be avoided. For example, when dealing with java.lang classes which
depend on java.security classes which then inherit from java.lang.Object,
the classes should all be imported but only initialised after no more
importing is necessary. Since usage of external names is recorded in the
bytecode translation process, it should be possible to reach such a
condition definitively.

The test program crashes, fairly quickly under Python 2.4, too. There seems
to be some kind of memory allocation problem.

Investigate better exception raising. Currently, exceptions have to be
derived from object so that object.__new__ can be used upon them. However,
this seems to prevent them from being raised, and they need to be wrapped
within Exception so that the information can be transmitted to the
exception's handler.

Consider nicer ways of writing the method names in Python, perhaps using a
function which takes the individual parameter types as arguments.

New in javaclass 0.2 (Changes since javaclass 0.1)
--------------------------------------------------------

  * Added Braden Thomas' class file serialisation patches.
  * Relicensed under the LGPL version 3 or later.

Release Procedures
------------------

Update the javaclass/__init__.py __version__ attribute.
Update the release notes (see above).
Update the setup.py and PKG-INFO files.
Check the setup.py file and ensure that all package directories are
mentioned.
Tag, export.
Archive, upload.
