package implicitflowifelse;


@SuppressWarnings({"UnnecessaryLocalVariable", "SameParameterValue"})
public class Program {

    public static void main(String[] args) {
        int result = foo(8);
        System.out.println(result);
    }

    /**
     * [Miguel Velez (2018] Foundations of Software Engineering: Taint Analysis [p. 46]
     * source: https://www.cs.cmu.edu/~ckaestne/15313/2018/20181023-taint-analysis.pdf
     * Implicit flow from secret to z through an intermediate third variable y.
     */
    static protected int foo(int secret) {
        int y = secret;
        int z;
        if (y == 0) {
            z = 2;
        } else {
            z = 1;
        }
        return z;
    }
}
