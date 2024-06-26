package ifcprog3;

import java.util.Arrays;

public class Program {

    public static void main(String[] args) {
        int[] s1 = new int[5];
        float[] s2 = new float[5];
        int[] t = new int[]{1, 2, 3, 4, 5};
        int i = 0, j = t[t.length - 1];
        example(i, j, s1, s2, t);
        System.out.println(Arrays.toString(t));
        System.out.println(Arrays.toString(s1));
        System.out.println(Arrays.toString(s2));
    }

    static protected void example(int i, int j, int[] s1, float[] s2, int[] t) {
        while (t[i] != j) {
            s1[i] = j * j;
            s2[i] = 1f / j;
            i++;
        }
    }
}
