#!/usr/bin/env python3

import json

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== EXACT MATCH DISCOVERY ===")

# Find the exact match cases from the simple model
def simple_model(days, miles, receipts):
    return 100 * days + 0.5 * miles + 0.3 * receipts

exact_match_cases = []
for i, case in enumerate(cases):
    inp = case['input']
    expected = case['expected_output']
    
    simple_pred = simple_model(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - simple_pred)
    
    if error < 0.5:  # Very close matches
        exact_match_cases.append((error, i, case, simple_pred))

# Sort by error
exact_match_cases.sort()

print(f"Found {len(exact_match_cases)} very close matches with simple model:")
for error, idx, case, pred in exact_match_cases[:10]:
    inp = case['input']
    expected = case['expected_output']
    print(f"Case {idx+1}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${expected:.2f}, Simple: ${pred:.2f}, Error: ${error:.2f}")
    
    # What exact coefficients would work?
    # expected = a*days + b*miles + c*receipts
    # We know simple model is close, so find exact adjustment
    if inp['trip_duration_days'] > 0:
        implied_day_rate = (expected - 0.5 * inp['miles_traveled'] - 0.3 * inp['total_receipts_amount']) / inp['trip_duration_days']
        print(f"  Implied day rate: ${implied_day_rate:.3f}")
    print()

# Look at the pattern in exact matches
print("=== ANALYZING EXACT MATCH PATTERN ===")

# The exact match case was: 1d, 47mi, $17.97 -> $128.91 (error: $0.02)
# Let's see what formula gives exactly $128.91

target_case = None
for case in cases:
    inp = case['input']
    if (inp['trip_duration_days'] == 1 and 
        abs(inp['miles_traveled'] - 47) < 1 and 
        abs(inp['total_receipts_amount'] - 17.97) < 0.1):
        target_case = case
        break

if target_case:
    inp = target_case['input']
    expected = target_case['expected_output']
    
    print(f"Exact match target: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f}")
    
    # Try different formulas to get exactly 128.91
    days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
    
    print("Testing exact formulas:")
    
    # Formula 1: a*days + b*miles + c*receipts = 128.91
    # With 1 day, 47 miles, 17.97 receipts
    # a + 47b + 17.97c = 128.91
    
    for a in range(50, 151, 5):  # Day rate
        for b in [0.5, 0.55, 0.6, 0.65, 0.7]:  # Mile rate
            c = (128.91 - a - 47 * b) / 17.97  # Solve for receipt rate
            if 0 <= c <= 2:  # Reasonable receipt rate
                test_result = a + 47 * b + 17.97 * c
                print(f"  ${a}/day + ${b:.2f}/mi + {c:.3f}*receipts = ${test_result:.2f}")
                
                if abs(test_result - 128.91) < 0.01:
                    print(f"    *** EXACT MATCH! ***")
                    
                    # Test this formula on a few other cases
                    print(f"    Testing on other cases:")
                    test_errors = []
                    for test_case in cases[:20]:
                        test_inp = test_case['input']
                        test_expected = test_case['expected_output']
                        test_pred = a * test_inp['trip_duration_days'] + b * test_inp['miles_traveled'] + c * test_inp['total_receipts_amount']
                        test_error = abs(test_expected - test_pred)
                        test_errors.append(test_error)
                        
                        if len(test_errors) <= 5:
                            print(f"      Case: ${test_expected:.2f} vs ${test_pred:.2f} = ${test_error:.2f}")
                    
                    avg_test_error = sum(test_errors) / len(test_errors)
                    print(f"    Average error on 20 cases: ${avg_test_error:.2f}")
                    print()

# Let's also check if there's a pattern in the coefficients
print("=== COEFFICIENT PATTERN ANALYSIS ===")

# For each case, calculate what the coefficients would need to be
coefficients = []
for case in cases[:100]:  # Sample 100 cases
    inp = case['input']
    expected = case['expected_output']
    
    days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
    
    # If we fix day rate at 100 and mile rate at 0.5, what receipt rate is needed?
    if receipts > 0:
        needed_receipt_rate = (expected - 100 * days - 0.5 * miles) / receipts
        coefficients.append({
            'case': case,
            'receipt_rate': needed_receipt_rate,
            'days': days,
            'miles': miles,
            'receipts': receipts
        })

# Look for patterns in the receipt rates
low_receipt_rates = [c for c in coefficients if c['receipt_rate'] < 0.2]
medium_receipt_rates = [c for c in coefficients if 0.2 <= c['receipt_rate'] < 0.8]
high_receipt_rates = [c for c in coefficients if c['receipt_rate'] >= 0.8]

print(f"Receipt rate distribution:")
print(f"  Low (<0.2): {len(low_receipt_rates)} cases")
print(f"  Medium (0.2-0.8): {len(medium_receipt_rates)} cases")  
print(f"  High (>=0.8): {len(high_receipt_rates)} cases")

print(f"\nLow receipt rate cases (high penalty):")
for coef in low_receipt_rates[:5]:
    inp = coef['case']['input']
    expected = coef['case']['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f} (rate: {coef['receipt_rate']:.3f})")

print(f"\nHigh receipt rate cases (good treatment):")
for coef in high_receipt_rates[:5]:
    inp = coef['case']['input']
    expected = coef['case']['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f} (rate: {coef['receipt_rate']:.3f})")