#!/usr/bin/env python3

import json
import numpy as np
from collections import defaultdict

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== SYSTEMATIC EXACT MATCH PURSUIT ===")

# Analyze the high-error cases from our current model
current_high_errors = [
    {"days": 3, "miles": 133, "receipts": 1728.50, "expected": 1373.40, "current": 474.90},
    {"days": 3, "miles": 91, "receipts": 1640.15, "expected": 1338.30, "current": 440.55},
    {"days": 1, "miles": 37, "receipts": 1397.17, "expected": 1092.94, "current": 199.14},
    {"days": 1, "miles": 9, "receipts": 2246.28, "expected": 1120.22, "current": 227.09},
    {"days": 1, "miles": 43, "receipts": 2149.22, "expected": 1134.47, "current": 245.46},
]

print("Current model failures analysis:")
for case in current_high_errors:
    days, miles, receipts, expected = case['days'], case['miles'], case['receipts'], case['expected']
    
    # What receipt rate would be needed?
    base_without_receipts = 95 * days + 0.70 * miles
    needed_from_receipts = expected - base_without_receipts
    needed_receipt_rate = needed_from_receipts / receipts if receipts > 0 else 0
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f} -> ${expected:.2f}")
    print(f"    Current receipt rate: 0.056, Needed: {needed_receipt_rate:.3f}")

# These cases need receipt rates around 0.4-0.6, not 0.056!
# I need a tiered receipt system

print(f"\n=== BUILDING OPTIMIZED TIERED MODEL ===")

# Let's systematically find the best tiered receipt model
def test_tiered_model(day_rate, mile_rate, receipt_tiers):
    """Test a tiered receipt model"""
    errors = []
    exact_matches = 0
    
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
        
        # Base calculation
        base = day_rate * days + mile_rate * miles
        
        # Tiered receipt calculation
        receipt_contrib = 0
        remaining_receipts = receipts
        
        for threshold, rate in receipt_tiers:
            if remaining_receipts <= 0:
                break
            
            tier_amount = min(remaining_receipts, threshold)
            receipt_contrib += tier_amount * rate
            remaining_receipts -= tier_amount
        
        predicted = base + receipt_contrib
        error = abs(expected - predicted)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
    
    avg_error = np.mean(errors)
    return avg_error, exact_matches, errors

# Test different tiered models
best_model = None
best_score = float('inf')

print("Testing tiered receipt models...")

# Define tier structures to test
tier_structures = [
    # [(tier_size, rate), (tier_size, rate), (remaining, rate)]
    [(500, 0.6), (1000, 0.4), (float('inf'), 0.2)],
    [(300, 0.7), (700, 0.5), (1000, 0.3), (float('inf'), 0.1)],
    [(200, 0.8), (500, 0.6), (1000, 0.4), (float('inf'), 0.2)],
    [(400, 0.6), (800, 0.4), (1200, 0.3), (float('inf'), 0.15)],
    [(250, 0.7), (750, 0.5), (1500, 0.3), (float('inf'), 0.1)],
]

day_rates = [90, 95, 100]
mile_rates = [0.65, 0.70, 0.75]

for day_rate in day_rates:
    for mile_rate in mile_rates:
        for tiers in tier_structures:
            avg_error, exact_matches, errors = test_tiered_model(day_rate, mile_rate, tiers)
            
            if avg_error < best_score:
                best_score = avg_error
                best_model = (day_rate, mile_rate, tiers, exact_matches)
            
            if exact_matches > 0:  # Found exact matches!
                print(f"  ${day_rate}/day + ${mile_rate:.2f}/mile + {tiers}")
                print(f"    Avg error: ${avg_error:.2f}, Exact matches: {exact_matches}")

print(f"\nBest tiered model:")
day_rate, mile_rate, tiers, exact_matches = best_model
print(f"  ${day_rate}/day + ${mile_rate:.2f}/mile + {tiers}")
print(f"  Avg error: ${best_score:.2f}, Exact matches: {exact_matches}")

# Test this model on our problematic cases
print(f"\nTesting best model on problematic cases:")
for case in current_high_errors:
    days, miles, receipts, expected = case['days'], case['miles'], case['receipts'], case['expected']
    
    # Calculate using best model
    base = day_rate * days + mile_rate * miles
    receipt_contrib = 0
    remaining_receipts = receipts
    
    for threshold, rate in tiers:
        if remaining_receipts <= 0:
            break
        tier_amount = min(remaining_receipts, threshold)
        receipt_contrib += tier_amount * rate
        remaining_receipts -= tier_amount
    
    predicted = base + receipt_contrib
    error = abs(expected - predicted)
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error ${error:.2f}")

# Now let's try even more sophisticated approaches
print(f"\n=== ADVANCED PATTERN ANALYSIS ===")

