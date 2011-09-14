public class StringBufferTest {
    StringBuffer sb1;
    StringBuffer sb2;
    String s;

    public StringBufferTest(String a, String b) {
        sb1 = new StringBuffer(a);
        sb2 = new StringBuffer(b);
        s = a + b;
    }

    public static void main(String[] args) {
        StringBufferTest test = new StringBufferTest("Hello ", "world");
        if (test.sb1.toString().equals("Hello ")) {
            System.out.println("test.sb1.toString() correct: " + test.sb1.toString());
        } else {
            System.err.println("test.sb1.toString() failed!");
        }
        if (test.sb2.toString().equals("world")) {
            System.out.println("test.sb2.toString() correct: " + test.sb2.toString());
        } else {
            System.err.println("test.sb2.toString() failed!");
        }
        if (test.s.equals("Hello world")) {
            System.out.println("test.s correct: " + test.s);
        } else {
            System.err.println("test.s failed!");
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
