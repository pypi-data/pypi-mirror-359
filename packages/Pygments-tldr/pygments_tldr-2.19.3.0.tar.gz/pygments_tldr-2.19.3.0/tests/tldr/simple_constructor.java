public class Simple {
    public Simple() {
        System.out.println("constructor");
    }
    
    public void method() {
        new Simple(); // Should NOT detect
    }
}