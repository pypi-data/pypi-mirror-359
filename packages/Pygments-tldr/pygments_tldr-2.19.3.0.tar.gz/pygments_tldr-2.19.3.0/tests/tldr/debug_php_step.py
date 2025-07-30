#!/usr/bin/env python3
"""Debug script to step through PHP function detection logic."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
    from pygments_tldr.token import Keyword, Name, Text
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

# Manually step through _detect_php_function logic
for i, (ttype, value) in enumerate(tokens):
    if ttype == Keyword and value == 'function':
        print(f"Found 'function' at index {i}")
        
        # Step 1: Skip function keyword
        i += 1
        print(f"After function keyword, i={i}")
        
        # Step 2: Skip whitespace/text
        while i < len(tokens) and (tokens[i][0] in (Text,) or (tokens[i][0] == Text and tokens[i][1].strip() == '')):
            print(f"Skipping whitespace at {i}: {tokens[i]}")
            i += 1
        
        print(f"After skipping whitespace, i={i}")
        if i < len(tokens):
            next_ttype, next_value = tokens[i]
            print(f"Next token: {next_ttype} -> {repr(next_value)}")
            
            # Check if it matches expected types
            expected_types = (Name.Other, Name, Name.Function, Name.Function.Magic)
            print(f"Expected types: {expected_types}")
            print(f"Matches? {next_ttype in expected_types}")
        break