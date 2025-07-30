#!/usr/bin/env python3
"""Debug script to show tokens for C++ code."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """int add(int a, int b) {
    printf("test");
    return a + b;
}"""

lexer = get_lexer_for_filename('test.cpp')
tokens = list(lexer.get_tokens(code))

print("Tokens around printf:")
for i, (token_type, value) in enumerate(tokens):
    if 'printf' in value or 'int' in value or 'add' in value or value in ('(', ')', '{', ';'):
        print(f"{i:2d}: {token_type} -> '{value}' ⭐")
    elif i > 5 and i < 25:  # Show context
        print(f"{i:2d}: {token_type} -> '{value}'")