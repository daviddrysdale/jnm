public class ComparisonTest {

    public boolean equals(int x, int y) {
        if (x == y) {
            return true;
        } else {
            return false;
        }
    }

    public boolean lessThan(int x, int y) {
        if (x < y) {
            return true;
        } else {
            return false;
        }
    }

    public boolean greaterThan(int x, int y) {
        if (x > y) {
            return true;
        } else {
            return false;
        }
    }

    public static void main(String[] args) {
        ComparisonTest test = new ComparisonTest();
        if (test.equals(1, -1)) {
            System.err.println("test.equals(1, -1) failed!");
        } else {
            System.out.println("test.equals(1, -1) correct: " + test.equals(1, -1));
        }
        if (!test.equals(10, 10)) {
            System.err.println("test.equals(10, 10) failed!");
        } else {
            System.out.println("test.equals(10, 10) correct: " + test.equals(10, 10));
        }
        if (test.lessThan(1, -1)) {
            System.err.println("test.lessThan(1, -1) failed!");
        } else {
            System.out.println("test.lessThan(1, -1) correct: " + test.lessThan(1, -1));
        }
        if (!test.lessThan(1, 15)) {
            System.err.println("test.lessThan(1, 15) failed!");
        } else {
            System.out.println("test.lessThan(1, 15) correct: " + test.lessThan(1, 15));
        }
        if (test.greaterThan(23, 29)) {
            System.err.println("test.greaterThan(23, 29) failed!");
        } else {
            System.out.println("test.greaterThan(23, 29) correct: " + test.greaterThan(23, 29));
        }
        if (!test.greaterThan(-23, -29)) {
            System.err.println("test.greaterThan(-23, -29) failed!");
        } else {
            System.out.println("test.greaterThan(-23, -29) correct: " + test.greaterThan(-23, -29));
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
