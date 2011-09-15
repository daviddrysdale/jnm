import java.util.List;
import java.util.ArrayList;
class GenericTest<T> {
  public T mT;
  public GenericTest(T t) {
    mT = t;
    List<T> l = new ArrayList<T>();
  }
}