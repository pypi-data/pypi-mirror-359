int add(int a, int b) {  // Should detect ✅
    printf("test");  // Should NOT detect ❌
    return a + b;
}

void test() {  // Should detect ✅
    add(1, 2);  // Should NOT detect ❌
}