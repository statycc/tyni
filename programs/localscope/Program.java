package localscope;

@SuppressWarnings("SameParameterValue")
public class Program {

    public static void main(String[] args) {
        System.out.println(example(5, 8, 11));
    }

    /**
     * For loops that reuse same variable name.
     * There are 9 distinct variables in total.
     */
    static protected int example(int a, int b, int c) {
        int x = 0, y = 2, z;
        for (int i = 0; i < a; i += 2) {
            for (int j = 0; j < 2; j++) y += i + j;
        }
        for (int i = 0; i < b; i++) {
            if (i < 5) {
                x += (i * i);
            } else {
                int j = i - 10;
                x += j;
            }
        }
        for (int j = c; j > 0; --j) {
            for (int i = 0; i < 10; i++) y -= i;
        }
        z = x + y;
        return z;
    }
}

