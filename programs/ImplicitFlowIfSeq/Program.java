package ImplicitFlowIfSeq;

public class Program {

    public static void main(String[] args) {
        int result = foo(0);
        System.out.println(result);
    }

    /**
     * Implicit information flow
     * with three variables and two conditional statements.
     */
    static protected int foo(int secret) {
        int y = 0;
        int z = 0;
        if (secret == 0) {
            y = 1;
        }
        if (y == 0) {
            z = 1;
        }
        return z;
    }
}
