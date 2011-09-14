public class Value {
    protected int value;

    public Value(int value) {
        this.value = value;
    }

    public int getValue() {
        return this.value;
    }

    public void setValue(int value) {
        this.value = value;
    }

    public boolean isPositive() {
        return this.value > 0;
    }

    public int compare(int value) {
        if (value < this.value) {
            return -1;
        } else if (value == this.value) {
            return 0;
        } else {
            return 1;
        }
    }

    public int add(int value) {
        return this.value + value;
    }

    public Value newValue() {
        return new Value(this.getValue());
    }

    public static void main(String[] args) {
        Value v = new Value(123);
        if (v.getValue() != 123) {
            System.err.println("v.getValue() failed!");
        } else {
            System.out.println("v.getValue() correct: " + v.getValue());
        }
        v.setValue(456);
        if (v.getValue() != 456) {
            System.err.println("v.setValue(456) or v.getValue() failed!");
        } else {
            System.out.println("v.getValue() correct: " + v.getValue());
        }
        if (!v.isPositive()) {
            System.err.println("v.isPositive() failed!");
        } else {
            System.out.println("v.isPositive() correct: " + v.isPositive());
        }
        v.setValue(-789);
        if (v.isPositive()) {
            System.err.println("v.isPositive() failed!");
        } else {
            System.out.println("v.isPositive() correct: " + v.isPositive());
        }
        if (v.compare(-790) != -1) {
            System.err.println("v.compare(-790) failed!");
        } else {
            System.out.println("v.compare(-790) correct: " + v.compare(-790));
        }
        if (v.compare(-788) != 1) {
            System.err.println("v.compare() failed!");
        } else {
            System.out.println("v.compare(-788) correct: " + v.compare(-788));
        }
        if (v.compare(-789) != 0) {
            System.err.println("v.compare() failed!");
        } else {
            System.out.println("v.compare(-789) correct: " + v.compare(-789));
        }
        Value v2 = v.newValue();
        if (v == v2) {
            System.err.println("v.newValue() failed!");
        }
        v2.setValue(123);
        if (v.getValue() == v2.getValue()) {
            System.err.println("v.newValue() failed (to establish separate members)!");
        } else {
            System.out.println("v.getValue() == v2.getValue() correct: " + (v.getValue() == v2.getValue()));
        }
        if (v2.add(-123) != 0) {
            System.err.println("v2.add(-123) failed!");
        } else {
            System.out.println("v2.add(-123) correct: " + v2.add(-123));
        }
        v2.setValue(255);
        if (v2.getValue() != 255) {
            System.err.println("v2.setValue(255) or v2.getValue() failed!");
        } else {
            System.out.println("v2.getValue() correct: " + v2.getValue());
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4
