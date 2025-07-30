<?php

// SHOULD BE DETECTED - Simple function
function simpleFunction($param) {
    // SHOULD NOT BE DETECTED - Function call
    echo "test";
    return $param;
}

// SHOULD BE DETECTED - Class method
class TestClass {
    public function publicMethod($value) {
        // SHOULD NOT BE DETECTED - Function call
        var_dump($value);
        return $value;
    }
}

// SHOULD NOT BE DETECTED - Function calls
simpleFunction("test");
$obj = new TestClass();
$obj->publicMethod(5);
echo "hello";
print "world";

?>