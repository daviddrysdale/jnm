public class WidgetTest extends qtjava.QWidget {
    public WidgetTest(qtjava.QWidget parent, String name) {
        super(parent, name);
    }

    public static void main(String[] args) {
        String[] empty = new String[0];
        qtjava.QApplication app = new qtjava.QApplication(empty);
        WidgetTest wt = new WidgetTest(null, "WidgetTest");
        wt.show();
        app.exec_loop();
    }
}
