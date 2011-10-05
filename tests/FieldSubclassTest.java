public class FieldSubClassTest extends FieldTest {
    public static void main(String[] args) {
        if (FieldSubClassTest.h != null && FieldSubClassTest.h.a == 789) {
            System.out.println("FieldSubClassTest.h.a correct: " + FieldSubClassTest.h.a);
        } else {
            System.out.println("FieldSubClassTest.h.a failed!");
        }
        FieldSubClassTest test = new FieldSubClassTest();
        if (test.h != null && test.h.a == 789) {
            System.out.println("test.h.a correct: " + test.h.a);
        } else {
            System.out.println("test.h.a failed!");
        }
        if (test.e != null && test.e.a == 456) {
            System.out.println("test.e.a correct: " + test.e.a);
        } else {
            System.out.println("test.e.a failed!");
        }
        if (test.f != null && test.f.a == 579) {
            System.out.println("test.f.a correct: " + test.f.a);
        } else {
            System.out.println("test.f.a failed!");
        }
    }
}
