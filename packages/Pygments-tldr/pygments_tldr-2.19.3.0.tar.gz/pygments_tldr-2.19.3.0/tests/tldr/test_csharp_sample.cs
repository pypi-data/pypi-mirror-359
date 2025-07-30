using System;
using System.Collections.Generic;

namespace TestNamespace
{
    public class Calculator
    {
        // Method definitions - should be detected ✅
        public int Add(int a, int b)  // Should detect ✅
        {
            // Method calls - should NOT be detected ❌
            Console.WriteLine("Adding numbers");
            return Math.Max(a, b);  // Should NOT detect ❌
        }

        private static void StaticMethod()  // Should detect ✅
        {
            // Constructor calls - should NOT be detected ❌
            List<string> list = new List<string>();
            string str = new String("test");
            
            // Method calls - should NOT be detected ❌
            list.Add("item");
            str.ToString();
        }

        // Constructor - should be detected ✅
        public Calculator()  // Should detect ✅
        {
            this.Initialize();  // Should NOT detect ❌
        }

        // Property - might be detected depending on implementation
        public string Name { get; set; }

        // Async method - should be detected ✅
        public async Task<int> AsyncMethod()  // Should detect ✅
        {
            await Task.Delay(1000);  // Should NOT detect ❌
            return new Random().Next();  // Should NOT detect ❌
        }

        private void Initialize()  // Should detect ✅
        {
            // More method calls that should NOT be detected
            DateTime.Now.ToString();
            Convert.ToInt32("42");
        }
    }
}