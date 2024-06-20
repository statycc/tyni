package IFCprog1;

public class Program {

    public static void main(String[] args) {
        example(0, 1, 1);
    }

    static protected void example(int x, int y, int z) {
        int t;
        if (z == 1) {
            if (x == 1) y = 1;
            else y = 0;
        } else {x = y; t++;}

        System.out.println(x);
        System.out.println(y);
    }
}
