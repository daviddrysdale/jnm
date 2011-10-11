/*
 * Determine various class paths
 */

class FindJRE {
  public static void main(String[] args) {
    System.out.println("Boot-Class-Path: " + System.getProperty("sun.boot.class.path"));
    System.out.println("Class-Path: " + System.getProperty("java.class.path"));
    System.out.println("Class-Path-Separator: " + System.getProperty("path.separator"));
  }
}