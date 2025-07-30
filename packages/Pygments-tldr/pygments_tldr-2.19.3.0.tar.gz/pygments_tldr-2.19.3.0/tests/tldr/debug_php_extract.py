#!/usr/bin/env python3
"""Debug script to test PHP parameter extraction directly."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr.lexers import get_lexer_for_filename
    from pygments_tldr.formatters.tldr import TLDRFormatter
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

formatter = TLDRFormatter()

# Find the function and call parameter extraction
for i, (ttype, value) in enumerate(tokens):
    if ttype == Keyword and value == 'function':
        print(f"Found 'function' at index {i}")
        
        # Step through _detect_php_function logic
        i += 1  # Skip 'function' keyword
        while i < len(tokens) and (tokens[i][0] in (Text,) or (tokens[i][0] == Text and tokens[i][1].strip() == '')):
            i += 1
        
        if i < len(tokens):
            next_ttype, next_value = tokens[i]
            if next_ttype in (Name.Other, Name, Name.Function, Name.Function.Magic):
                function_name = next_value
                print(f"Function name: {function_name}")
                i += 1
                
                # Call parameter extraction directly
                print(f"Calling _extract_function_parameters with i={i}")
                print(f"Tokens from i onwards: {[(j, tokens[j]) for j in range(i, min(i+10, len(tokens)))]}")
                
                result = formatter._extract_function_parameters(tokens, i, function_name, 2)  # start_idx=2 (function keyword)
                print(f"Parameter extraction result: {result}")
        break