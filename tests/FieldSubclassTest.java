public class FieldSubclassTest extends FieldTest {
    public static void main(String[] args) {
        if (FieldSubclassTest.h != null && FieldSubclassTest.h.a == 789) {
            System.out.println("FieldSubclassTest.h.a correct: " + FieldSubclassTest.h.a);
        } else {
            System.out.println("FieldSubclassTest.h.a failed!");
        }
        FieldSubclassTest test = new FieldSubclassTest();
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

// vim: tabstop=4 expandtab shiftwidth=4
