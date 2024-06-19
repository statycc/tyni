package ImplicitFlowNested;

public class Program {

    public static void main(String[] args) {
        int result = foo(42);
        System.out.println(result);
    }

    /**
     * Implicit information flow leak
     * through control variable.
     */
    static protected int foo(int secret) {
        int k, x = 0;
        if (secret == 0) {
        } else {
            if (secret == 1) {
                x = 2;
            } else {
            }
        }
        k = x;
        return k;
    }
}