# Look for cases that need special handling
special_cases = []
_, _, errors = test_tiered_model(day_rate, mile_rate, tiers)

for i, error in enumerate(errors):
    if error > 200:  # High error cases
        case = cases[i]
        inp = case['input']
        expected = case['expected_output']
        special_cases.append({
            'index': i,
            'input': inp,
            'expected': expected,
            'error': error
        })

print(f"Found {len(special_cases)} cases with error > $200")

# Analyze patterns in high-error cases
print(f"\nHigh error case patterns:")
for case in special_cases[:10]:
    inp = case['input']
    expected = case['expected']
    
    days, miles, receipts = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
    miles_per_day = miles / days if days > 0 else 0
    
    print(f"  Case {case['index']+1}: {days}d, {miles:.0f}mi, ${receipts:.2f} -> ${expected:.2f}")
    print(f"    {miles_per_day:.1f} mi/day, Error: ${case['error']:.2f}")

# Look for patterns that distinguish high vs low reimbursement cases
print(f"\n=== FINDING DISCRIMINATING PATTERNS ===")

# Group cases by output ranges
low_output = [case for case in cases if case['expected_output'] < 500]
medium_output = [case for case in cases if 500 <= case['expected_output'] < 1500]
high_output = [case for case in cases if case['expected_output'] >= 1500]

print(f"Output distribution: Low (<$500): {len(low_output)}, Medium ($500-1500): {len(medium_output)}, High (>=$1500): {len(high_output)}")

# Analyze characteristics of each group
for group_name, group_cases in [("Low", low_output), ("Medium", medium_output), ("High", high_output)]:
    if not group_cases:
        continue
        
    avg_days = np.mean([case['input']['trip_duration_days'] for case in group_cases])
    avg_miles = np.mean([case['input']['miles_traveled'] for case in group_cases])
    avg_receipts = np.mean([case['input']['total_receipts_amount'] for case in group_cases])
    avg_miles_per_day = np.mean([case['input']['miles_traveled'] / max(case['input']['trip_duration_days'], 1) for case in group_cases])
    
    print(f"{group_name} output group averages:")
    print(f"  Days: {avg_days:.1f}, Miles: {avg_miles:.0f}, Receipts: ${avg_receipts:.0f}")
    print(f"  Miles/day: {avg_miles_per_day:.1f}")

# Try to find the exact pattern by examining successful vs failed predictions
print(f"\n=== EXACT PATTERN DISCOVERY ===")

# Find cases where our current best model works well vs fails
_, _, errors = test_tiered_model(day_rate, mile_rate, tiers)
good_predictions = []
bad_predictions = []

for i, error in enumerate(errors):
    case_data = {
        'case': cases[i],
        'error': error
    }
    
    if error < 10:
        good_predictions.append(case_data)
    elif error > 100:
        bad_predictions.append(case_data)

print(f"Good predictions (error < $10): {len(good_predictions)}")
print(f"Bad predictions (error > $100): {len(bad_predictions)}")

# Look for the distinguishing features
if good_predictions and bad_predictions:
    print(f"\nComparing good vs bad predictions:")
    
    # Good predictions characteristics
    good_days = [case['case']['input']['trip_duration_days'] for case in good_predictions]
    good_miles = [case['case']['input']['miles_traveled'] for case in good_predictions]
    good_receipts = [case['case']['input']['total_receipts_amount'] for case in good_predictions]
    
    # Bad predictions characteristics  
    bad_days = [case['case']['input']['trip_duration_days'] for case in bad_predictions]
    bad_miles = [case['case']['input']['miles_traveled'] for case in bad_predictions]
    bad_receipts = [case['case']['input']['total_receipts_amount'] for case in bad_predictions]
    
    print(f"Good predictions avg: {np.mean(good_days):.1f}d, {np.mean(good_miles):.0f}mi, ${np.mean(good_receipts):.0f}")
    print(f"Bad predictions avg: {np.mean(bad_days):.1f}d, {np.mean(bad_miles):.0f}mi, ${np.mean(bad_receipts):.0f}")

    # Look for specific patterns in bad predictions
    print(f"\nWorst prediction examples:")
    bad_predictions.sort(key=lambda x: x['error'], reverse=True)
    for case_data in bad_predictions[:5]:
        case = case_data['case']
        inp = case['input']
        expected = case['expected_output']
        error = case_data['error']
        
        print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f} (error: ${error:.2f})")
        
        # What would make this work?
        base = day_rate * inp['trip_duration_days'] + mile_rate * inp['miles_traveled']
        needed_from_receipts = expected - base
        needed_rate = needed_from_receipts / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
        
        print(f"    Base: ${base:.2f}, Needed from receipts: ${needed_from_receipts:.2f} (rate: {needed_rate:.3f})")