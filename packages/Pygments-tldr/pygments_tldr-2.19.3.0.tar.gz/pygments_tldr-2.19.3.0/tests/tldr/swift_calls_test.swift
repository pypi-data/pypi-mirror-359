// Only 1 function definition - should detect only this
func realFunction() {
    // Many function calls below - should NOT be detected
    print("test")
    debugPrint("hello")
    assert(true)
    "string".uppercased()
    "string".lowercased()
    "string".trimmingCharacters(in: .whitespaces)
    [1, 2, 3].forEach { print($0) }
    [1, 2, 3].map { $0 * 2 }
    [1, 2, 3].filter { $0 > 1 }
    Array(1...5)
    String("test")
    Data()
    Date()
    sqrt(16)
    max(1, 2)
}

// Function calls that should NOT be detected
realFunction()
print("output")
debugPrint("more output")
"test".uppercased()
[1, 2, 3].forEach { print($0) }