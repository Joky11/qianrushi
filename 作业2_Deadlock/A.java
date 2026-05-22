class A {
    synchronized void methodA(B b) {
        b.last();
    }

    synchronized void last() {
        System.out.println("Inside A.last()");
    }
}
