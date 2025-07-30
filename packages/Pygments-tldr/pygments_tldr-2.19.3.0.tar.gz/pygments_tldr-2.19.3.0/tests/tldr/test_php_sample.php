<?php
// ========================================
// PHP Test File for TLDR Formatter
// This file tests various PHP patterns to verify correct function detection
// ========================================

// SHOULD BE DETECTED - Regular function definition
function regularFunction($param1, $param2) {
    return $param1 + $param2;
}

// SHOULD BE DETECTED - Function with return type
function typedFunction(int $a, string $b): string {
    return $b . $a;
}

// SHOULD BE DETECTED - Function with nullable parameter
function nullableFunction(?string $name = null): void {
    if ($name) {
        echo "Hello, $name!";
    }
}

// SHOULD BE DETECTED - Function with reference parameter
function referenceFunction(&$value) {
    $value = $value * 2;
}

// SHOULD BE DETECTED - Function with variadic parameters
function variadicFunction(...$args) {
    return array_sum($args);
}

// Class definitions with methods
class TestClass {
    private $property;
    
    // SHOULD BE DETECTED - Constructor method
    public function __construct($value) {
        $this->property = $value;
    }
    
    // SHOULD BE DETECTED - Magic method
    public function __toString() {
        return (string) $this->property;
    }
    
    // SHOULD BE DETECTED - Public method
    public function publicMethod($param) {
        return $param * 2;
    }
    
    // SHOULD BE DETECTED - Private method
    private function privateMethod() {
        return $this->property;
    }
    
    // SHOULD BE DETECTED - Protected method
    protected function protectedMethod() {
        return true;
    }
    
    // SHOULD BE DETECTED - Static method
    public static function staticMethod($value) {
        return $value * 3;
    }
    
    // SHOULD BE DETECTED - Final method
    final public function finalMethod() {
        return "final";
    }
    
    // SHOULD BE DETECTED - Abstract method in abstract class
    // abstract public function abstractMethod();
    
    // SHOULD BE DETECTED - Method with multiple modifiers
    final protected static function complexMethod() {
        return "complex";
    }
}

// Abstract class with abstract method
abstract class AbstractClass {
    // SHOULD BE DETECTED - Abstract method
    abstract public function abstractMethod($param);
    
    // SHOULD BE DETECTED - Concrete method in abstract class
    public function concreteMethod() {
        return "concrete";
    }
}

// Interface with method declarations
interface TestInterface {
    // SHOULD BE DETECTED - Interface method
    public function interfaceMethod($param);
    
    // SHOULD BE DETECTED - Interface method with return type
    public function typedInterfaceMethod(string $param): bool;
}

// Trait with methods
trait TestTrait {
    // SHOULD BE DETECTED - Trait method
    public function traitMethod() {
        return "trait";
    }
    
    // SHOULD BE DETECTED - Private trait method
    private function privateTraitMethod() {
        return "private trait";
    }
}

// ========================================
// SHOULD BE DETECTED - Anonymous functions and closures
// ========================================

// Anonymous function assigned to variable
$anonymousFunction = function($x, $y) {
    return $x + $y;
};

// Closure with use clause
$closure = function($multiplier) use ($someVariable) {
    return $someVariable * $multiplier;
};

// Arrow function (PHP 7.4+)
$arrowFunction = fn($x) => $x * 2;

// Callback function passed to array_map
$result = array_map(function($item) {
    return $item * 2;
}, [1, 2, 3]);

// ========================================
// SHOULD NOT BE DETECTED - Function calls
// ========================================

// Built-in function calls
echo "Hello World";
print "Another output";
var_dump($someVariable);
isset($variable);
empty($array);
count($items);
strlen($string);
array_push($array, $value);
array_pop($array);
json_encode($data);
file_get_contents($filename);
preg_match($pattern, $subject);
header('Content-Type: application/json');
die('Error occurred');
exit(1);
unset($variable);

// User-defined function calls
regularFunction(1, 2);
typedFunction(5, "test");
nullableFunction("John");
referenceFunction($myValue);
variadicFunction(1, 2, 3, 4, 5);

// Method calls on objects
$obj = new TestClass(10);
$obj->publicMethod(5);
$obj->__toString();

// Static method calls
TestClass::staticMethod(7);
AbstractClass::concreteMethod();

// Chained method calls
$obj->publicMethod(5)->anotherMethod()->finalMethod();

// Function calls with complex expressions
call_user_func('regularFunction', 1, 2);
call_user_func_array('variadicFunction', [1, 2, 3]);
$callback = 'regularFunction';
$callback(1, 2);

