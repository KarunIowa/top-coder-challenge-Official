#!/usr/bin/env python3

import json
from calculate_reimbursement import calculate_reimbursement

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== FINDING EXACT MATCHES FOR PERFECT SCORE ===")

# Find the exact matches to understand what makes them work
exact_matches = []
close_matches = []
all_errors = []

for i, case in enumerate(cases):
    inp = case['input']
    expected = case['expected_output']
    actual = calculate_reimbursement(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    
    error = abs(expected - actual)
    all_errors.append(error)
    
    if error < 0.01:
        exact_matches.append({
            'index': i+1,
            'input': inp,
            'expected': expected,
            'actual': actual,
            'error': error
        })
    elif error < 1.0:
        close_matches.append({
            'index': i+1,
            'input': inp,
            'expected': expected,
            'actual': actual,
            'error': error
        })

print(f"Found {len(exact_matches)} exact matches:")
for match in exact_matches:
    inp = match['input']
    print(f"  Case {match['index']}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.1f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Expected: ${match['expected']:.2f}, Got: ${match['actual']:.2f}, Error: ${match['error']:.6f}")
    
    # Calculate what the current formula gives
    formula_result = 86 * inp['trip_duration_days'] + 0.76 * inp['miles_traveled'] + 0.35 * inp['total_receipts_amount']
    print(f"    Formula (86d + 0.76m + 0.35r): ${formula_result:.2f}")
    print()

print(f"Found {len(close_matches)} close matches (within $1):")
for match in close_matches[:5]:  # Show first 5
    inp = match['input']
    print(f"  Case {match['index']}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.1f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"    Expected: ${match['expected']:.2f}, Got: ${match['actual']:.2f}, Error: ${match['error']:.2f}")

# Now let's try to find a pattern that could get us to perfect accuracy
print(f"\n=== ANALYZING ALL CASES FOR PERFECT PATTERN ===")

# Try to find if there's a simple mathematical relationship
# that could explain ALL cases exactly

# Test if it's actually a completely different formula
print("Testing alternative formulas...")

# Test different bases
test_formulas = [
    (75, 0.58, 0.30),  # Standard government rates
    (100, 0.50, 0.25), # Round numbers
    (80, 0.75, 0.40),  # Close to current best
    (90, 0.70, 0.30),  # Variations
    (85, 0.77, 0.35),  # Fine-tuned around current
]

best_exact = 0
best_formula = None
best_avg_error = float('inf')

for day_rate, mile_rate, receipt_rate in test_formulas:
    exact_count = 0
    total_error = 0
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        predicted = day_rate * inp['trip_duration_days'] + mile_rate * inp['miles_traveled'] + receipt_rate * inp['total_receipts_amount']
        predicted = round(predicted, 2)
        
        error = abs(expected - predicted)
        total_error += error
        
        if error < 0.01:
            exact_count += 1
    
    avg_error = total_error / len(cases)
    
    print(f"Formula {day_rate}d + {mile_rate}m + {receipt_rate}r: {exact_count} exact, ${avg_error:.2f} avg error")
    
    if exact_count > best_exact or (exact_count == best_exact and avg_error < best_avg_error):
        best_exact = exact_count
        best_formula = (day_rate, mile_rate, receipt_rate)
        best_avg_error = avg_error

print(f"\nBest formula found: ${best_formula[0]}/day + ${best_formula[1]}/mile + {best_formula[2]}*receipts")
print(f"Achieves: {best_exact} exact matches, ${best_avg_error:.2f} average error")

# If we're still not at perfect, let's try a completely different approach
if best_exact < 1000:
    print(f"\n=== TRYING NON-LINEAR APPROACHES ===")
    
    # Maybe it's not linear at all - let's check for other patterns
    print("Checking for non-linear patterns...")
    
    # Look at cases where linear model fails badly
    big_errors = []
    for i, case in enumerate(cases):
        inp = case['input']
        expected = case['expected_output']
        
        # Current best linear
        predicted = best_formula[0] * inp['trip_duration_days'] + best_formula[1] * inp['miles_traveled'] + best_formula[2] * inp['total_receipts_amount']
        predicted = round(predicted, 2)
        
        error = abs(expected - predicted)
        
        if error > 100:  # Big errors
            big_errors.append({
                'case': i+1,
                'input': inp,
                'expected': expected,
                'predicted': predicted,
                'error': error
            })
    
    print(f"Found {len(big_errors)} cases with >$100 error. Sample:")
    for err in big_errors[:5]:
        inp = err['input']
        print(f"  Case {err['case']}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
        print(f"    Expected: ${err['expected']:.2f}, Predicted: ${err['predicted']:.2f}, Error: ${err['error']:.2f}")

print(f"\n=== RECOMMENDATION FOR PERFECT SCORE ===")
if best_exact < 1000:
    print("Linear models are not achieving perfect accuracy.")
    print("The legacy system likely has:")
    print("1. Complex conditional logic")
    print("2. Lookup tables")
    print("3. Historical quirks/bugs that must be replicated")
    print("4. Non-linear relationships")
    print()
    print("To achieve score of 0, we need to analyze the specific")
    print("patterns in the high-error cases and build conditional logic.")