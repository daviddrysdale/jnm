public class SwitchTest {

    public int test(int x) {
        switch (x) {
            case 0:

            case 1:
            x = x + 10;
            break;

            case 2:
            x = x + 20;
            break;

            default:
            break;
        }

        return x;
    }

    public static void main(String[] args) {
        SwitchTest test = new SwitchTest();
        if (test.test(0) == 10) {
            System.out.println("test.test(0) correct: " + test.test(0));
        } else {
            System.err.println("test.test(0) failed!");
        }
        if (test.test(1) == 11) {
            System.out.println("test.test(1) correct: " + test.test(1));
        } else {
            System.err.println("test.test(1) failed!");
        }
        if (test.test(2) == 22) {
            System.out.println("test.test(2) correct: " + test.test(2));
        } else {
            System.err.println("test.test(2) failed!");
        }
        if (test.test(3) == 3) {
            System.out.println("test.test(3) correct: " + test.test(3));
        } else {
            System.err.println("test.test(3) failed!");
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
