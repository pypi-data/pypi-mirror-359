#!/usr/bin/env python3
"""Debug script to see PHP tokens around function definition."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """<?php
function simpleFunction($param) {
    echo "test";
    return $param;
}
?>"""

lexer = get_lexer_for_filename('test.php')
tokens = list(lexer.get_tokens(code))

print("Tokens around function definition:")
for i, (token_type, value) in enumerate(tokens):
    if 'function' in value.lower() or 'simpleFunction' in value:
        # Show context around function-related tokens
        start = max(0, i - 3)
        end = min(len(tokens), i + 15)
        print(f"\nContext around token {i}:")
        for j in range(start, end):
            marker = " ⭐ " if j == i else "    "
            print(f"{j:2d}:{marker}{tokens[j][0]} -> '{repr(tokens[j][1])}'")
        break