package ifcex2;

@SuppressWarnings({"SameParameterValue", "UnusedAssignment", "SuspiciousNameCombination"})
public class Program {

    public static void main(String[] args) {
        example(42);
    }

    static protected void example(int y) {
        int z, x;

        z = 3;
        x = y;
        x = z;

        System.out.println(x);
        System.out.println(y);
        System.out.println(z);
    }
}
