#include <iostream>
#include <vector>
#include <string>

// Function definitions - should be detected ✅
int add(int a, int b) {  // Should detect ✅
    // Function calls - should NOT be detected ❌
    std::cout << "Adding numbers" << std::endl;
    return std::max(a, b);  // Should NOT detect ❌
}

void staticFunction() {  // Should detect ✅
    // Constructor calls - should NOT be detected ❌
    std::vector<int> vec;
    std::string str("test");
    
    // Method calls - should NOT be detected ❌
    vec.push_back(42);
    str.length();
    printf("Hello");  // Should NOT detect ❌
}

class Calculator {
public:
    // Constructor - should be detected ✅
    Calculator() {  // Should detect ✅
        initialize();  // Should NOT detect ❌
    }
    
    // Method definition - should be detected ✅
    int multiply(int x, int y) {  // Should detect ✅
        return x * y;
    }
    
    // Destructor - should be detected ✅
    ~Calculator() {  // Should detect ✅
        cleanup();  // Should NOT detect ❌
    }
    
private:
    void initialize() {  // Should detect ✅
        // More function calls that should NOT be detected
        std::cout << "Initializing" << std::endl;
        malloc(100);  // Should NOT detect ❌
        free(nullptr);  // Should NOT detect ❌
    }
    
    void cleanup() {  // Should detect ✅
        // Function calls
        std::cout << "Cleaning up" << std::endl;
    }
};

// Template function - should be detected ✅
template<typename T>
T maximum(T a, T b) {  // Should detect ✅
    return (a > b) ? a : b;
}

int main() {  // Should detect ✅
    Calculator calc;
    int result = calc.multiply(5, 3);  // Should NOT detect ❌
    std::cout << result << std::endl;
    return 0;
}