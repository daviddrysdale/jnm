class AnnotationTest {
  @AnnotationMarker(a=1, b="foo")
  public static void hello() {
  }
  @Preliminary
  private static int getx() {
    return 1;
  }
}