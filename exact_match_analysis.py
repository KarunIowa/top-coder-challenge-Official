#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== EXACT MATCH ANALYSIS ===")

# Analyze the specific high-error cases to understand the pattern
high_error_cases = [
    {"days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69},
    {"days": 5, "miles": 516, "receipts": 1878.49, "expected": 669.85},
    {"days": 4, "miles": 87, "receipts": 2463.92, "expected": 1413.52},
    {"days": 4, "miles": 84, "receipts": 2243.12, "expected": 1392.10},
    {"days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94},
]

print("High error case analysis:")
for case in high_error_cases:
    print(f"\n{case['days']}d, {case['miles']:.0f}mi, ${case['receipts']:.2f} -> ${case['expected']:.2f}")
    
    # What would different base rates give?
    base_75 = 75 * case['days']
    base_100 = 100 * case['days'] 
    base_120 = 120 * case['days']
    
    remaining_75 = case['expected'] - base_75
    remaining_100 = case['expected'] - base_100
    remaining_120 = case['expected'] - base_120
    
    print(f"  Base $75/day: remaining ${remaining_75:.2f}")
    print(f"  Base $100/day: remaining ${remaining_100:.2f}")
    print(f"  Base $120/day: remaining ${remaining_120:.2f}")
    
    # What mileage + receipt combination would work?
    if case['miles'] > 0:
        # Try different mileage rates
        for mileage_rate in [0.3, 0.4, 0.5, 0.58]:
            mileage_contrib = mileage_rate * case['miles']
            receipt_contrib = case['expected'] - base_100 - mileage_contrib
            receipt_rate = receipt_contrib / case['receipts'] if case['receipts'] > 0 else 0
            print(f"  $100/day + ${mileage_rate}/mi: receipt rate = {receipt_rate:.3f}")

# Let's try to find the exact algorithm by looking for consistent patterns
print(f"\n=== SYSTEMATIC PATTERN SEARCH ===")

# Test a range of base per diems and mileage rates
best_error = float('inf')
best_params = None

for base_per_diem in range(50, 151, 5):  # $50-150 per day
    for mileage_rate in [0.1, 0.2, 0.3, 0.4, 0.5, 0.58, 0.6]:
        errors = []
        
        for case in cases[:200]:  # Test on subset for speed
            inp = case['input']
            expected = case['expected_output']
            
            # Simple model
            estimated = base_per_diem * inp['trip_duration_days'] + mileage_rate * inp['miles_traveled']
            
            # Add basic receipt handling
            if inp['total_receipts_amount'] <= 500:
                receipt_contrib = inp['total_receipts_amount'] * 0.3
            elif inp['total_receipts_amount'] <= 1500:
                receipt_contrib = 500 * 0.3 + (inp['total_receipts_amount'] - 500) * 0.2
            else:
                receipt_contrib = 500 * 0.3 + 1000 * 0.2 + (inp['total_receipts_amount'] - 1500) * 0.1
            
            estimated += receipt_contrib
            
            error = abs(expected - estimated)
            errors.append(error)
        
        avg_error = np.mean(errors)
        
        if avg_error < best_error:
            best_error = avg_error
            best_params = (base_per_diem, mileage_rate)

print(f"Best simple model: ${best_params[0]}/day + ${best_params[1]:.2f}/mile")
print(f"Average error: ${best_error:.2f}")

# Now let's look for more complex patterns by examining similar cases
print(f"\n=== FINDING SIMILAR CASE PATTERNS ===")

# Group cases by similar characteristics
def find_similar_cases(target_case):
    """Find cases similar to the target case"""
    target = target_case['input']
    similar = []
    
    for case in cases:
        inp = case['input']
        
        # Define similarity criteria
        day_diff = abs(inp['trip_duration_days'] - target['trip_duration_days'])
        mile_diff = abs(inp['miles_traveled'] - target['miles_traveled'])
        receipt_diff = abs(inp['total_receipts_amount'] - target['total_receipts_amount'])
        
        # Normalize differences
        day_score = day_diff / max(target['trip_duration_days'], 1)
        mile_score = mile_diff / max(target['miles_traveled'], 1) if target['miles_traveled'] > 0 else 0
        receipt_score = receipt_diff / max(target['total_receipts_amount'], 1) if target['total_receipts_amount'] > 0 else 0
        
        total_score = day_score + mile_score + receipt_score
        
        if total_score < 0.3:  # Similar cases
            similar.append({
                'case': case,
                'similarity': total_score
            })
    
    return sorted(similar, key=lambda x: x['similarity'])

# Find exact matches or near-exact matches in the dataset
exact_matches = defaultdict(list)
for case in cases:
    inp = case['input']
    
    # Create a signature for exact matching
    signature = (
        inp['trip_duration_days'],
        round(inp['miles_traveled']),
        round(inp['total_receipts_amount'])
    )
    
    exact_matches[signature].append(case)

# Look for patterns in exact duplicate inputs
duplicates = {k: v for k, v in exact_matches.items() if len(v) > 1}
print(f"Found {len(duplicates)} sets of duplicate inputs")

for signature, group in list(duplicates.items())[:5]:
    outputs = [case['expected_output'] for case in group]
    if len(set(outputs)) == 1:  # Same output
        print(f"  {signature}: {len(group)} cases -> ${outputs[0]:.2f}")
    else:  # Different outputs for same input!
        print(f"  {signature}: {len(group)} cases -> outputs vary: {[f'${x:.2f}' for x in outputs]}")

# Try to find the linear formula by solving a system of equations
print(f"\n=== LINEAR REGRESSION APPROACH ===")

# Prepare data for linear regression
X = []
y = []

for case in cases:
    inp = case['input']
    output = case['expected_output']
    
    # Features: days, miles, receipts, days^2, miles^2, receipts^2, interactions
    features = [
        1,  # intercept
        inp['trip_duration_days'],
        inp['miles_traveled'],
        inp['total_receipts_amount'],
        inp['trip_duration_days'] ** 2,
        inp['miles_traveled'] ** 2,
        inp['total_receipts_amount'] ** 2,
        inp['trip_duration_days'] * inp['miles_traveled'],
        inp['trip_duration_days'] * inp['total_receipts_amount'],
        inp['miles_traveled'] * inp['total_receipts_amount'],
    ]
    
    X.append(features)
    y.append(output)

X = np.array(X)
y = np.array(y)

# Solve using least squares
try:
    coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
    
    print("Linear regression coefficients:")
    feature_names = ['intercept', 'days', 'miles', 'receipts', 'days²', 'miles²', 'receipts²', 'days*miles', 'days*receipts', 'miles*receipts']
    
    for i, (name, coef) in enumerate(zip(feature_names, coefficients)):
        if abs(coef) > 0.001:  # Only show significant coefficients
            print(f"  {name}: {coef:.6f}")
    
    # Test this model
    predictions = X.dot(coefficients)
    errors = np.abs(predictions - y)
    avg_error = np.mean(errors)
    exact_matches_lr = np.sum(errors < 0.01)
    
    print(f"\nLinear regression results:")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  Exact matches: {exact_matches_lr}/1000")
    
except Exception as e:
    print(f"Linear regression failed: {e}")