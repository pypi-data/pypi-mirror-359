// SHOULD BE DETECTED - Function definitions
func simpleFunction() {
    print("test")  // Should NOT be detected - function call
    return
}

func functionWithParams(name: String, age: Int) -> String {
    print(name)  // Should NOT be detected - function call
    return "Hello \(name)"
}

class TestClass {
    func instanceMethod() {
        print("instance")  // Should NOT be detected - function call
    }
    
    static func staticMethod() {
        print("static")  // Should NOT be detected - function call
    }
}

// SHOULD NOT BE DETECTED - Function calls
simpleFunction()
functionWithParams(name: "John", age: 30)
print("hello")
debugPrint("world")

let obj = TestClass()
obj.instanceMethod()
TestClass.staticMethod()

// More function calls that should NOT be detected
"hello".uppercased()
[1, 2, 3].map { $0 * 2 }
Array(1...5)
String("test")