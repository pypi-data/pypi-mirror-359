public class Simple 
{
    public void Method() // Should detect ✅
    {
        Console.WriteLine("test"); // Should NOT detect ❌
        new List<string>(); // Should NOT detect ❌
    }
    
    public Simple() // Should detect ✅
    {
        Method(); // Should NOT detect ❌
    }
}