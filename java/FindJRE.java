/*
 * Determine various class paths
 */

class FindJRE {
  public static void main(String[] args) {
    String classPath = System.getProperty("sun.boot.class.path");
    if (classPath == null) {
      classPath = System.getProperty("java.boot.class.path");
    }
    if (classPath != null) {
      System.out.println("Boot-Class-Path: " + classPath);
    }
    classPath = System.getProperty("java.class.path");
    if (classPath != null) {
      System.out.println("Class-Path: " + classPath);
    }
    String separator = System.getProperty("path.separator");
    if (separator != null) {
      System.out.println("Class-Path-Separator: " + separator);
    }
  }
}
