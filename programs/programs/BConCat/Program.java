package BConCat;

public class Program {

    public static void main(String[] args) {
        List<Integer> initial = new List<>(3).add(2).add(1);
        System.out.println(initial); // expect: 1,2,3
        List<Integer> result = new Program().bconcat(initial, 2);
        System.out.println(result); // expect: 2,1,1,2,3
    }

    /**
     * [Hainry & Péchoux (2023)] EXAMPLE 3.14: Bounded concatenation
     * concatenates two lists given as input up to some fixed bound.
     * <p>
     * The judgment Γ ⊢NI bconcat : 1 can be derived for the typing
     * environment Γ defined by Γ(x) = Γ(w) ≜ 1 and Γ(y) = Γ(z) ≜ 0.
     * Hence bconcat ∈ NIΓ.
     */
    protected List<Integer> bconcat(List<Integer> x, int w) {
        int z;
        List<Integer> y = x;
        while (x != null && w > 0) {
            z = x.head();
            y = new List<>(z, y);
            w = w - 1;
            x = x.tail();
        }
        return y;
    }
}

