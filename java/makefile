all: FindJRE.jar

FindJRE.jar: manifest FindJRE.class manifest
	jar -cfm $@ $^

%.class: %.java
	javac $<

test: FindJRE.jar
	java -jar $< 

clean:
	rm -f FindJRE.jar FindJRE.class