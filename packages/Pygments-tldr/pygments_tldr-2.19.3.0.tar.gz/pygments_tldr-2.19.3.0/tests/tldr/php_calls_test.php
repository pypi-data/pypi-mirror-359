<?php

// Only 1 function definition - should detect only this
function realFunction() {
    // Many function calls below - should NOT be detected
    echo "test";
    print "hello";
    var_dump($data);
    json_encode($array);
    file_get_contents("file.txt");
    array_push($arr, $value);
    strlen($string);
    preg_match($pattern, $subject);
    count($items);
    isset($variable);
    empty($array);
    unset($var);
    header("Content-Type: text/html");
    die("error");
    exit(1);
}

// Function calls that should NOT be detected
realFunction();
echo "output";
print "more output";
var_dump($someData);

?>