package main

import (
	"fmt"
	"strings"
	"time"
)

// Function definitions - should be detected ✅
func add(a, b int) int {  // Should detect ✅
	// Function calls - should NOT be detected ❌
	fmt.Printf("Adding %d and %d\n", a, b)  // Should NOT detect ❌
	return a + b
}

func publicFunction() string {  // Should detect ✅
	// More function calls that should NOT be detected
	return strings.ToUpper("hello")  // Should NOT detect ❌
}

func processData(data []int) []int {  // Should detect ✅
	var result []int
	for _, v := range data {
		// Function calls - should NOT be detected
		result = append(result, v*2)  // Should NOT detect ❌
	}
	return result
}

// Struct with methods
type Calculator struct {
	value int
}

// Method with receiver - should be detected ✅
func (c *Calculator) Add(x int) {  // Should detect ✅
	c.value += x
}

// Method with receiver - should be detected ✅
func (c Calculator) GetValue() int {  // Should detect ✅
	// Method calls that should NOT be detected
	time.Sleep(time.Millisecond)  // Should NOT detect ❌
	return c.value
}

// Interface
type Processor interface {
	Process(data string) string
}

// Generic function (Go 1.18+) - should be detected ✅
func genericFunction[T any](item T) T {  // Should detect ✅
	return item
}

func main() {  // Should detect ✅
	// Function calls that should NOT be detected
	calc := &Calculator{value: 0}
	calc.Add(5)  // Should NOT detect ❌
	
	result := add(1, 2)  // Should NOT detect ❌
	fmt.Println(result)  // Should NOT detect ❌
	
	data := processData([]int{1, 2, 3})  // Should NOT detect ❌
	fmt.Printf("Data: %v\n", data)  // Should NOT detect ❌
	
	// More function calls
	publicFunction()  // Should NOT detect ❌
	strings.Contains("hello", "ell")  // Should NOT detect ❌
}