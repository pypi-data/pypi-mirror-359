use std::collections::HashMap;

// Function definitions - should be detected ✅
fn add(a: i32, b: i32) -> i32 {  // Should detect ✅
    // Function calls - should NOT be detected ❌
    println!("Adding {} and {}", a, b);  // Should NOT detect ❌
    std::cmp::max(a, b)  // Should NOT detect ❌
}

pub fn public_function() -> String {  // Should detect ✅
    // More function calls that should NOT be detected
    String::new()  // Should NOT detect ❌
}

fn process_data(data: Vec<i32>) -> Vec<i32> {  // Should detect ✅
    // Method calls - should NOT be detected ❌
    data.iter()
        .map(|x| x * 2)  // Should NOT detect ❌
        .filter(|&x| x > 10)  // Should NOT detect ❌
        .collect()  // Should NOT detect ❌
}

struct Calculator {
    value: i32,
}

impl Calculator {
    // Associated function - should be detected ✅
    fn new() -> Self {  // Should detect ✅
        Self { value: 0 }
    }
    
    // Method - should be detected ✅
    fn add(&mut self, x: i32) {  // Should detect ✅
        self.value += x;
    }
    
    // Method calls inside methods
    fn calculate(&self) -> i32 {  // Should detect ✅
        // Function calls that should NOT be detected
        std::cmp::min(self.value, 100)  // Should NOT detect ❌
    }
}

// Generic function - should be detected ✅
fn generic_function<T: Clone>(item: T) -> T {  // Should detect ✅
    item.clone()  // Should NOT detect ❌ 
}

// Async function - should be detected ✅
async fn async_function() -> Result<(), Box<dyn std::error::Error>> {  // Should detect ✅
    // Async function calls - should NOT be detected
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;  // Should NOT detect ❌
    Ok(())
}

fn main() {  // Should detect ✅
    let mut calc = Calculator::new();  // Should NOT detect ❌
    calc.add(5);  // Should NOT detect ❌
    
    // More function calls
    println!("Result: {}", calc.calculate());  // Should NOT detect ❌
    add(1, 2);  // Should NOT detect ❌
    process_data(vec![1, 2, 3]);  // Should NOT detect ❌
}