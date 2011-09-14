public abstract class AbstractClassTest {
    public static ConcreteClassTest member = new ConcreteClassTest();

    public static void main(String[] args) {
        if (AbstractClassTest.member != null) {
            System.out.println("AbstractClassTest.member correct: " + AbstractClassTest.member);
        } else {
            System.err.println("AbstractClassTest.member failed!");
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
