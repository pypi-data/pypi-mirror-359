#!/usr/bin/env python3
"""Debug script to understand Java method detection."""

import sys
import os
import logging

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

try:
    from pygments_tldr import highlight
    from pygments_tldr.lexers import get_lexer_for_filename
    from pygments_tldr.formatters.tldr import TLDRFormatter
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    sys.exit(1)

code = """public class Simple {
    public Simple() {
        System.out.println("constructor");
    }
    
    public void method() {
        new Simple();
    }
}"""

print("Code to analyze:")
print(code)
print("\n" + "="*50)

lexer = get_lexer_for_filename('test.java')
formatter = TLDRFormatter(highlight_functions=True, lang='java')
result = highlight(code, lexer, formatter)

print("Result:")
print(result)