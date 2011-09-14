public class StringTest {
    private String s;
    private String s2 = new String("abc");
    private static String s3;
    public static String s4 = new String("xyz");

    public StringTest() {
        s = s2;
    }

    public StringTest(String newString) {
        s = newString;
    }

    public StringTest(String firstString, String secondString) {
        s = firstString + secondString;
    }

    public static void main(String[] args) {
        if (StringTest.s4.equals("xyz")) {
            System.out.println("StringTest.s4 correct: " + StringTest.s4);
        } else {
            System.err.println("StringTest.s4 failed!");
        }
        StringTest test0 = new StringTest();
        if (test0.s.equals("abc")) {
            System.out.println("test0.s correct: " + test0.s);
        } else {
            System.err.println("test0.s failed!");
        }
        StringTest test1 = new StringTest("Test");
        if (test1.s.equals("Test")) {
            System.out.println("test1.s correct: " + test1.s);
        } else {
            System.err.println("test1.s failed!");
        }
        StringTest test2 = new StringTest("Hello ", "world");
        if (test2.s.equals("Hello world")) {
            System.out.println("test2.s correct: " + test2.s);
        } else {
            System.err.println("test2.s failed!");
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
