#!/usr/bin/env python3

import json
import numpy as np

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== BUILDING CONDITIONAL RECEIPT MODEL ===")

# The key insight: receipt treatment depends on trip characteristics
# Some cases need NEGATIVE receipt coefficients!

def test_conditional_model(day_rate, mile_rate, receipt_rules):
    """Test a conditional receipt model based on trip characteristics"""
    errors = []
    exact_matches = 0
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
        miles_per_day = miles / days if days > 0 else 0
        
        # Base calculation
        base = day_rate * days + mile_rate * miles
        
        # Apply conditional receipt rules
        receipt_contrib = 0
        for condition, rate in receipt_rules:
            if condition(days, miles, receipts, miles_per_day):
                receipt_contrib = receipts * rate
                break
        
        predicted = base + receipt_contrib
        error = abs(expected - predicted)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
    
    avg_error = np.mean(errors)
    return avg_error, exact_matches

# Define conditional rules based on the analysis
receipt_rules = [
    # Rule format: (condition_function, receipt_rate)
    
    # High penalty cases: long trips with high receipts
    (lambda d, m, r, mpd: d >= 8 and r > 1500, -0.3),
    
    # Medium penalty: long trips with medium receipts  
    (lambda d, m, r, mpd: d >= 8 and r > 800, -0.2),
    
    # Very high mileage single day trips with high receipts - negative
    (lambda d, m, r, mpd: d == 1 and m > 800 and r > 1500, -0.1),
    
    # Long trips generally get receipt penalties
    (lambda d, m, r, mpd: d >= 10, 0.0),
    
    # Short trips with very high receipts
    (lambda d, m, r, mpd: d <= 3 and r > 2000, 0.3),
    
    # Medium trips with high receipts but good mileage
    (lambda d, m, r, mpd: 4 <= d <= 6 and r > 1000 and m > 300, 0.5),
    
    # 5-day trips (bonus mentioned in interviews)
    (lambda d, m, r, mpd: d == 5, 0.4),
    
    # High efficiency trips (good miles per day)
    (lambda d, m, r, mpd: mpd > 100 and r < 1500, 0.6),
    
    # Low receipt trips
    (lambda d, m, r, mpd: r < 200, 0.7),
    
    # Medium receipt trips
    (lambda d, m, r, mpd: 200 <= r < 800, 0.5),
    
    # High receipt trips
    (lambda d, m, r, mpd: 800 <= r < 1500, 0.4),
    
    # Default for very high receipts
    (lambda d, m, r, mpd: True, 0.2),
]

# Test different base rates with this conditional system
best_model = None
best_score = float('inf')

day_rates = [90, 95, 100, 105]
mile_rates = [0.65, 0.70, 0.75]

print("Testing conditional receipt models...")

for day_rate in day_rates:
    for mile_rate in mile_rates:
        avg_error, exact_matches = test_conditional_model(day_rate, mile_rate, receipt_rules)
        
        if avg_error < best_score:
            best_score = avg_error
            best_model = (day_rate, mile_rate, exact_matches)
        
        if exact_matches > 0 or avg_error < 200:
            print(f"  ${day_rate}/day + ${mile_rate:.2f}/mile: Avg error ${avg_error:.2f}, Exact matches: {exact_matches}")

print(f"\nBest conditional model: ${best_model[0]}/day + ${best_model[1]:.2f}/mile")
print(f"Average error: ${best_score:.2f}, Exact matches: {best_model[2]}")

# Let's try an even more precise approach - decision tree like rules
print(f"\n=== BUILDING DECISION TREE MODEL ===")

