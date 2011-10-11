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
    % jldd test.jar
    	 java.io => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.lang => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.lang.annotation => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar
    	 java.util => /System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Classes/classes.jar



Provenance
----------
The core functionality of these tools is provided in the javaclass/classfile.py code, which is a minor variant
on code taken from Paul Boddie's javaclass (http://hgweb.boddie.org.uk/javaclass/).
