public class Application extends tkjava.Frame {
    private tkjava.Button QUIT, hiThere;

    public Application() {
        super();
        this.pack();
        this.createWidgets();
    }

    public void sayHello() {
        System.out.println("hi there, everyone!");
    }

    public void createWidgets() {

        // Instead of just getting tkjava.Frame.quit or even this.quit...

        Class[] empty = new Class[0];
        java.lang.reflect.Method quit = null, sayHello = null;
        try {
            quit = this.getClass().getMethod("quit", empty);
            sayHello = this.getClass().getMethod("sayHello", empty);
        } catch (NoSuchMethodException exc) {
            // Methods remain as null -> None and will cause runtime errors.
        }

        this.QUIT = new tkjava.Button(this);
        this.QUIT.__setitem__("text", "QUIT");
        this.QUIT.__setitem__("fg", "red");
        this.QUIT.__setitem__("command", quit);
        this.QUIT.pack();
        this.hiThere = new tkjava.Button(this);
        this.hiThere.__setitem__("text", "Hello");
        this.hiThere.__setitem__("command", sayHello);
        this.hiThere.pack();
    }

    public static void main(String[] args) {
        Application app = new Application();
        app.mainloop();
    }
}
