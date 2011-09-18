
class AnnotationTest {
  @Annotation(a=1, b="foo")
  public static void hello() {
  }
  @AnnotationMarker
  private static int getx() {
    return 1;
  }
  private static int addup(@Annotation(b="param") int x, 
                           int y) {
    return x+y;
  }
}