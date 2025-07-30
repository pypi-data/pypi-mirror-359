// Swift Test File for TLDR Formatter Function Detection
// This file tests whether the TLDR formatter correctly identifies only function definitions
// and not function calls, method calls, or other patterns that should be ignored.

import Foundation
import UIKit

// =============================================================================
// SECTION 1: FUNCTION DEFINITIONS (SHOULD BE DETECTED)
// =============================================================================

// Global function definitions
func simpleFunction() {
    print("This is a simple function") // print() is a CALL, not a definition
}

func functionWithParameters(name: String, age: Int) -> String {
    return "Name: \(name), Age: \(age)"
}

func functionWithGenericParameters<T>(value: T) -> T {
    return value
}

func functionWithInoutParameter(value: inout Int) {
    value += 1
}

func functionWithVariadicParameters(numbers: Int...) -> Int {
    return numbers.reduce(0, +) // reduce is a CALL, not a definition
}

func functionWithThrows() throws -> String {
    throw SampleError.invalidInput
}

func functionWithAsync() async -> String {
    await Task.sleep(nanoseconds: 1000000) // Task.sleep is a CALL
    return "async result"
}

func functionWithAsyncThrows() async throws -> String {
    return "async throws result"
}

// =============================================================================
// SECTION 2: STRUCT DEFINITIONS WITH METHODS (SHOULD BE DETECTED)
// =============================================================================

struct Person {
    let name: String
    var age: Int
    
    // Initializer - SHOULD BE DETECTED
    init(name: String, age: Int) {
        self.name = name
        self.age = age
        // String() below is a CALL, not a definition
        let greeting = String(format: "Hello %@", name)
        print(greeting) // print() is a CALL
    }
    
    // Convenience initializer - SHOULD BE DETECTED
    init(name: String) {
        self.init(name: name, age: 0) // self.init() is a CALL
    }
    
    // Instance method - SHOULD BE DETECTED  
    func greet() -> String {
        return "Hello, I'm \(name)"
    }
    
    // Mutating method - SHOULD BE DETECTED
    mutating func celebrateBirthday() {
        age += 1
        print("Happy birthday!") // print() is a CALL
    }
    
    // Static method - SHOULD BE DETECTED
    static func createDefault() -> Person {
        return Person(name: "Default", age: 0) // Person() is a CALL
    }
    
    // Computed property getter - SHOULD BE DETECTED
    var description: String {
        get {
            return "Person: \(name), Age: \(age)"
        }
    }
    
    // Computed property with getter and setter - SHOULD BE DETECTED
    var displayAge: Int {
        get {
            return age
        }
        set {
            age = max(0, newValue) // max() is a CALL
        }
    }
}

// =============================================================================
// SECTION 3: CLASS DEFINITIONS WITH METHODS (SHOULD BE DETECTED)
// =============================================================================

class Vehicle {
    let brand: String
    var speed: Double
    
    // Class initializer - SHOULD BE DETECTED
    init(brand: String, speed: Double = 0.0) {
        self.brand = brand
        self.speed = speed
    }
    
    // Convenience initializer - SHOULD BE DETECTED
    convenience init(brand: String) {
        self.init(brand: brand, speed: 0.0) // self.init() is a CALL
    }
    
    // Instance method - SHOULD BE DETECTED
    func accelerate(by amount: Double) {
        speed += amount
        print("Accelerating...") // print() is a CALL
    }
    
    // Virtual method - SHOULD BE DETECTED
    func start() {
        print("Vehicle starting") // print() is a CALL
    }
    
    // Class method - SHOULD BE DETECTED
    class func maxSpeed() -> Double {
        return 200.0
    }
    
    // Static method - SHOULD BE DETECTED
    static func manufacturerInfo() -> String {
        return "Generic Vehicle Manufacturer"
    }
    
    // Final method - SHOULD BE DETECTED
    final func serialNumber() -> String {
        return UUID().uuidString // UUID() is a CALL
    }
    
    // Private method - SHOULD BE DETECTED
    private func validateSpeed() -> Bool {
        return speed >= 0
    }
    
    // Deinitializer - SHOULD BE DETECTED
    deinit {
        print("Vehicle deallocated") // print() is a CALL
    }
}

// Subclass
class Car: Vehicle {
    let numberOfWheels: Int
    
    // Override initializer - SHOULD BE DETECTED
    override init(brand: String, speed: Double = 0.0) {
        self.numberOfWheels = 4
        super.init(brand: brand, speed: speed) // super.init() is a CALL
    }
    
    // Override method - SHOULD BE DETECTED
    override func start() {
        super.start() // super.start() is a CALL
        print("Car engine started") // print() is a CALL
    }
    
