package mvt;

import java.util.Arrays;

@SuppressWarnings({"ConstantValue", "ManualMinMaxCalculation"})
public class Program {

    public static void main(String[] args) {
        int[] x1 = {1, 2, 3};
        int[] x2 = new int[]{2, 2, 2}, y1 = new int[]{1, 6, 4};
        int[] y2 = {1, 1, 1};
        int[][] A = new int[][]{x1, {2, 2, 2}, {3, 3, 3}};
        int N = x2.length < x1.length ? x2.length : x1.length;
        mvt(N, x1, x2, y1, y2, A);
        System.out.println(Arrays.toString(x1));
        System.out.println(Arrays.toString(x2));
    }

    /**
     * From PolyBench/C benchmark suite.
     * Linear algebra/mvt kernel
     */
    static protected void mvt(int N, int[] x1, int[] x2, int[] y1, int[] y2, int[][] A) {
        int i, j;
        for (i = 0; i < N; i++)
            for (j = 0; j < N; j++)
                x1[i] = x1[i] + A[i][j] * y1[j];
        for (i = 0; i < N; i++)
            for (j = 0; j < N; j++)
                x2[i] = x2[i] + A[j][i] * y2[j];
    }
}

