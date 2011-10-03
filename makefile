TEST_JAVA_FILES = $(shell find tests -name \*.java)

TEST_CLASS_FILES = $(subst tests/,bin/,$(TEST_JAVA_FILES:.java=.class))
TEST_JAVAP_FILES = $(subst tests/,javap.out/,$(TEST_JAVA_FILES:.java=.dis))
TEST_JDUMP_FILES = $(subst tests/,jdump.out/,$(TEST_JAVA_FILES:.java=.dis))

test: testclasses testjar testjdump testjnm

testclasses: bin $(TEST_CLASS_FILES)
	@list='$(TEST_CLASS_FILES)'; for cfile in $$list; do \
	  python javaclass/classfile.py $$cfile; \
	done

testjar: test.jar
	python javaclass/jarfile.py $<

test.jar: $(TEST_CLASS_FILES)
	jar -cf $@ $^

testjdump: javap.out $(TEST_JAVAP_FILES) jdump.out $(TEST_JDUMP_FILES)

testjnm: test.jar
	jnm -C test.jar

bin/%.class: tests/%.java
	javac -d bin $(TEST_JAVA_FILES)

javap.out/%.dis: bin/%.class
	javap -private -s -verbose -classpath bin $* > $@

jdump.out/%.dis: bin/%.class
	jdump $< > $@

bin:
	mkdir $@
	mkdir $@/testpackage
	mkdir $@/testpackage/subpackage
javap.out:
	mkdir $@
	mkdir $@/testpackage
	mkdir $@/testpackage/subpackage
jdump.out:
	mkdir $@
	mkdir $@/testpackage
	mkdir $@/testpackage/subpackage

clean:
	rm -rf build
	rm -f test.jar
	rm -f javaclass/*.pyc javaclass/*.py,cover
	rm -rf bin jdump.out javap.out
