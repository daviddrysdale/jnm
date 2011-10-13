TEST_JAVA_FILES = $(shell find tests -name \*.java)

TEST_CLASS_FILES = $(subst tests/,,$(TEST_JAVA_FILES:.java=.class))
TEST_BIN_CLASS_FILES = $(subst tests/,bin/,$(TEST_JAVA_FILES:.java=.class))
TEST_JAVAP_FILES = $(subst tests/,javap.out/,$(TEST_JAVA_FILES:.java=.dis))
TEST_JDUMP_FILES = $(subst tests/,jdump.out/,$(TEST_JAVA_FILES:.java=.dis))

test: testclasses testjar testjdump testjnm testjldd

testclasses: bin $(TEST_BIN_CLASS_FILES)
	@list='$(TEST_BIN_CLASS_FILES)'; for cfile in $$list; do \
	  python javaclass/classfile.py $$cfile; \
	done

testjar: test.jar
	python javaclass/jarfile.py $<

test.jar: $(TEST_BIN_CLASS_FILES)
	cd bin && jar -cf ../$@ $(TEST_CLASS_FILES) *\$*.class

testjdump: javap.out $(TEST_JAVAP_FILES) jdump.out $(TEST_JDUMP_FILES)

testjnm: test.jar
	jnm -C test.jar

bin/%.class: tests/%.java
	javac -d bin $(TEST_JAVA_FILES)

testjldd: test.jar java_make
	jldd test.jar

java_make:
	cd java && $(MAKE)

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

clean: java_clean
	rm -rf build deb_dist dist
	rm -f test.jar
	rm -f javaclass/*.pyc javaclass/*.py,cover
	rm -rf bin jdump.out javap.out

java_clean:
	cd java && $(MAKE) clean

VERSION=$(shell grep __version__ javaclass/__init__.py | sed 's/__version__ = "\(.*\)"/\1/')
TARBALL=dist/jnm-$(VERSION).tar.gz
# Build setuptools packaged tarball $(TARBALL)
sdist: java/FindJRE.class
	python setup.py sdist
$(TARBALL): sdist

install:
	python setup.py build
	sudo python setup.py install

distclean: clean
	rm -rf jnm.egg-info
	rm -f FindJRE.class

# Create Debian package.  Requires py2dsc, included in the python-stdeb package.
DEB_VERSION=$(VERSION)-1_all
deb: deb_dist/python-jnm_$(DEB_VERSION).deb

deb_dist/python-jnm_$(VERSION)-1_all.deb: $(TARBALL)
	py2dsc $(TARBALL)
	cd deb_dist/jnm-$(VERSION) && dpkg-buildpackage -us -uc -nc