    // Subscript - SHOULD BE DETECTED
    subscript(index: Int) -> String {
        get {
            return "Wheel \(index)"
        }
        set {
            print("Setting wheel \(index) to \(newValue)") // print() is a CALL
        }
    }
}

// =============================================================================
// SECTION 4: PROTOCOL DEFINITIONS (SHOULD BE DETECTED)
// =============================================================================

protocol Drawable {
    // Protocol method requirements - SHOULD BE DETECTED
    func draw()
    func area() -> Double
    
    // Protocol property requirements - SHOULD BE DETECTED
    var color: String { get set }
    var isVisible: Bool { get }
}

protocol Movable {
    // Protocol method with mutating - SHOULD BE DETECTED
    mutating func move(to point: CGPoint)
    
    // Protocol method with parameters - SHOULD BE DETECTED
    func canMoveTo(point: CGPoint) -> Bool
}

// =============================================================================
// SECTION 5: EXTENSION DEFINITIONS (SHOULD BE DETECTED)
// =============================================================================

extension String {
    // Extension method - SHOULD BE DETECTED
    func isValidEmail() -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        return NSPredicate(format: "SELF MATCHES %@", emailRegex).evaluate(with: self)
        // NSPredicate() is a CALL
    }
    
    // Extension computed property - SHOULD BE DETECTED
    var wordCount: Int {
        return self.components(separatedBy: .whitespaces).count
        // components() is a CALL
    }
    
    // Extension subscript - SHOULD BE DETECTED
    subscript(safe index: Int) -> Character? {
        guard index >= 0 && index < count else { return nil }
        return self[self.index(startIndex, offsetBy: index)]
        // self.index() is a CALL
    }
}

// =============================================================================
// SECTION 6: ENUM DEFINITIONS (SHOULD BE DETECTED)
// =============================================================================

enum Direction {
    case north, south, east, west
    
    // Enum method - SHOULD BE DETECTED
    func opposite() -> Direction {
        switch self {
        case .north: return .south
        case .south: return .north
        case .east: return .west
        case .west: return .east
        }
    }
    
    // Enum static method - SHOULD BE DETECTED
    static func random() -> Direction {
        let directions: [Direction] = [.north, .south, .east, .west]
        return directions.randomElement() ?? .north // randomElement() is a CALL
    }
    
    // Enum computed property - SHOULD BE DETECTED
    var description: String {
        switch self {
        case .north: return "North"
        case .south: return "South"
        case .east: return "East"
        case .west: return "West"
        }
    }
}

// =============================================================================
// SECTION 7: GENERIC DEFINITIONS (SHOULD BE DETECTED)
// =============================================================================

// Generic function - SHOULD BE DETECTED
func swapValues<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

// Generic struct - SHOULD BE DETECTED
struct Stack<Element> {
    private var items: [Element] = []
    
    // Generic method - SHOULD BE DETECTED
    mutating func push(_ item: Element) {
        items.append(item) // append() is a CALL
    }
    
    // Generic method - SHOULD BE DETECTED
    mutating func pop() -> Element? {
        return items.popLast() // popLast() is a CALL
    }
    
    // Generic computed property - SHOULD BE DETECTED
    var count: Int {
        return items.count
    }
}

// =============================================================================
// SECTION 8: CLOSURES AND FUNCTION TYPES (SHOULD BE DETECTED)
// =============================================================================

// Function that takes closure - SHOULD BE DETECTED
func performOperation(on value: Int, operation: (Int) -> Int) -> Int {
    return operation(value) // operation() is a CALL
}

// Function that returns closure - SHOULD BE DETECTED
func createMultiplier(factor: Int) -> (Int) -> Int {
    return { number in
        return number * factor
    }
}

// =============================================================================
// SECTION 9: PROPERTY WRAPPERS (SHOULD BE DETECTED)
// =============================================================================

@propertyWrapper
struct Capitalized {
    private var value: String = ""
    
    // Property wrapper getter/setter - SHOULD BE DETECTED
    var wrappedValue: String {
        get { return value }
        set { value = newValue.capitalized } // capitalized is a CALL
    }
    
    // Property wrapper initializer - SHOULD BE DETECTED
    init(wrappedValue: String) {
        self.value = wrappedValue.capitalized // capitalized is a CALL
    }
}

// =============================================================================
// SECTION 10: OPERATOR OVERLOADING (SHOULD BE DETECTED)
// =============================================================================

// Operator overloading - SHOULD BE DETECTED
func +(left: Person, right: Person) -> [Person] {
    return [left, right]
}

