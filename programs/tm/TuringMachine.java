package tm;

@SuppressWarnings("ALL")
public class TuringMachine {

    /**
     * [Hainry & Péchoux (2023)] Sect. 4.4 (p. 17 - 18): STR is undecidable.
     * Encode deterministic one-tape TMs...
     * Program can be typed in NI by setting Γ(s) = Γ(left) = Γ(right) ≜ 1 and
     * checking that Γ ⊢NI true : 2 can be derived.
     * Program is not in STR, as the statement st(l) breaks the noninterference
     * (s increases in a loop guarded by itself).
     *
     * @return
     */
    public int run(boolean ctrl) {
        s = 0;
        right = 0;
        left = tape.length - 1;
        while (ctrl) {
            trans();
            if (s == 1) {
                while (s > 0) {
                    s = s + 1;  // st(l)
                }
            }
        }
         return s;
    }

    private int s;
    private int left;
    private int right;
    private final boolean[] tape = new boolean[100];

    private int head(int pos) {
        return !tape[pos] ? 0 : 1;
    }

    private int cons(int val, int pos) {
        tape[pos] = val != 0;
        return pos - 1;
    }

    private void trans() {
        if (s == 5 && head(right) == 0) {
            s = 6;
            left = cons(1, left);
            right = right + 1;
        }
    }
}

