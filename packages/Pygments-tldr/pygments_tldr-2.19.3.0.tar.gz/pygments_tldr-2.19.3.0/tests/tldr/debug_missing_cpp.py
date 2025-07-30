#!/usr/bin/env python3
"""Debug script to see why some C++ functions are missing."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """class Calculator {
public:
    Calculator() {
        initialize();
    }
    
    int multiply(int x, int y) {
        return x * y;
    }
};

int main() {
    return 0;
}"""

lexer = get_lexer_for_filename('test.cpp')
tokens = list(lexer.get_tokens(code))

print("All tokens with function-like names:")
for i, (token_type, value) in enumerate(tokens):
    if value in ('Calculator', 'initialize', 'multiply', 'main') or 'Function' in str(token_type):
        print(f"{i:2d}: {token_type} -> '{value}' ⭐")
    elif i > 5 and i < 50:  # Show some context
        print(f"{i:2d}: {token_type} -> '{value}'")