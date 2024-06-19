package SqlInjection;

public class Program {

    public static void main(String[] args) {
        example("secret");
    }

    static protected void example(String request) {
        String user = request;
        String sb1 = "SELECT * FROM Users WHERE name=";
        String sb2 = "SELECT * FROM Users WHERE name=";
        sb1 = sb1 + user;
        sb2 = sb2 + "John";
        String query = sb2;
        System.out.println(query);
    }
}
