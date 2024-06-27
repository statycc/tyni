package switches;

import java.util.Scanner;

public class Program {

    public static void main(String[] args) {
        Scanner reader = new Scanner(System.in);
        System.out.println("Welcome to CSCI 1301!");
        System.out.println("Enter a number 1-12: ");
        int n = reader.nextInt();
        String m1 = month(n); //, m2 = m_exp(n);
        // assert (m1.equals(m2));
        System.out.printf("Number %d as a month is %s.", n, m1);
    }

    @SuppressWarnings({"UnnecessaryLocalVariable"})
    static protected String month(int n) {
        String mth;
        switch (n) {
             case 1: mth = "January"; break;
             case 2: { mth = "February"; break; }
             case 3: mth = "March"; break;
             case 4: mth = "April"; break;
             case 5: mth = "May"; break;
             case 6: mth = "June"; break;
             case 7: mth = "July"; break;
             case 8: { String temp = "August"; mth = temp; break; }
             case 9: mth = "September"; break;
             case 10: mth= "October"; break;
             case 11: mth= "November"; break;
             case 12: mth= "December"; break;
             case 13: case 14:
             default: return "invalid";
        }
        return mth;
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