// Operator overloading - SHOULD BE DETECTED
func ==(left: Person, right: Person) -> Bool {
    return left.name == right.name && left.age == right.age
}

// =============================================================================
// SECTION 11: FUNCTION CALLS AND METHOD CALLS (SHOULD NOT BE DETECTED)
// =============================================================================

// This section contains examples of function calls, method calls, and other patterns
// that should NOT be detected as function definitions by the TLDR formatter

func demonstrateFunctionCalls() {
    // Built-in function calls - SHOULD NOT BE DETECTED
    print("Hello World")
    debugPrint("Debug message")
    assert(true, "This should pass")
    precondition(true, "This should pass")
    
    // Standard library function calls - SHOULD NOT BE DETECTED
    let numbers = Array(1...10)
    let doubled = numbers.map { $0 * 2 }
    let filtered = numbers.filter { $0 > 5 }
    let sum = numbers.reduce(0, +)
    
    // String function calls - SHOULD NOT BE DETECTED
    let text = "Hello World"
    let uppercase = text.uppercased()
    let lowercase = text.lowercased()
    let trimmed = text.trimmingCharacters(in: .whitespaces)
    
    // Collection method calls - SHOULD NOT BE DETECTED
    var mutableArray = [1, 2, 3]
    mutableArray.append(4)
    mutableArray.insert(0, at: 0)
    mutableArray.remove(at: 1)
    
    // Dictionary method calls - SHOULD NOT BE DETECTED
    var dictionary = ["key": "value"]
    dictionary.updateValue("newValue", forKey: "key")
    let value = dictionary.removeValue(forKey: "key")
    
    // Set method calls - SHOULD NOT BE DETECTED
    var numberSet = Set([1, 2, 3])
    numberSet.insert(4)
    numberSet.remove(1)
    let contains = numberSet.contains(2)
    
    // Class instantiation - SHOULD NOT BE DETECTED
    let person = Person(name: "John", age: 25)
    let car = Car(brand: "Toyota")
    let vehicle = Vehicle(brand: "Generic")
    
    // Method calls on instances - SHOULD NOT BE DETECTED
    let greeting = person.greet()
    car.accelerate(by: 10.0)
    vehicle.start()
    
    // Static method calls - SHOULD NOT BE DETECTED
    let defaultPerson = Person.createDefault()
    let maxSpeed = Vehicle.maxSpeed()
    let manufacturerInfo = Vehicle.manufacturerInfo()
    
    // Chained method calls - SHOULD NOT BE DETECTED
    let result = "  hello world  "
        .trimmingCharacters(in: .whitespaces)
        .uppercased()
        .replacingOccurrences(of: "WORLD", with: "SWIFT")
    
    // Closure calls - SHOULD NOT BE DETECTED
    let multiplier = createMultiplier(factor: 2)
    let doubled = multiplier(5)
    
    // Foundation framework calls - SHOULD NOT BE DETECTED
    let url = URL(string: "https://example.com")
    let data = Data()
    let date = Date()
    let uuid = UUID()
    
    // Core Graphics calls - SHOULD NOT BE DETECTED
    let point = CGPoint(x: 10, y: 20)
    let size = CGSize(width: 100, height: 200)
    let rect = CGRect(origin: point, size: size)
    
    // Math function calls - SHOULD NOT BE DETECTED
    let sqrt = sqrt(16.0)
    let pow = pow(2.0, 3.0)
    let abs = abs(-5)
    let min = min(5, 10)
    let max = max(5, 10)
    
    // String interpolation with function calls - SHOULD NOT BE DETECTED
    let message = "Square root of 16 is \(sqrt(16.0))"
    let info = "Person: \(person.greet())"
    
    // Conditional function calls - SHOULD NOT BE DETECTED
    if person.age > 18 {
        print("Adult")
    } else {
        print("Minor")
    }
    
    // Loop with function calls - SHOULD NOT BE DETECTED
    for i in 1...5 {
        print("Number: \(i)")
    }
    
    // Switch with function calls - SHOULD NOT BE DETECTED
    switch person.age {
    case 0...17:
        print("Minor")
    case 18...65:
        print("Adult")
    default:
        print("Senior")
    }
    
    // Guard with function calls - SHOULD NOT BE DETECTED
    guard person.age > 0 else {
        print("Invalid age")
        return
    }
    
    // Defer with function calls - SHOULD NOT BE DETECTED
    defer {
        print("Cleanup")
    }
}

// =============================================================================
// SECTION 12: ASYNC/AWAIT PATTERNS (SHOULD BE DETECTED FOR DEFINITIONS ONLY)
// =============================================================================

