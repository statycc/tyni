package IFCex1;

public class Program {

    public static void main(String[] args) {
        example(1, 2, 3);
    }

    static protected void example(int h, int y, int z) {
        if (h == 0) y = 1;
        if (y == 0) z = 1;
        else y = z;
        System.out.println(h);
        System.out.println(y);
        System.out.println(z);
    }
}
