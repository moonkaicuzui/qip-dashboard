#!/usr/bin/env python3
"""Run calculation with debugging"""

import sys
import os

# Redirect input
sys.path.append('src')

print("Running calculation with debugging for ĐINH KIM NGOAN...")
print("=" * 60)

# Mock input
class MockInput:
    def __init__(self):
        self.responses = ['3', '2025', '9']  # Fixed order: year first, then month
        self.index = 0

    def __call__(self, prompt=''):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")
            return response
        return ''

import builtins
original_input = builtins.input
builtins.input = MockInput()

try:
    from step1_인센티브_계산_개선버전 import main
    main()
finally:
    builtins.input = original_input

print("\nCalculation complete. Check output above for debug messages.")