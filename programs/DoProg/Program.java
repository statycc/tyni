package DoProg;


public class Program {

    public static void main(String[] args) {
        var c = example(100);
        System.out.println(c);
    }

    static protected int example(int n) {
        int r = 1, m = 2;
        do {
            m *= 2 + n;
            r += m;
            n--;
        } while (n > 0);
        return r;
    }
}
