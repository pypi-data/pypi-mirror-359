#!/usr/bin/env python3
"""Debug script to show tokens for Java code."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """public class Simple {
    public Simple() {
        System.out.println("constructor");
    }
}"""

lexer = get_lexer_for_filename('test.java')
tokens = list(lexer.get_tokens(code))

print("Tokens around constructor:")
for i, (token_type, value) in enumerate(tokens):
    if 'Simple' in value or 'public' in value or value in ('(', ')', '{'):
        print(f"{i:2d}: {token_type} -> '{value}' ⭐")
    elif i > 5 and i < 25:  # Show context around the constructor
        print(f"{i:2d}: {token_type} -> '{value}'")