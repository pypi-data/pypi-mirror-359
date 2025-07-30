#!/usr/bin/env python3
"""Debug script to see PHP function parameter extraction."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
    from pygments_tldr.formatters.tldr import TLDRFormatter
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """<?php
function realFunction() {
    echo "test";
}
?>"""

lexer = get_lexer_for_filename('test.php')
tokens = list(lexer.get_tokens(code))

print("All tokens:")
for i, (token_type, value) in enumerate(tokens):
    print(f"{i:2d}: {token_type} -> {repr(value)}")

print("\n" + "="*50)
print("Testing function detection:")

formatter = TLDRFormatter()
formatter.lexer = lexer

# Manually test the detection
from pygments_tldr.token import Keyword
for i, (ttype, value) in enumerate(tokens):
    if ttype == Keyword and value == 'function':
        print(f"Found 'function' at index {i}")
        result = formatter._detect_php_function(tokens, i)
        print(f"Detection result: {result}")
        break