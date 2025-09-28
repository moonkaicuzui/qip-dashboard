#!/usr/bin/env python3
"""Test ĐINH KIM NGOAN calculation directly"""

import sys
sys.path.append('src')
from step1_인센티브_계산_개선버전 import main as calculate_main

print("=== TESTING ĐINH KIM NGOAN CALCULATION ===\n")
print("Running calculation with month=9, year=2025...")
print("Look for '🔍 ĐINH KIM NGOAN 특별 디버깅' in the output below:\n")
print("=" * 60)

# Mock input for automatic response
class MockInput:
    def __init__(self):
        self.responses = ['3', '9', '2025']  # Option 3 for custom, then month 9, then year 2025
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
    # Run calculation
    calculate_main()
finally:
    builtins.input = original_input

print("\n" + "=" * 60)
print("Calculation complete. Check output above for ĐINH KIM NGOAN debugging info.")