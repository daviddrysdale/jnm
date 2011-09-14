public class MultiArrayTest {
    public int[][] multiArray;

    public MultiArrayTest(int[] multiSizes) {
        multiArray = new int[multiSizes[0]][multiSizes[1]];
    }

    public int get(int index1, int index2) {
        return multiArray[index1][index2];
    }

    public static void main(String[] args) {
        int[] sizes = {4, 7};
        MultiArrayTest test = new MultiArrayTest(sizes);
        if (test.multiArray.length != 4) {
            System.err.println("test.multiArray.length failed!");
        } else {
            System.out.println("test.multiArray.length correct: " + test.multiArray.length);
        }
        if (test.multiArray[0].length != 7) {
            System.err.println("test.multiArray[0].length failed!");
        } else {
            System.out.println("test.multiArray[0].length correct: " + test.multiArray[0].length);
        }
        if (test.multiArray[3][6] != 0) {
            System.err.println("test.multiArray[3][6] failed!");
        } else {
            System.out.println("test.multiArray[3][6] correct: " + test.multiArray[3][6]);
        }
        test.multiArray[3][6] = 36;
        if (test.get(3, 6) != 36) {
            System.err.println("test.get(3, 6) failed!");
        } else {
            System.out.println("test.get(3, 6) correct: " + test.get(3, 6));
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
