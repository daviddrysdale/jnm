TEST_JAVA_FILES = $(shell find tests -name \*.java)
TEST_CLASS_FILES = $(TEST_JAVA_FILES:.java=.class)

test: $(TEST_CLASS_FILES)
	@list='$(TEST_CLASS_FILES)'; for cfile in $$list; do \
	  python javaclass/classfile.py $$cfile; \
	done

%.class: %.java
	javac $(TEST_JAVA_FILES)

clean:
	rm -rf build
	rm -f javaclass/*.pyc javaclass/*.py,cover
	rm -f tests/*.class
	rm -f tests/testpackage/*.class
	rm -f tests/testpackage/subpackage/*.class
