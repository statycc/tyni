package Rev;

class List<E> {
    private final E value;
    private List<E> next;

    public List(E value) {
        this.value = value;
    }

    public List<E> add(E value) {
        return new List<E>(value, this);
    }

    public List(E value, List<E> next) {
        this.value = value;
        this.next = next;
    }

    public E head() {
        return value;
    }

    public List<E> tail() {
        return next;
    }

    public void tail(List<E> next) {
        this.next = next;
    }

    @Override
    public String toString() {
        return head().toString() + (next == null ? "" : ("," + next));
    }
}
