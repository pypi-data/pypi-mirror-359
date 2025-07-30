// SHOULD BE DETECTED - Function definitions
func regularFunction() {
    print("test")  // Should NOT be detected
}

func functionWithParams(name: String, age: Int) -> String {
    return "Hello \(name)"
}

class TestClass {
    init() {
        // Should NOT be detected - method calls
        print("initializing")
    }
    
    func instanceMethod() {
        // Should NOT be detected - method calls
        self.anotherMethod()
    }
    
    static func staticMethod() -> Int {
        return 42
    }
}

// SHOULD NOT BE DETECTED - Variable assignments with closures
let simpleClosure = { print("hello") }
let closureWithParams = { (x: Int) in return x * 2 }
let result = [1, 2, 3].map { $0 * 2 }
let filtered = [1, 2, 3].filter { $0 > 1 }

// SHOULD NOT BE DETECTED - Function calls
regularFunction()
functionWithParams(name: "John", age: 30)
print("output")
TestClass.staticMethod()

// SHOULD NOT BE DETECTED - Method chaining
"hello".uppercased().lowercased()
[1, 2, 3].map { $0 * 2 }.filter { $0 > 2 }

// SHOULD NOT BE DETECTED - Constructor calls
let obj = TestClass()
let array = Array(1...5)
let string = String("test")