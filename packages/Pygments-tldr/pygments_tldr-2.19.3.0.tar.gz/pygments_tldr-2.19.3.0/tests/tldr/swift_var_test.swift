// Only function definitions - should detect only this
func realFunction() {
    return
}

// Variable assignments - should NOT be detected
let simpleVar = "hello"
var mutableVar = 42
let closure = { print("closure") }
let obj = TestClass()

// This specific pattern was causing issues:
let result = [1, 2, 3].map { $0 * 2 }