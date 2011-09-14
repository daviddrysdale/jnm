#!/usr/bin/env python

"Run the test suite."

import os, glob
import runclass
import java.lang

def get_test_sources():
    return glob.glob("*.java")

def get_test_classes():
    # Use the original source files to decide which classes have main methods.
    return [os.path.splitext(f)[0] for f in get_test_sources()]

def compile_test_files(javac):
    for java_file in get_test_sources():
        class_file = os.path.splitext(java_file)[0] + ".class"
        if not os.path.exists(class_file) or os.path.getmtime(class_file) < os.path.getmtime(java_file):
            print "Compiling", java_file
            os.system(javac + " " + java_file)

def run_test_files():
    classes = runclass.load_classes(get_test_classes())
    for cls in classes:
        print "Running", cls
        runclass.run_class(cls, [java.lang.String("Test")])

if __name__ == "__main__":
    import sys

    # Find the compiler.

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        javac = os.path.join(java_home, "bin", "javac")
    elif len(sys.argv) > 1:
        javac = sys.argv[1]
    else:
        print "Guessing that javac is your Java compiler."
        print "If this does not work then please specify the full path as an"
        print "argument to this program or set JAVA_HOME to refer to the JDK"
        print "installation."
        javac = "javac"

    if javac != "javac" and not os.path.exists(javac):
        print "The suggested Java compiler cannot be found."
        sys.exit(1)

    # Compile the programs.

    os.chdir("tests")
    compile_test_files(javac)
    run_test_files()

    print "Tests complete."

# vim: tabstop=4 expandtab shiftwidth=4
