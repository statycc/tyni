package implicitflowmod;

public class Program {

    public static void main(String[] args) {
        int result = implicit(0);
        System.out.println(result);
    }

    /**
     * [Sabelfeld & Myers (2003) p. 3]
     * 2-variable implicit flow with added arithmetic operation.
     * Confidentiality can be obtained by ensuring that the process sensitivity
     * label remains high throughout the rest of the program, effectively
     * treating all values read from variables as confidential after the if
     * statement completes.
     */
    static protected int implicit(int high) {
        high = high % 2;
        int low = 0;
        if (high == 1) {
            low = 1;
        } // else skip
        return low;
    }
}
