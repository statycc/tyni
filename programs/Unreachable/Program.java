package Unreachable;

public class Program {

    public static void main(String[] args) {
        int result = foo(42);
        System.out.println(result);
    }

    /**
     * Explicit information flow from secret to x.
     * However, the violating statement is unreachable.
     */
    static protected int foo(int secret) {
        int j = 0;
        int x = 0;
        if (secret == 0) {
        } else {
            if (secret == 0) {
                x = secret;
            } else {
            }
        }
        j = x;
        return j;
    }
}
