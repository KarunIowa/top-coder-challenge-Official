#!/usr/bin/env python3

import json
import numpy as np

# Load the public cases  
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== DIRECT FORMULA SEARCH ===")

# Look for the exact mathematical relationship
# Try different combinations systematically

def test_formula(formula_func, name):
    """Test a formula function against all cases"""
    errors = []
    exact_matches = 0
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        try:
            predicted = formula_func(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
            error = abs(expected - predicted)
            errors.append(error)
            
            if error < 0.01:
                exact_matches += 1
        except:
            errors.append(1000)  # Large error for failed cases
    
    avg_error = np.mean(errors)
    max_error = np.max(errors)
    
    print(f"{name}:")
    print(f"  Avg error: ${avg_error:.2f}")
    print(f"  Max error: ${max_error:.2f}")
    print(f"  Exact matches: {exact_matches}/1000")
    print(f"  Close matches: {sum(1 for e in errors if e < 1.0)}/1000")
    
    return avg_error, exact_matches

# Test various formulas
formulas = []

# Formula 1: Pure linear with different coefficients
def formula1(days, miles, receipts):
    return 88.17 * days + 0.41 * miles + 1.21 * receipts - 165.14

formulas.append((formula1, "Linear regression (original)"))

# Formula 2: Modified linear with constraints
def formula2(days, miles, receipts):
    base = 88.17 * days + 0.41 * miles + 0.8 * receipts - 165.14
    return max(base, 50)

formulas.append((formula2, "Linear with receipt cap"))

# Formula 3: Piecewise linear for receipts
def formula3(days, miles, receipts):
    base = 88.17 * days + 0.41 * miles - 165.14
    
    if receipts <= 500:
        receipt_contrib = receipts * 1.2
    elif receipts <= 1500:
        receipt_contrib = 500 * 1.2 + (receipts - 500) * 0.8
    else:
        receipt_contrib = 500 * 1.2 + 1000 * 0.8 + (receipts - 1500) * 0.3
    
    return max(base + receipt_contrib, 50)

formulas.append((formula3, "Piecewise receipt handling"))

# Formula 4: Days squared term
def formula4(days, miles, receipts):
    return 88.17 * days + 0.41 * miles + 1.21 * receipts - 165.14 - 2.59 * (days * days)

formulas.append((formula4, "With days² term"))

# Formula 5: All interaction terms
def formula5(days, miles, receipts):
    return (88.17 * days + 0.41 * miles + 1.21 * receipts - 165.14 - 
            2.59 * (days * days) + 0.0145 * (days * miles) - 0.0089 * (days * receipts))

formulas.append((formula5, "Full linear regression"))

# Formula 6: Conservative version
def formula6(days, miles, receipts):
    base = 75 * days + 0.4 * miles
    
    # Conservative receipt handling
    if receipts <= 200:
        receipt_contrib = receipts * 0.6
    elif receipts <= 800:
        receipt_contrib = 200 * 0.6 + (receipts - 200) * 0.4
    elif receipts <= 1500:
        receipt_contrib = 200 * 0.6 + 600 * 0.4 + (receipts - 800) * 0.2
    else:
        receipt_contrib = 200 * 0.6 + 600 * 0.4 + 700 * 0.2 + (receipts - 1500) * 0.1
    
    total = base + receipt_contrib
    
    # 5-day bonus
    if days == 5:
        total += 50
    
    return max(total, 50)

formulas.append((formula6, "Conservative tiered"))

# Formula 7: Based on interview patterns
def formula7(days, miles, receipts):
    # Base rates from interviews
    base = 100 * days + 0.58 * miles
    
    # Receipt rate based on trip characteristics
    if days <= 3 and miles >= 500:
        receipt_rate = 0.5  # High efficiency short trips
    elif days >= 7:
        receipt_rate = 0.3  # Long trips get lower receipt rates
    elif receipts > 2000:
        receipt_rate = 0.15  # Very high receipts penalized
    else:
        receipt_rate = 0.4
    
    receipt_contrib = receipts * receipt_rate
    
    return max(base + receipt_contrib, 50)

formulas.append((formula7, "Interview-based"))

# Test all formulas
best_formula = None
best_score = float('inf')

for formula_func, name in formulas:
    avg_error, exact_matches = test_formula(formula_func, name)
    
    if avg_error < best_score:
        best_score = avg_error
        best_formula = (formula_func, name)
    
    print()

print(f"Best formula: {best_formula[1]} with avg error ${best_score:.2f}")

# Test the best formula on problematic cases
print(f"\nTesting best formula on problematic cases:")
problematic_cases = [
    (8, 795, 1645.99, 644.69),
    (5, 516, 1878.49, 669.85),
    (4, 87, 2463.92, 1413.52),
    (4, 84, 2243.12, 1392.10),
    (1, 1082, 1809.49, 446.94),
]

for days, miles, receipts, expected in problematic_cases:
    predicted = best_formula[0](days, miles, receipts)
    error = abs(expected - predicted)
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error ${error:.2f}")

# Look for an even simpler pattern by examining outliers
print(f"\n=== OUTLIER ANALYSIS ===")

# Find cases where simple models work well
simple_errors = []
for case in cases:
    inp = case['input']
    expected = case['expected_output']
    
    # Very simple model
    simple_pred = 100 * inp['trip_duration_days'] + 0.5 * inp['miles_traveled'] + 0.3 * inp['total_receipts_amount']
    simple_error = abs(expected - simple_pred)
    simple_errors.append((simple_error, case))

# Sort by error
simple_errors.sort()

print("Cases where simple model works well (low error):")
for i in range(5):
    error, case = simple_errors[i]
    inp = case['input']
    expected = case['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f} (error: ${error:.2f})")

print("\nCases where simple model fails (high error):")
for i in range(5):
    error, case = simple_errors[-(i+1)]
    inp = case['input']
    expected = case['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f} (error: ${error:.2f})")