public class StaticTest {

    public static StaticTestClass staticMember = StaticTestClass.newInstance();
    public static StaticTestClass staticMember2 = StaticTestClass.newInstance(123);
    public static int staticMember3 = StaticTestClass.getNumber();

    public static void main(String[] args) {
        if (StaticTest.staticMember != null && StaticTest.staticMember.x == 321) {
            System.out.println("StaticTest.staticMember.x correct: " + StaticTest.staticMember.x);
        } else {
            System.out.println("StaticTest.staticMember.x failed!");
        }
        if (StaticTest.staticMember2 != null && StaticTest.staticMember2.x == 123) {
            System.out.println("StaticTest.staticMember2.x correct: " + StaticTest.staticMember2.x);
        } else {
            System.out.println("StaticTest.staticMember2.x failed!");
        }
        if (StaticTest.staticMember3 == 456) {
            System.out.println("StaticTest.staticMember3 correct: " + StaticTest.staticMember3);
        } else {
            System.out.println("StaticTest.staticMember3 failed!");
        }
    }
}

