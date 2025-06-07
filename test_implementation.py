#!/usr/bin/env python3

import json

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Test our implementation on first 20 cases
print("Testing first 20 cases:")
print("Expected vs Actual vs Error")

total_error = 0
exact_matches = 0

for i, case in enumerate(cases[:20]):
    inp = case['input']
    expected = case['expected_output']
    
    # Import our calculator
    from calculate_reimbursement import calculate_reimbursement
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    
    error = abs(expected - actual)
    total_error += error
    
    if error < 0.01:
        exact_matches += 1
        status = "✓"
    elif error < 1.0:
        status = "~"
    else:
        status = "✗"
    
    print(f"{i+1:2d}: ${expected:7.2f} vs ${actual:7.2f} = ${error:6.2f} {status} ({inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f})")

avg_error = total_error / 20
print(f"\nSummary: {exact_matches}/20 exact matches, avg error: ${avg_error:.2f}")

# Now let's see what patterns we're missing
print("\nAnalyzing errors...")
large_errors = []
for i, case in enumerate(cases[:100]):
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - actual)
    
    if error > 50:  # Large errors
        large_errors.append({
            'case': i+1,
            'input': inp,
            'expected': expected,
            'actual': actual,
            'error': error
        })

print(f"\nFound {len(large_errors)} cases with error > $50:")
for err in large_errors[:5]:
    inp = err['input']
    print(f"Case {err['case']}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${err['expected']:.2f}, Got: ${err['actual']:.2f}, Error: ${err['error']:.2f}")