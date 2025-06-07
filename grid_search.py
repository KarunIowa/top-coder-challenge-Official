#!/usr/bin/env python3

import json
import numpy as np

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== EXHAUSTIVE GRID SEARCH FOR EXACT MATCHES ===")

# I need to find the exact coefficients that maximize exact matches
# Let's do a very fine-grained search

def test_formula(day_coef, mile_coef, receipt_coef, bonus_5day=0):
    """Test a specific formula"""
    exact_matches = 0
    errors = []
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
        
        predicted = day_coef * days + mile_coef * miles + receipt_coef * receipts
        
        # Add 5-day bonus if applicable
        if days == 5:
            predicted += bonus_5day
        
        error = abs(expected - predicted)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
    
    avg_error = np.mean(errors)
    return exact_matches, avg_error

# Start with the formula that gave us 1 exact match and refine it
base_day = 95
base_mile = 0.70
base_receipt = 0.056

print("Refining around the best known formula...")

# Fine-tune around the known good values
best_exact = 0
best_params = None
best_error = float('inf')

# Search around the known good values with finer increments
for day_coef in np.arange(base_day - 10, base_day + 11, 1):
    for mile_coef in np.arange(base_mile - 0.1, base_mile + 0.11, 0.02):
        for receipt_coef in np.arange(0.01, 0.6, 0.01):
            for bonus_5day in [0, 20, 30, 50, 75, 100]:
                
                exact_matches, avg_error = test_formula(day_coef, mile_coef, receipt_coef, bonus_5day)
                
                # Prioritize exact matches, then low average error
                if (exact_matches > best_exact or 
                    (exact_matches == best_exact and avg_error < best_error)):
                    best_exact = exact_matches
                    best_error = avg_error
                    best_params = (day_coef, mile_coef, receipt_coef, bonus_5day)
                
                # Report progress for good results
                if exact_matches > 0 or avg_error < 200:
                    print(f"  ${day_coef:.0f}/day + ${mile_coef:.2f}/mile + {receipt_coef:.3f}*receipts + ${bonus_5day} 5-day bonus")
                    print(f"    Exact matches: {exact_matches}, Avg error: ${avg_error:.2f}")

print(f"\nBest formula found:")
day_coef, mile_coef, receipt_coef, bonus_5day = best_params
print(f"${day_coef:.0f}/day + ${mile_coef:.2f}/mile + {receipt_coef:.3f}*receipts + ${bonus_5day} 5-day bonus")
print(f"Exact matches: {best_exact}, Average error: ${best_error:.2f}")

# Test this formula on some known cases
print(f"\nTesting best formula on known cases:")
test_cases = [
    (1, 47, 17.97, 128.91),  # The original exact match
    (3, 133, 1728.50, 1373.40),  # Previous failure
    (5, 250, 150.75, None),  # Test case
]

for days, miles, receipts, expected in test_cases:
    predicted = day_coef * days + mile_coef * miles + receipt_coef * receipts
    if days == 5:
        predicted += bonus_5day
    
    if expected:
        error = abs(expected - predicted)
        print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error ${error:.2f}")
    else:
        print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Predicted ${predicted:.2f}")

# If we still don't have enough exact matches, try a different approach
if best_exact < 5:
    print(f"\n=== TRYING PIECEWISE LINEAR APPROACH ===")
    
    # Maybe the system uses different coefficients for different ranges
    # Let's try a piecewise approach
    
    def test_piecewise_formula(day_coef, mile_coef, receipt_ranges):
        """Test a piecewise receipt formula"""
        exact_matches = 0
        errors = []
        
        for case in cases:
            inp = case['input']
            expected = case['expected_output']
            
            days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
            
            # Base calculation
            predicted = day_coef * days + mile_coef * miles
            
            # Piecewise receipt calculation
            receipt_contrib = 0
            for (min_val, max_val, coef) in receipt_ranges:
                if min_val <= receipts < max_val:
                    receipt_contrib = receipts * coef
                    break
            
            predicted += receipt_contrib
            
            error = abs(expected - predicted)
            errors.append(error)
            
            if error < 0.01:
                exact_matches += 1
        
        avg_error = np.mean(errors)
        return exact_matches, avg_error
    
    # Try different piecewise structures
    piecewise_structures = [
        [(0, 500, 0.8), (500, 1500, 0.4), (1500, float('inf'), 0.1)],
        [(0, 200, 0.9), (200, 800, 0.5), (800, 2000, 0.3), (2000, float('inf'), 0.05)],
        [(0, 300, 0.7), (300, 1000, 0.5), (1000, 1800, 0.3), (1800, float('inf'), 0.15)],
    ]
    
    best_piecewise = 0
    best_piecewise_params = None
    best_piecewise_error = float('inf')
    
    for day_coef in [90, 95, 100]:
        for mile_coef in [0.65, 0.70, 0.75]:
            for structure in piecewise_structures:
                exact_matches, avg_error = test_piecewise_formula(day_coef, mile_coef, structure)
                
                if (exact_matches > best_piecewise or 
                    (exact_matches == best_piecewise and avg_error < best_piecewise_error)):
                    best_piecewise = exact_matches
                    best_piecewise_error = avg_error
                    best_piecewise_params = (day_coef, mile_coef, structure)
                
                if exact_matches > 0:
                    print(f"  ${day_coef}/day + ${mile_coef}/mile + {structure}")
                    print(f"    Exact matches: {exact_matches}, Avg error: ${avg_error:.2f}")
    
    if best_piecewise > best_exact:
        print(f"\nBetter piecewise formula found:")
        day_coef, mile_coef, structure = best_piecewise_params
        print(f"${day_coef}/day + ${mile_coef}/mile + {structure}")
        print(f"Exact matches: {best_piecewise}, Average error: ${best_piecewise_error:.2f}")
        
        # Update best parameters for implementation
        best_params = best_piecewise_params
        best_exact = best_piecewise
        best_error = best_piecewise_error

print(f"\n=== FINAL BEST MODEL ===")
if len(best_params) == 3:  # Piecewise
    day_coef, mile_coef, structure = best_params
    print(f"Piecewise model: ${day_coef}/day + ${mile_coef}/mile + {structure}")
else:  # Linear
    day_coef, mile_coef, receipt_coef, bonus_5day = best_params
    print(f"Linear model: ${day_coef}/day + ${mile_coef:.2f}/mile + {receipt_coef:.3f}*receipts + ${bonus_5day} 5-day bonus")

print(f"Performance: {best_exact} exact matches, ${best_error:.2f} average error")

# Save the best model parameters for implementation
import pickle
model_params = {
    'type': 'piecewise' if len(best_params) == 3 else 'linear',
    'params': best_params,
    'exact_matches': best_exact,
    'avg_error': best_error
}

with open('/app/best_model_params.pkl', 'wb') as f:
    pickle.dump(model_params, f)

print(f"\nBest model parameters saved to best_model_params.pkl")