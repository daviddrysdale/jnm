package testpackage;

public class MainTest {
    public static void main(String[] args) {
        for (int i = 0; i < args.length; i++) {
            System.out.println(args[i] + " " + new Integer(args[i].length()).toString());
        }
    }
}
