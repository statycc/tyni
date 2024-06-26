package vectmult;

@SuppressWarnings("SameParameterValue")
public class Program {

    public static void main(String[] args) {
        int[] arr = new int[]{2 * 3, 5, 6, 8 * 9};
        mul(arr, 5);
    }

    /**
     * A "foreach"-style loops.
     */
    static protected void mul(int[] arr, int n) {
        for (int x : arr) {
            int t = x * n;
            System.out.println(t);
        }
        for (int x : arr) {
            for (int x1 : arr)
                System.out.println(x * x1);
        }
    }
}

