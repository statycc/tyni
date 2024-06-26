package ifcprog2a;

@SuppressWarnings("SuspiciousNameCombination")
public class Program {

    public static void main(String[] args) {
        example(0, 0, 0);
    }

    static protected void example(int w, int x, int y) {
        w = w + x;
        int z = y + 2;
        x = y;
        z = z * 2;

        System.out.println(w);
        System.out.println(x);
        System.out.println(y);
        System.out.println(z);
    }
}
