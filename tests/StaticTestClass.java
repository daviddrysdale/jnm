
class StaticTestClass {
    public int x;

    public StaticTestClass() {
        x = 321;
    }

    public StaticTestClass(int x) {
        this.x = x;
    }

    public static StaticTestClass newInstance() {
        return new StaticTestClass();
    }

    public static StaticTestClass newInstance(int x) {
        return new StaticTestClass(x);
    }

    public static int getNumber() {
        return 456;
    }
}
