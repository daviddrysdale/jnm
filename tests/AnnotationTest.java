
class AnnotationTest {
  @Annotation(a=1, b="foo")
  public static void hello() {
  }
  @AnnotationMarker
  private static int getx() {
    return 1;
  }
}