TEST_JAVA_FILES = $(shell find tests -name \*.java)
TEST_CLASS_FILES = $(TEST_JAVA_FILES:.java=.class)
TEST_JAVAP_FILES = $(TEST_JAVA_FILES:.java=.javap)
TEST_JDUMP_FILES = $(TEST_JAVA_FILES:.java=.jdump)

test: testclasses testjar

test.jar: $(TEST_CLASS_FILES)
	jar -cf $@ $^

testclasses: $(TEST_CLASS_FILES)
	@list='$(TEST_CLASS_FILES)'; for cfile in $$list; do \
	  python javaclass/classfile.py $$cfile; \
	done

testjar: test.jar
	python javaclass/jarfile.py $<

%.class: %.java
	javac $(TEST_JAVA_FILES)

testjdump: $(TEST_JAVAP_FILES) $(TEST_JDUMP_FILES)

%.javap: %.class
	javap -private -s -verbose -classpath tests $* > $@

%.jdump: %.class
	jdump $< > $@

clean:
	rm -rf build
	rm -f test.jar
	rm -f javaclass/*.pyc javaclass/*.py,cover
	rm -f $(TEST_CLASS_FILES) $(TEST_JAVAP_FILES) $(TEST_JDUMP_FILES)
