package switchmth;

import java.util.Scanner;

public class Program {

    public static void main(String[] args) {
        Scanner reader = new Scanner(System.in);
//         System.out.println("Welcome to CSCI 1301!");
//         System.out.println("Enter a number 1-12: ");
        int n = reader.nextInt();
        String m1 = month(n), m2 = m_exp(n);
//         assert (m1.equals(m2));
//         System.out.printf("Number %d as a month is %s.", n, m1);
    }

    @SuppressWarnings("EnhancedSwitchMigration")
    static protected String month(int n) {
        switch (n) {
            case 1: return "January";
            case 2: return "February";
            case 3: return "March";
            case 4: return "April";
            case 5: return "May";
            case 6: return "June";
            case 7: return "July";
            case 8: return "August";
            case 9: return "September";
            case 10: return "October";
            case 11: return "November";
            case 12: return "December";
            default: return "invalid";
        }
    }

//     static protected String m_exp(int n) {
//         String m = switch (n) {
//             case 1 -> "January";
//             case 2 -> "February";
//             case 3 -> "March";
//             case 4 -> "April";
//             case 5 -> "May";
//             case 6 -> "June";
//             case 7 -> "July";
//             case 8 -> "August";
//             case 9 -> "September";
//             case 10 -> "October";
//             case 11 -> "November";
//             case 12 -> "December";
//             default -> "invalid";
//         };
//         return m;
//     }
}
