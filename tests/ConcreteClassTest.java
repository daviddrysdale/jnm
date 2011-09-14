public class ConcreteClassTest extends AbstractClassTest {
    public static void main(String[] args) {
        ConcreteClassTest test = new ConcreteClassTest();
        if (test.member != null && test.member instanceof ConcreteClassTest) {
            System.out.println("test.member correct: " + test.member);
        } else {
            System.err.println("test.member failed!");
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
