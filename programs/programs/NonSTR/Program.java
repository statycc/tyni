package NonSTR;


public class Program {

    public static void main(String[] args) {
        int result = nonStr();
        System.out.println(result);
    }

    /**
     * [Hainry & Péchoux (2023)] This statement runs in polynomial time
     * and is non-interfering by setting, for example, Γ(x) = 1.
     * However, it is not stratified, as the reduction of assignment
     * x := x + 1; make the level-1 value increase.
     */
    static protected int nonStr() {
        int x = 0;
        while (x < 28) {
            x = x + 1;
        }
        return x;
    }
}
