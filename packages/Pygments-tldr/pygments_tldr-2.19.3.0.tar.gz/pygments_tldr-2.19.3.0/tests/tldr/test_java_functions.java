public class TestJavaFunctions {
    
    // Method definitions - should be detected ✅
    public void publicMethod() {  // Should detect ✅
        // Constructor calls - should NOT be detected ❌
        List<String> list = new ArrayList<>();
        String str = new String("test");
        
        // Method calls - should NOT be detected ❌
        list.add("item");
        str.toString();
        System.out.println("test");
    }
    
    private static int staticMethod(String param) {  // Should detect ✅
        return param.length(); // Method call - should NOT detect ❌
    }
    
    protected final boolean finalMethod() {  // Should detect ✅
        return new Boolean(true); // Constructor call - should NOT detect ❌
    }
    
    // Constructor definition - should be detected ✅ 
    public TestJavaFunctions() {  // Should detect ✅
        this.initialize(); // Method call - should NOT detect ❌
    }
    
    // Inner class
    static class InnerClass {
        void innerMethod() {  // Should detect ✅
            new InnerClass(); // Constructor call - should NOT detect ❌
        }
    }
    
    // Generic method
    public <T> T genericMethod(T param) {  // Should detect ✅
        return param;
    }
    
    // Abstract method declaration (if this were abstract)
    // abstract void abstractMethod();  // Should detect ✅
    
    private void initialize() {  // Should detect ✅
        // More constructor calls and method calls
        Map<String, Integer> map = new HashMap<>();
        map.put("key", new Integer(42));
        map.get("key");
    }
}