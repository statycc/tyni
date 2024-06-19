package TM;

@SuppressWarnings("ALL")
public class Program {

    public static void main(String[] args) {
        int result = new TuringMachine().run(true);
        System.out.println(result);
    }
}
