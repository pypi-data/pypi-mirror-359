#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function definitions - should be detected ✅
int add(int a, int b) {  // Should detect ✅
    // Function calls - should NOT be detected ❌
    printf("Adding %d and %d\n", a, b);  // Should NOT detect ❌
    return a + b;
}

void print_array(int *arr, int size) {  // Should detect ✅
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);  // Should NOT detect ❌
    }
    printf("\n");  // Should NOT detect ❌
}

static int compare(const void *a, const void *b) {  // Should detect ✅
    return (*(int*)a - *(int*)b);
}

// Struct with no methods (C doesn't have methods)
struct Point {
    int x, y;
};

struct Point create_point(int x, int y) {  // Should detect ✅
    struct Point p;
    p.x = x;
    p.y = y;
    return p;
}

void process_data() {  // Should detect ✅
    // Function calls that should NOT be detected
    int *arr = malloc(10 * sizeof(int));  // Should NOT detect ❌
    memset(arr, 0, 10 * sizeof(int));  // Should NOT detect ❌
    qsort(arr, 10, sizeof(int), compare);  // Should NOT detect ❌
    free(arr);  // Should NOT detect ❌
}

int main(int argc, char *argv[]) {  // Should detect ✅
    int result = add(5, 3);  // Should NOT detect ❌
    print_array(&result, 1);  // Should NOT detect ❌
    process_data();  // Should NOT detect ❌
    return 0;
}