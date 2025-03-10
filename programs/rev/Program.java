package rev;

@SuppressWarnings({"UnusedAssignment", "SuspiciousNameCombination"})
public class Program {

    public static void main(String[] args) {
        List<Integer> initial = new List<>(1).add(2).add(3);
        System.out.println(initial); // expect: 1,2,3
        List<Integer> result = new Program().rev(initial);
        System.out.println(result); // expect: 3,2,1
    }

    /**
     * [Hainry & Péchoux (2023)] EXAMPLE 2.1: List reversal
     * rev is a non-interfering program in NI,
     * for the typing assignment Γ(x) ≜ 1 and Γ(y) = Γ(z) ≜ 0.
     * rev cannot be typed wrt a typing environment Γ
     * such that Γ(x) = 0 or Γ(x) ≺ Γ(y).
     */
    protected List<Integer> rev(List<Integer> x) {
        List<Integer> y = null;
        List<Integer> z = null;
        while (x != null) {
            z = y;
            y = x;
            x = x.tail();
            y.tail(z);
        }
        z = null;
        return y;
    }
}
