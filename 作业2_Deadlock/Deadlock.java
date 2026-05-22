class Deadlock implements Runnable {
    A a = new A();
    B b = new B();

    Deadlock() {
        Thread t = new Thread(this);
        int count = 20000;

        t.start();
        while (count-- > 0);
        a.methodA(b);
    }

    public void run() {
        b.methodB(a);
    }

    public static void main(String args[]) {
        new Deadlock();
    }
}
