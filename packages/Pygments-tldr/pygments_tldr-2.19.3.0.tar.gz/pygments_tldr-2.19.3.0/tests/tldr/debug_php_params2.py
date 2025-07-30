#!/usr/bin/env python3
"""Debug script to see PHP function parameter extraction with parameters."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

code_with_params = """<?php
function realFunction($data) {
    echo "test";
}
?>"""

code_no_params = """<?php
function realFunction() {
    echo "test";
}
?>"""

try:
    from pygments_tldr.lexers import get_lexer_for_filename
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

print("=== WITH PARAMETERS ===")
lexer = get_lexer_for_filename('test.php')
tokens = list(lexer.get_tokens(code_with_params))

for i, (token_type, value) in enumerate(tokens):
    if 'realFunction' in value or '(' in value or ')' in value or '$data' in value:
        print(f"{i:2d}: {token_type} -> {repr(value)}")

print("\n=== WITHOUT PARAMETERS ===")
lexer = get_lexer_for_filename('test.php')
tokens = list(lexer.get_tokens(code_no_params))

for i, (token_type, value) in enumerate(tokens):
    if 'realFunction' in value or '(' in value or ')' in value:
        print(f"{i:2d}: {token_type} -> {repr(value)}")