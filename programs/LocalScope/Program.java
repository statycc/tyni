package LocalScope;

public class Program {

    public static void main(String[] args) {
        int result = example(5, 8, 11);
        System.out.println(result);
    }

    /**
     * For loops that reuse same variable name.
     * There are 9 distinct variables in total.
     */
    static protected int example(int a, int b, int c) {
        int x = 0, y = 2, z;
        for (int i = 0; i < a; i += 2) y += i + 1;
        for (int i = 0; i < b; i++) x += (i * i);
        for (int i = c; i > 0; --i) y -= 1;
        z = x + y;
        return z;
    }
}

