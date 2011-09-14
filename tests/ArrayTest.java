public class ArrayTest {
    public int[] array;

    public ArrayTest(int size) {
        array = new int[size];
    }

    public int get(int index) {
        return array[index];
    }

    public static void main(String[] args) {
        ArrayTest test = new ArrayTest(10);
        if (test.array.length != 10) {
            System.err.println("test.array.length failed!");
        } else {
            System.out.println("test.array.length correct: " + test.array.length);
        }
        for (int i = 0; i < test.array.length; i++) {
            test.array[i] = i + 10;
        }
        for (int j = 0; j < test.array.length; j++) {
            if (test.get(j) != j + 10) {
                System.err.println("test.get(" + j + ") failed!");
            } else {
                System.out.println("test.get(" + j + ") correct: " + test.get(j));
            }
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
