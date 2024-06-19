package IFCprog2a;

public class Program {

    public static void main(String[] args) {
        example(0, 0, 0, 1);
    }

    static protected void example(int w, int x, int y, int z) {
        w = w + x;
        z = y + 2;
        x = y;
        z = z * 2;

        System.out.println(w);
        System.out.println(x);
        System.out.println(y);
        System.out.println(z);
    }
}
