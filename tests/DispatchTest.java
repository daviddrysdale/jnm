public class DispatchTest {
    public int a;
    public float b;

    public DispatchTest() {
        this.a = 1;
        this.b = 2;
    }

    public DispatchTest(int a) {
        this.a = a;
        this.b = 2;
    }

    public DispatchTest(float b) {
        this.a = 1;
        this.b = b;
    }

    public DispatchTest(int a, float b) {
        this.a = a;
        this.b = b;
    }

    public void set(int a) {
        this.a = a;
    }

    public void set(float b) {
        this.b = b;
    }

    // The ordering of the methods probably should not prevent the most specific
    // method from being chosen, but this happens with a linear search of
    // appropriate methods.

    public int test(DispatchInterface obj) {
        return obj.test();
    }

    public int test(DispatchClass1 obj) {
        return obj.test() + 10;
    }

    public int testTest(DispatchInterface obj) {
        return test(obj);
    }

    public static void main(String[] args) {
        DispatchTest test = new DispatchTest();
        DispatchClass1 dc1 = new DispatchClass1();
        DispatchClass2 dc2 = new DispatchClass2();

        if (test.a == 1 && test.b == 2) {
            System.out.println("test.a, test.b correct: " + test.a + ", " + test.b);
        } else {
            System.err.println("test.a, test.b failed!");
        }
        test.set(5);
        if (test.a == 5 && test.b == 2) {
            System.out.println("test.a, test.b correct: " + test.a + ", " + test.b);
        } else {
            System.err.println("test.a, test.b failed!");
        }
        test.set(7.0f);
        if (test.a == 5 && test.b == 7.0f) {
            System.out.println("test.a, test.b correct: " + test.a + ", " + test.b);
        } else {
            System.err.println("test.a, test.b failed!");
        }
        if (test.test(dc1) == 11) {
            System.out.println("test.test(dc1) correct: " + test.test(dc1));
        } else {
            System.err.println("test.test(dc1) failed!");
        }
        if (test.test(dc2) == 2) {
            System.out.println("test.test(dc2) correct: " + test.test(dc2));
        } else {
            System.err.println("test.test(dc2) failed!");
        }
        // Yes, one might think this could be 11, but the parameter becomes
        // "more vague" when passed to testTest.
        if (test.testTest(dc1) == 1) {
            System.out.println("test.testTest(dc1) correct: " + test.testTest(dc1));
        } else {
            System.err.println("test.testTest(dc1) failed!");
        }
        if (test.testTest(dc2) == 2) {
            System.out.println("test.testTest(dc2) correct: " + test.testTest(dc2));
        } else {
            System.err.println("test.testTest(dc2) failed!");
        }
    }
}

interface DispatchInterface {
    public int test();
}

class DispatchClass1 implements DispatchInterface {
    public int test() {
        return 1;
    }
}

class DispatchClass2 implements DispatchInterface {
    public int test() {
        return 2;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
