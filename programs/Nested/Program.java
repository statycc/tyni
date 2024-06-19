package Nested;

public class Program {

    public static void main(String[] args) {
        List<Integer> initial = new List<>(1).add(2).add(3);
        System.out.println(initial); // expect: 1,2,3
        List<Integer> result = new Program().nested(initial);
        System.out.println(result); // 1,1,1,1,1,1,1,2,3
    }

    /**
     * [Hainry (2023)]  EXAMPLE 3.15: Nested loops
     * Adds a number n of new elements in a list, where n is equal
     * to the sum of the integers of the initial list.
     */
    protected List<Integer> nested(List<Integer> x) {
        int z;
        List<Integer> y = x;
        while (x != null) {
            z = x.head();
            while (z > 0) {
                y = new List<>(1, y);
                z = z - 1;
            }
            x = x.tail();
        }
        return y;
    }
}
