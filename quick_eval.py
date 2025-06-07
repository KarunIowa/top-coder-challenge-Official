#!/usr/bin/env python3

import json
from calculate_reimbursement import calculate_reimbursement

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== FINAL EVALUATION ===")

# Test on all 1000 cases
total_error = 0
exact_matches = 0
close_matches = 0
max_error = 0
max_error_case = ""

for i, case in enumerate(cases):
    if i % 200 == 0:
        print(f"Progress: {i}/1000 cases...")
    
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    
    error = abs(expected - actual)
    total_error += error
    
    if error < 0.01:
        exact_matches += 1
    elif error < 1.0:
        close_matches += 1
        
    if error > max_error:
        max_error = error
        max_error_case = f"Case {i+1}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}"

# Calculate final metrics
avg_error = total_error / 1000
exact_pct = (exact_matches / 1000) * 100
close_pct = (close_matches / 1000) * 100

print(f"\n✅ Final Results:")
print(f"  Total test cases: 1000")
print(f"  Exact matches (±$0.01): {exact_matches} ({exact_pct:.1f}%)")
print(f"  Close matches (±$1.00): {close_matches} ({close_pct:.1f}%)")
print(f"  Average error: ${avg_error:.2f}")
print(f"  Maximum error: ${max_error:.2f}")
print(f"  Worst case: {max_error_case}")

# Calculate score (same as eval.sh)
score = avg_error * 100 + (1000 - exact_matches) * 0.1
print(f"\n🎯 Score: {score:.2f} (lower is better)")

# Provide feedback
if exact_matches == 1000:
    print("🏆 PERFECT SCORE! System fully reverse-engineered!")
elif exact_matches > 950:
    print("🥇 Excellent! Very close to perfect solution.")
elif exact_matches > 800:
    print("🥈 Great work! Captured most system behavior.")
elif exact_matches > 500:
    print("🥉 Good progress! Understanding key patterns.")
else:
    print("📚 Keep analyzing patterns.")

# Show some high-error cases for debugging
print(f"\nTop 5 highest error cases:")
high_errors = []
for i, case in enumerate(cases):
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - actual)
    high_errors.append((error, i+1, inp, expected, actual))

high_errors.sort(reverse=True)
for error, case_num, inp, expected, actual in high_errors[:5]:
    print(f"  Case {case_num}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Expected: ${expected:.2f}, Got: ${actual:.2f}, Error: ${error:.2f}")