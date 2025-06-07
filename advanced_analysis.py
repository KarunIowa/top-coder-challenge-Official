#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict
from calculate_reimbursement import calculate_reimbursement

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== ADVANCED PATTERN ANALYSIS ===")

# Test current model on larger sample
print("Testing current model on 200 cases:")
errors = []
exact_matches = 0
close_matches = 0

for case in cases[:200]:
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - actual)
    errors.append(error)
    
    if error < 0.01:
        exact_matches += 1
    elif error < 1.0:
        close_matches += 1

avg_error = np.mean(errors)
print(f"Current model: {exact_matches}/200 exact, {close_matches}/200 close, avg error ${avg_error:.2f}")

# Analyze the error patterns to find missing logic
print("\nAnalyzing error patterns:")

# Group by error characteristics
high_error_cases = []
for i, case in enumerate(cases[:200]):
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - actual)
    
    if error > 50:
        high_error_cases.append({
            'index': i,
            'input': inp,
            'expected': expected,
            'actual': actual,
            'error': error,
            'ratio': expected / actual if actual > 0 else 0
        })

print(f"\nFound {len(high_error_cases)} cases with error > $50")

# Look for patterns in high error cases
print("\nPattern analysis in high error cases:")

# Pattern 1: Are we consistently over or under-estimating?
over_estimates = [case for case in high_error_cases if case['actual'] > case['expected']]
under_estimates = [case for case in high_error_cases if case['actual'] < case['expected']]

print(f"Over-estimates: {len(over_estimates)}, Under-estimates: {len(under_estimates)}")

# Pattern 2: Trip duration analysis
duration_errors = defaultdict(list)
for case in high_error_cases:
    duration = case['input']['trip_duration_days']
    duration_errors[duration].append(case['error'])

print("\nError by trip duration:")
for duration in sorted(duration_errors.keys()):
    errors = duration_errors[duration]
    avg_err = np.mean(errors)
    print(f"  {duration} days: avg error ${avg_err:.2f} ({len(errors)} cases)")

# Pattern 3: Look for non-linear relationships
print("\nLooking for missing non-linear patterns...")

# Test if error correlates with specific input ranges
receipt_errors = defaultdict(list)
mile_errors = defaultdict(list)

for case in high_error_cases:
    # Receipt buckets
    receipt_bucket = int(case['input']['total_receipts_amount'] // 200) * 200
    receipt_errors[receipt_bucket].append(case['ratio'])
    
    # Mile buckets  
    mile_bucket = int(case['input']['miles_traveled'] // 100) * 100
    mile_errors[mile_bucket].append(case['ratio'])

print("\nExpected/Actual ratios by receipt amount:")
for bucket in sorted(receipt_errors.keys())[:8]:
    ratios = receipt_errors[bucket]
    if len(ratios) >= 3:
        avg_ratio = np.mean(ratios)
        print(f"  ${bucket}-${bucket+199}: ratio {avg_ratio:.2f} ({len(ratios)} cases)")

print("\nExpected/Actual ratios by mileage:")
for bucket in sorted(mile_errors.keys())[:8]:
    ratios = mile_errors[bucket]
    if len(ratios) >= 3:
        avg_ratio = np.mean(ratios)
        print(f"  {bucket}-{bucket+99} miles: ratio {avg_ratio:.2f} ({len(ratios)} cases)")

# Show some specific high-error examples for manual analysis
print("\nHigh error examples for manual analysis:")
sorted_errors = sorted(high_error_cases, key=lambda x: x['error'], reverse=True)
for case in sorted_errors[:5]:
    inp = case['input']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Expected: ${case['expected']:.2f}, Got: ${case['actual']:.2f}, Error: ${case['error']:.2f}")
    
    # Calculate what our base model gives
    base = 75 * inp['trip_duration_days'] + 0.5 * inp['miles_traveled'] + 0.5 * inp['total_receipts_amount']
    print(f"    Base model: ${base:.2f}, Difference: ${case['expected'] - base:.2f}")
    print()