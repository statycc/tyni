package ImplicitFlowSimple;

public class Program {

    public static void main(String[] args) {
        boolean result = implicit(args != null);
        System.out.println(result);
    }

    /**
     * [Volpano (1996) p. 5] 2-variable implicit flow.
     * There is an implicit flow because high is indirectly copied to low.
     * Since information of the condition variable level (high) is implicitly known, the branches
     * must assign to variables of level high.
     */
    static protected boolean implicit(boolean high) {
        boolean low;
        if (high) {
            low = true;
        } else{
            low = false;
        }
        return low;
    }
}
