package ifcprog2b;

@SuppressWarnings("SuspiciousNameCombination")
public class Program {

    public static void main(String[] args) {

        example(0, 0, 0, 2);
    }

    static protected void example(int w, int x, int y, int z) {
        if (w > x) {
            w = w + x;
            z = y + 2;
        } else {
            x = y;
            z = z * 2;
        }
        System.out.println(w);
        System.out.println(x);
        System.out.println(z);
    }
}
