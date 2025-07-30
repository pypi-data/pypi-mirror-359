#!/usr/bin/env python3
"""Debug script to check C# language detection."""

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

# Test language detection
lexer = get_lexer_for_filename('test.cs')
print(f"Lexer: {lexer.__class__.__name__}")

formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
print(f"Language detected by formatter: {formatter._detect_language()}")

# Test without explicit lang
formatter2 = TLDRFormatter(highlight_functions=True)
print(f"Language detected without explicit lang: {formatter2._detect_language()}")