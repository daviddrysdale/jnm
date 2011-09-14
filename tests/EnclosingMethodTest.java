public class EnclosingMethodTest {
  public int outer(int a) {
    class InnerClass {
      public int inner(int b) {
        return b+1;
      }
    }
    InnerClass inc = new InnerClass();
    return inc.inner(a);
  }
}

