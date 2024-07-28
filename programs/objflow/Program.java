package objflow;

import java.util.Arrays;

class MyClass {
    public MyClass(String arg) {
        System.out.println(arg);
    }
}

public class Program {


    public static void main(String[] args) {
        init("?", "*");
    }

    static protected void init(String x, String y) {
        MyClass a = new MyClass(x);
        MyClass b = new MyClass(y);
    }
}
