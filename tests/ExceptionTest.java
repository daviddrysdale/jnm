public class ExceptionTest {
    public int last;

    public int testThrow(int x) throws java.lang.Exception {
        if (x == 0) {
            throw new MyException();
        } else if (x == 1) {
            throw new MyOtherException();
        } else {
            return 1;
        }
    }

    public int testCatch(int x) {
        try {
            if (x == 0) {
                throw new MyException();
            } else if (x == 1) {
                throw new MyOtherException();
            } else {
                x = 1;
            }
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        }
        return x;
    }

    public int testIncomingCatch(int x) {
        try {
            return testThrow(x);
        } catch (MyException exc) {
            return 3;
        } catch (MyOtherException exc) {
            return 2;
        } catch (java.lang.Exception exc) {
            return -1; // Should be unreachable, really.
        }
    }

    public int testFinally(int x) throws java.lang.Exception {
        try {
            if (x == 0) {
                x = 3;
                throw new MyException();
            } else if (x == 1) {
                x = 2;
                throw new MyOtherException();
            }
            x = 1;
        } finally {
            x += 10;
            last = x;
        }
        return x;
    }

    public int testCatchFinally(int x) throws MyUncheckedException {
        try {
            if (x == 0) {
                throw new MyException();
            } else if (x == 1) {
                throw new MyOtherException();
            } else if (x == 2) {
                throw new MyUncheckedException();
            }
            x = 1;
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        } finally {
            x += 10;
            last = x;
        }
        return x;
    }

    public int testMultipleCatch(int x, int y) {
        try {
            x = testThrow(x);
        } catch (MyException exc) {
            x = 3;
        } catch (MyOtherException exc) {
            x = 2;
        } catch (java.lang.Exception exc) {
            x = -1; // Should be unreachable, really.
        }

        try {
            x += 10 * testThrow(y);
        } catch (MyException exc) {
            x += 30;
        } catch (MyOtherException exc) {
            x += 20;
        } catch (java.lang.Exception exc) {
            x += -10; // Should be unreachable, really.
        }
        return x;
    }

    public static void main(String[] args) {
        ExceptionTest test = new ExceptionTest();
        try {
            test.testThrow(0);
            System.err.println("testThrow(0) failed!");
        } catch (MyException exc) {
            System.out.println("testThrow(0) correct: " + exc);
        } catch (java.lang.Exception exc) {
            System.err.println("testThrow(0) failed (MyException expected)!");
        }
        try {
            test.testThrow(1);
            System.err.println("testThrow(1) failed!");
        } catch (MyOtherException exc) {
            System.out.println("testThrow(1) correct: " + exc);
        } catch (java.lang.Exception exc) {
            System.err.println("testThrow(1) failed (MyOtherException expected)!");
        }
        try {
            if (test.testThrow(2) != 1) {
                System.err.println("testThrow(2) failed!");
            } else {
                System.out.println("testThrow(2) correct.");
            }
        } catch (java.lang.Exception exc) {
            System.err.println("testThrow(2) failed (no exception expected)!");
        }

        if (test.testCatch(0) != 3) {
            System.err.println("testCatch(0) failed!");
        } else {
            System.out.println("testCatch(0) correct.");
        }
        if (test.testCatch(1) != 2) {
            System.err.println("testCatch(1) failed!");
        } else {
            System.out.println("testCatch(1) correct.");
        }
        if (test.testCatch(2) != 1) {
            System.err.println("testCatch(2) failed!");
        } else {
            System.out.println("testCatch(2) correct.");
        }

        if (test.testIncomingCatch(0) != 3) {
            System.err.println("testIncomingCatch(0) failed!");
        } else {
            System.out.println("testIncomingCatch(0) correct.");
        }
        if (test.testIncomingCatch(1) != 2) {
            System.err.println("testIncomingCatch(1) failed!");
        } else {
            System.out.println("testIncomingCatch(1) correct.");
        }
        if (test.testIncomingCatch(2) != 1) {
            System.err.println("testIncomingCatch(2) failed!");
        } else {
            System.out.println("testIncomingCatch(2) correct.");
        }

        try {
            test.testFinally(0);
            System.err.println("testFinally(0) failed!");
        } catch (MyException exc) {
            if (test.last == 13) {
                System.out.println("testFinally(0) correct: set " + test.last);
            } else {
                System.err.println("testFinally(0) failed: set " + test.last);
            }
        } catch (java.lang.Exception exc) {
            System.err.println("testFinally(0) failed!");
        }
        try {
            test.testFinally(1);
            System.err.println("testFinally(1) failed!");
        } catch (MyOtherException exc) {
            if (test.last == 12) {
                System.out.println("testFinally(1) correct: set " + test.last);
            } else {
                System.err.println("testFinally(1) failed: set " + test.last);
            }
        } catch (java.lang.Exception exc) {
            System.err.println("testFinally(1) failed!");
        }
        try {
            if (test.testFinally(2) != 11) {
                System.err.println("testFinally(2) failed!");
            } else {
                System.out.println("testFinally(2) correct.");
            }
        } catch (java.lang.Exception exc) {
            System.err.println("testFinally(2) failed!");
        }

        try {
            if (test.testCatchFinally(0) != 13) {
                System.err.println("testCatchFinally(0) failed!");
            } else {
                System.out.println("testCatchFinally(0) correct.");
            }
        } catch (MyUncheckedException exc) {
            System.err.println("testCatchFinally(0) failed!");
        }
        try {
            if (test.testCatchFinally(1) != 12) {
                System.err.println("testCatchFinally(1) failed!");
            } else {
                System.out.println("testCatchFinally(1) correct.");
            }
        } catch (MyUncheckedException exc) {
            System.err.println("testCatchFinally(0) failed!");
        }
        try {
            test.testCatchFinally(2);
            System.err.println("testCatchFinally(2) failed!");
        } catch (MyUncheckedException exc) {
            if (test.last != 12) {
                System.err.println("testCatchFinally(2) failed!");
            } else {
                System.out.println("testCatchFinally(2) correct.");
            }
        }

        if (test.testMultipleCatch(0, 1) != 23) {
            System.err.println("testMultipleCatch(0, 1) failed!");
        } else {
            System.out.println("testMultipleCatch(0, 1) correct.");
        }
        if (test.testMultipleCatch(1, 2) != 12) {
            System.err.println("testMultipleCatch(1, 2) failed!");
        } else {
            System.out.println("testMultipleCatch(1, 2) correct.");
        }
        if (test.testMultipleCatch(2, 0) != 31) {
            System.err.println("testMultipleCatch(2, 0) failed!");
        } else {
            System.out.println("testMultipleCatch(2, 0) correct.");
        }
    }
}