// Async function definition - SHOULD BE DETECTED
func fetchUserData() async throws -> String {
    // Async function calls - SHOULD NOT BE DETECTED
    let data = await URLSession.shared.data(for: URLRequest(url: URL(string: "https://api.example.com")!))
    return String(data: data.0, encoding: .utf8) ?? ""
}

// Function with async calls - SHOULD BE DETECTED (the function itself)
func processUserData() async {
    // These are calls, not definitions - SHOULD NOT BE DETECTED
    do {
        let userData = try await fetchUserData()
        print("User data: \(userData)")
    } catch {
        print("Error: \(error)")
    }
}

// =============================================================================
// SECTION 13: COMPLEX NESTED PATTERNS
// =============================================================================

// Complex function with nested patterns - SHOULD BE DETECTED
func complexFunction() {
    // Nested closure - the closure itself is NOT a named function definition
    let numbers = [1, 2, 3, 4, 5]
    
    // Method calls with closures - SHOULD NOT BE DETECTED
    let mapped = numbers.map { number in
        return number * 2
    }
    
    let filtered = numbers.filter { $0 > 3 }
    
    // Completion handler calls - SHOULD NOT BE DETECTED
    performOperation(on: 10) { value in
        return value * 2
    }
    
    // Nested function definition - SHOULD BE DETECTED
    func nestedFunction() {
        print("This is a nested function")
    }
    
    // Call to nested function - SHOULD NOT BE DETECTED
    nestedFunction()
}

// =============================================================================
// SECTION 14: ERROR HANDLING
// =============================================================================

enum SampleError: Error {
    case invalidInput
    case networkError
    case processingError
    
    // Error method - SHOULD BE DETECTED
    func description() -> String {
        switch self {
        case .invalidInput:
            return "Invalid input provided"
        case .networkError:
            return "Network error occurred"
        case .processingError:
            return "Processing error occurred"
        }
    }
}

// Function that handles errors - SHOULD BE DETECTED
func handleErrors() {
    do {
        // Function calls that might throw - SHOULD NOT BE DETECTED
        try functionWithThrows()
    } catch SampleError.invalidInput {
        print("Invalid input error")
    } catch {
        print("Other error: \(error)")
    }
}

// =============================================================================
// SUMMARY OF EXPECTATIONS
// =============================================================================

/*
FUNCTION DEFINITIONS THAT SHOULD BE DETECTED:
- simpleFunction
- functionWithParameters
- functionWithGenericParameters
- functionWithInoutParameter
- functionWithVariadicParameters
- functionWithThrows
- functionWithAsync
- functionWithAsyncThrows
- Person.init (multiple)
- Person.greet
- Person.celebrateBirthday
- Person.createDefault
- Person.description (getter)
- Person.displayAge (getter/setter)
- Vehicle.init (multiple)
- Vehicle.accelerate
- Vehicle.start
- Vehicle.maxSpeed
- Vehicle.manufacturerInfo
- Vehicle.serialNumber
- Vehicle.validateSpeed
- Vehicle.deinit
- Car.init
- Car.start
- Car.subscript
- Drawable.draw
- Drawable.area
- Drawable.color
- Drawable.isVisible
- Movable.move
- Movable.canMoveTo
- String.isValidEmail
- String.wordCount
- String.subscript
- Direction.opposite
- Direction.random
- Direction.description
- swapValues
- Stack.push
- Stack.pop
- Stack.count
- performOperation
- createMultiplier
- Capitalized.wrappedValue
- Capitalized.init
- + (operator)
- == (operator)
- demonstrateFunctionCalls
- fetchUserData
- processUserData
- complexFunction
- nestedFunction (inside complexFunction)
- SampleError.description
- handleErrors

FUNCTION CALLS THAT SHOULD NOT BE DETECTED:
- print()
- debugPrint()
- assert()
- precondition()
- Array()
- map()
- filter()
- reduce()
- uppercased()
- lowercased()
- trimmingCharacters()
- append()
- insert()
- remove()
- updateValue()
- removeValue()
- contains()
- Person() (constructor calls)
- Car() (constructor calls)
- Vehicle() (constructor calls)
- greet() (method calls)
- accelerate() (method calls)
- start() (method calls)
- createDefault() (static method calls)
- maxSpeed() (class method calls)
- manufacturerInfo() (static method calls)
- replacingOccurrences()
- URL()
- Data()
- Date()
- UUID()
- CGPoint()
- CGSize()
- CGRect()
- sqrt()
- pow()
- abs()
- min()
- max()
- URLSession.shared.data()
- String(data:encoding:)
- fetchUserData() (async call)
- nestedFunction() (call to nested function)
- functionWithThrows() (function call in do-catch)
*/