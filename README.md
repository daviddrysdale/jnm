Python tools for investigating Java class files
===============================================

This is a collection of tools for investigating Java class files and jar files.

* jnm lists the symbols in a given class file, analogously to the UNIX nm command.
* jldd shows the package dependencies for a given jar file, analogously to the UNIX ldd command.
* jdump performs a disassembly of a class file (similarly to the JDK javap command).
* jdemangle converts internal Java descriptor formats to user-comprehensible versions.

License
-------
This code is covered by the GNU Lesser General Public License, version 3 or higher.

Example Usage
-------------

    % jnm bin/StaticTestClass.class 
    00000217 C StaticTestClass
             K java.lang.Object
    00000004 I StaticTestClass.x:I
    0000000c T StaticTestClass.<init>:()V
             R java.lang.Object.<init>:()V
    0000000a T StaticTestClass.<init>:(I)V
    00000008 T StaticTestClass.newInstance:()LStaticTestClass;
    00000009 T StaticTestClass.newInstance:(I)LStaticTestClass;
    00000004 T StaticTestClass.getNumber:()I

    % jnm --demangle bin/StaticTestClass.class 
    00000217 C StaticTestClass
             K java.lang.Object
    00000004 I int StaticTestClass.x
    0000000c T void StaticTestClass.<init>()
             R void java.lang.Object.<init>()
    0000000a T void StaticTestClass.<init>(int)
    00000008 T StaticTestClass StaticTestClass.newInstance()
    00000009 T StaticTestClass StaticTestClass.newInstance(int)
    00000004 T int StaticTestClass.getNumber()

    % jldd test.jar
    	 java.io => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.lang => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.lang.annotation => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.util => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar

    % jnm --help
    jnm [options] file[s]
    
    jnm displays the symbol table of each file in the argument list.  If an
    argument is a jarfile, a listing for each class file in the file will be
    produced.
    
    Each symbol name is preceded by its value (blanks if undefined).  This
    value is followed by one of the following characters, representing the
    symbol type:
    
        C  Class
        D  Static field
        I  Instance field
        T  Method
    
        K  Undefined reference to class
        F  Undefined reference to static field
        J  Undefined reference to instance field
        R  Undefined reference to method
    
    If the symbol is private, the symbol's type is instead represented by
    the corresponding lowercase letter.
    
    Options:
       -h/--help               : show this help
       -p/--no-sort            : Don't sort; display in order encountered (default)
       -n/--numeric-sort       : Sort symbols numerically
       -r/--reverse-sort       : Sort in reverse order
       -a/--alpha-sort         : Sort alphabetically
       -u/--undefined-only     : Display only undefined symbols
       -U/--defined-only       : Don't display undefined symbols
       -g/--extern-only        : Don't display external (non-private) symbols
       -c/--class-only         : Only display classes, not fields or methods
       -f/--flatten            : Resolve references within the set of files specified
       -A/--print-file-name    : Write the pathname on each line
       -j/--symbols-only       : Just display the symbol names (no value or type)
       -C/--demangle           : Decode symbol names into user-visible names
       --m64                   : Assume pointers are 64-bit (default)
       --m32                   : Assume pointers are 32-bit


Provenance
----------
The core functionality of these tools is provided in the javaclass/classfile.py code, which is a minor variant
on code taken from [Paul Boddie's javaclass](http://hgweb.boddie.org.uk/javaclass/) library.