# Analyze the exact patterns more systematically
def build_precise_rules():
    """Build very precise rules based on the data patterns"""
    
    # Group cases by characteristics and find optimal receipt rates
    rules = []
    
    # Rule 1: Long trips with high receipts get negative rates
    long_high_receipt = [(case, i) for i, case in enumerate(cases) 
                        if case['input']['trip_duration_days'] >= 8 and case['input']['total_receipts_amount'] > 1500]
    
    if long_high_receipt:
        # Find optimal rate for this group
        best_rate = None
        best_error = float('inf')
        
        for rate in np.arange(-0.5, 0.1, 0.05):
            errors = []
            for case, idx in long_high_receipt:
                inp = case['input']
                expected = case['expected_output']
                
                predicted = 95 * inp['trip_duration_days'] + 0.70 * inp['miles_traveled'] + rate * inp['total_receipts_amount']
                error = abs(expected - predicted)
                errors.append(error)
            
            avg_error = np.mean(errors)
            if avg_error < best_error:
                best_error = avg_error
                best_rate = rate
        
        print(f"Long trips (8+ days) with high receipts (>$1500): rate {best_rate:.3f}, avg error ${best_error:.2f}")
        rules.append((lambda d, m, r, mpd: d >= 8 and r > 1500, best_rate))
    
    # Rule 2: Short trips with very high receipts
    short_very_high = [(case, i) for i, case in enumerate(cases) 
                      if case['input']['trip_duration_days'] <= 3 and case['input']['total_receipts_amount'] > 1800]
    
    if short_very_high:
        best_rate = None
        best_error = float('inf')
        
        for rate in np.arange(0.1, 0.8, 0.05):
            errors = []
            for case, idx in short_very_high:
                inp = case['input']
                expected = case['expected_output']
                
                predicted = 95 * inp['trip_duration_days'] + 0.70 * inp['miles_traveled'] + rate * inp['total_receipts_amount']
                error = abs(expected - predicted)
                errors.append(error)
            
            avg_error = np.mean(errors)
            if avg_error < best_error:
                best_error = avg_error
                best_rate = rate
        
        print(f"Short trips (≤3 days) with very high receipts (>$1800): rate {best_rate:.3f}, avg error ${best_error:.2f}")
        rules.append((lambda d, m, r, mpd: d <= 3 and r > 1800, best_rate))
    
    # Rule 3: 5-day trips (special case from interviews)
    five_day_trips = [(case, i) for i, case in enumerate(cases) 
                     if case['input']['trip_duration_days'] == 5]
    
    if five_day_trips:
        best_rate = None
        best_error = float('inf')
        
        for rate in np.arange(0.1, 0.8, 0.05):
            errors = []
            for case, idx in five_day_trips:
                inp = case['input']
                expected = case['expected_output']
                
                predicted = 95 * inp['trip_duration_days'] + 0.70 * inp['miles_traveled'] + rate * inp['total_receipts_amount']
                error = abs(expected - predicted)
                errors.append(error)
            
            avg_error = np.mean(errors)
            if avg_error < best_error:
                best_error = avg_error
                best_rate = rate
        
        print(f"5-day trips: rate {best_rate:.3f}, avg error ${best_error:.2f}")
        rules.append((lambda d, m, r, mpd: d == 5, best_rate))
    
    # Rule 4: Default for remaining cases
    remaining_cases = []
    for i, case in enumerate(cases):
        inp = case['input']
        d, m, r = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
        
        # Check if this case is covered by previous rules
        covered = False
        if d >= 8 and r > 1500:
            covered = True
        elif d <= 3 and r > 1800:
            covered = True
        elif d == 5:
            covered = True
        
        if not covered:
            remaining_cases.append((case, i))
    
    if remaining_cases:
        best_rate = None
        best_error = float('inf')
        
        for rate in np.arange(0.0, 0.8, 0.05):
            errors = []
            for case, idx in remaining_cases:
                inp = case['input']
                expected = case['expected_output']
                
                predicted = 95 * inp['trip_duration_days'] + 0.70 * inp['miles_traveled'] + rate * inp['total_receipts_amount']
                error = abs(expected - predicted)
                errors.append(error)
            
            avg_error = np.mean(errors)
            if avg_error < best_error:
                best_error = avg_error
                best_rate = rate
        
        print(f"Default cases: rate {best_rate:.3f}, avg error ${best_error:.2f}")
        rules.append((lambda d, m, r, mpd: True, best_rate))
    
    return rules

precise_rules = build_precise_rules()

# Test the precise rules
print(f"\nTesting precise rules model...")
avg_error, exact_matches = test_conditional_model(95, 0.70, precise_rules)
print(f"Precise rules: Avg error ${avg_error:.2f}, Exact matches: {exact_matches}")

# Test on the problematic cases
print(f"\nTesting on previously problematic cases:")
problematic_cases = [
    (3, 133, 1728.50, 1373.40),
    (3, 91, 1640.15, 1338.30),
    (1, 37, 1397.17, 1092.94),
    (1, 9, 2246.28, 1120.22),
    (1, 43, 2149.22, 1134.47),
]

for days, miles, receipts, expected in problematic_cases:
    miles_per_day = miles / days
    base = 95 * days + 0.70 * miles
    
    # Apply rules
    receipt_contrib = 0
    for condition, rate in precise_rules:
        if condition(days, miles, receipts, miles_per_day):
            receipt_contrib = receipts * rate
            break
    
    predicted = base + receipt_contrib
    error = abs(expected - predicted)
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error ${error:.2f}")