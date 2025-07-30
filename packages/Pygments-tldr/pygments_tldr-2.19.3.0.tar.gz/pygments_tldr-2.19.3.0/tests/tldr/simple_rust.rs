fn simple_function() {  // Should detect ✅
    println!("test");  // Should NOT detect ❌
    some_function();  // Should NOT detect ❌
}

struct Test;
impl Test {
    fn method(&self) {  // Should detect ✅
        self.other_method();  // Should NOT detect ❌
    }
}