// Function calls in conditions
if (function_exists('regularFunction')) {
    regularFunction(1, 2);
}

// Function calls in loops
foreach (range(1, 10) as $i) {
    echo $i;
}

// Function calls in arrays
$functions = [
    'first' => 'regularFunction',
    'second' => 'typedFunction'
];

// Lambda/anonymous function calls
$anonymousFunction(5, 10);
$closure(3);
$arrowFunction(4);

// ========================================
// EDGE CASES AND COMPLEX PATTERNS
// ========================================

// Nested function definitions (should both be detected)
function outerFunction() {
    function innerFunction() {
        return "inner";
    }
    return innerFunction();
}

// Function with heredoc
function heredocFunction() {
    return <<<EOD
This is a heredoc string
with multiple lines
EOD;
}

// Function with nowdoc
function nowdocFunction() {
    return <<<'EOD'
This is a nowdoc string
with multiple lines
EOD;
}

// Function in conditional
if (true) {
    function conditionalFunction() {
        return "conditional";
    }
}

// Function with complex default values
function complexDefaultFunction($param = ['key' => 'value'], $callback = null) {
    return $param;
}

// Function with type union (PHP 8.0+)
function unionTypeFunction(int|string $value): int|string {
    return $value;
}

// Function with named parameters usage (this is a call, not definition)
complexDefaultFunction(param: ['test' => 'value'], callback: function() { return true; });

// ========================================
// COMMENTS AND STRINGS CONTAINING FUNCTION KEYWORDS
// ========================================

// This comment mentions "function" but should not be detected
/* This is a multi-line comment with the word function */

echo "This string contains the word function but should not be detected";
echo 'Another string with function keyword';

$string = "
function fakeFunction() {
    return 'this is in a string';
}
";

// ========================================
// NAMESPACE AND USE STATEMENTS
// ========================================

namespace MyNamespace;

use SomeNamespace\SomeClass;
use function SomeNamespace\someFunction;

// SHOULD BE DETECTED - Function in namespace
function namespacedFunction() {
    return "namespaced";
}

// ========================================
// REGEX PATTERNS AND PREG FUNCTIONS
// ========================================

// These are function calls, not definitions
preg_match('/function\s+(\w+)/', $code, $matches);
preg_replace('/function/', 'method', $text);
preg_split('/\s+/', $text);

// ========================================
// VARIABLE FUNCTIONS AND DYNAMIC CALLS
// ========================================

$functionName = 'regularFunction';
$functionName(1, 2); // Dynamic function call

$obj = new TestClass(5);
$methodName = 'publicMethod';
$obj->$methodName(10); // Dynamic method call

// ========================================
// REFLECTION AND MAGIC METHODS
// ========================================

// These are calls to reflection methods
$reflection = new ReflectionFunction('regularFunction');
$reflection->invoke(1, 2);

$classReflection = new ReflectionClass('TestClass');
$method = $classReflection->getMethod('publicMethod');

// ========================================
// CLOSURES AND CALLBACKS IN VARIOUS CONTEXTS
// ========================================

// Array functions with closures
array_filter($array, function($item) {
    return $item > 5;
});

array_reduce($array, function($carry, $item) {
    return $carry + $item;
}, 0);

usort($array, function($a, $b) {
    return $a <=> $b;
});

// ========================================
// GENERATOR FUNCTIONS
// ========================================

// SHOULD BE DETECTED - Generator function
function generatorFunction() {
    yield 1;
    yield 2;
    yield 3;
}

// SHOULD BE DETECTED - Generator with key-value pairs
function keyValueGenerator() {
    yield 'key1' => 'value1';
    yield 'key2' => 'value2';
}

// ========================================
// FUNCTION CALLS IN DIFFERENT CONTEXTS
// ========================================

// Function calls in array initialization
$array = [
    'result1' => regularFunction(1, 2),
    'result2' => TestClass::staticMethod(5),
    'result3' => $obj->publicMethod(3)
];

// Function calls in switch statements
switch (regularFunction(1, 2)) {
    case 3:
        echo "Three";
        break;
    default:
        echo "Other";
}

// Function calls in try-catch
try {
    regularFunction(1, 2);
} catch (Exception $e) {
    error_log($e->getMessage());
}

// Function calls in ternary operator
$result = true ? regularFunction(1, 2) : typedFunction(5, "test");

// Function calls in null coalescing
$result = $maybeNull ?? regularFunction(1, 2);

?>