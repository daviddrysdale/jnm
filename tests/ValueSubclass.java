public class ValueSubClass extends Value {
    public Value tmp;

    /**
     * Test of sub Class initialisation with super usage and foreign object initialisation.
     */
    public ValueSubClass(int x) {
        super(x);
        tmp = new Value(42);
    }

    /**
     * Test of overriding.
     */
    public void setValue(int x) {
        this.value = -x;
    }

    /**
     * Test of overriding and super methods.
     */
    public int add(int x) {
        return super.add(-x);
    }

    /**
     * Test of objects as arguments.
     */
    public void setValueObject(Value v) {
        this.value = v.getValue();
    }

    /**
     * Test program.
     */
    public static void main(String[] args) {
        SubClassValue sv = new SubClassValue(686);
        if (sv.getValue() == 686) {
            System.out.println("sv.getValue() correct: " + sv.getValue());
        } else {
            System.err.println("sv.getValue() failed!");
        }
        
        ValueSubClass vs = new ValueSubClass(109);
        if (vs.tmp.getValue() == 42) {
            System.out.println("vs.tmp.getValue() correct: " + vs.tmp.getValue());
        } else {
            System.err.println("vs.tmp.getValue() failed!");
        }
        if (vs.getValue() == 109) {
            System.out.println("vs.getValue() correct: " + vs.getValue());
        } else {
            System.err.println("vs.getValue() failed!");
        }
        vs.setValue(404);
        if (vs.getValue() == -404) {
            System.out.println("vs.getValue() correct: " + vs.getValue());
        } else {
            System.err.println("vs.getValue() failed!");
        }
        if (vs.add(404) == -808) {
            System.out.println("vs.add(404) correct: " + vs.add(404));
        } else {
            System.err.println("vs.add(404) failed!");
        }
        vs.setValueObject(sv);
        if (vs.getValue() == 686) {
            System.out.println("vs.getValue() correct: " + vs.getValue());
        } else {
            System.err.println("vs.getValue() failed!");
        }
    }
}

