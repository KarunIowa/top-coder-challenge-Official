#!/usr/bin/env python3

import json
import numpy as np
import statistics

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== EXTREME CASE ANALYSIS ===")

# Find cases with very high receipts to understand the pattern
high_receipt_cases = [case for case in cases if case['input']['total_receipts_amount'] > 1500]
print(f"Found {len(high_receipt_cases)} cases with receipts > $1500")

print("\nHigh receipt patterns:")
for case in high_receipt_cases[:10]:
    inp = case['input']
    output = case['expected_output']
    
    # Calculate what a simple per diem would give
    simple_per_diem = 100 * inp['trip_duration_days']
    
    # Calculate receipt reimbursement rate
    if simple_per_diem < output:
        receipt_rate = (output - simple_per_diem) / inp['total_receipts_amount']
    else:
        receipt_rate = (output - simple_per_diem) / inp['total_receipts_amount']
    
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${output:.2f}")
    print(f"    Receipt rate: {receipt_rate:.3f} (per $ of receipts)")

# Analyze very high mileage cases
high_mileage_cases = [case for case in cases if case['input']['miles_traveled'] > 800]
print(f"\nFound {len(high_mileage_cases)} cases with miles > 800")

print("\nHigh mileage patterns:")
for case in high_mileage_cases[:10]:
    inp = case['input']
    output = case['expected_output']
    
    # Calculate per mile rate
    per_mile = output / inp['miles_traveled'] if inp['miles_traveled'] > 0 else 0
    miles_per_day = inp['miles_traveled'] / inp['trip_duration_days']
    
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${output:.2f}")
    print(f"    ${per_mile:.3f}/mile, {miles_per_day:.1f} mi/day")

# Look for the actual pattern by trying different base models
print(f"\n=== TESTING DIFFERENT BASE MODELS ===")

# Try to find patterns by grouping similar cases
def group_similar_cases():
    """Group cases by similar characteristics"""
    groups = {}
    
    for case in cases:
        inp = case['input']
        
        # Create a signature for grouping
        days_bucket = min(inp['trip_duration_days'], 10)  # Cap at 10
        miles_bucket = int(inp['miles_traveled'] // 100) * 100  # Group by 100s
        receipts_bucket = int(inp['total_receipts_amount'] // 500) * 500  # Group by 500s
        
        signature = (days_bucket, miles_bucket, receipts_bucket)
        
        if signature not in groups:
            groups[signature] = []
        groups[signature].append(case)
    
    return groups

groups = group_similar_cases()
print(f"Found {len(groups)} unique patterns")

# Analyze groups with multiple cases to find consistent patterns
consistent_groups = {k: v for k, v in groups.items() if len(v) >= 3}
print(f"Found {len(consistent_groups)} patterns with 3+ cases")

print("\nConsistent patterns:")
for signature, group_cases in list(consistent_groups.items())[:10]:
    days_bucket, miles_bucket, receipts_bucket = signature
    outputs = [case['expected_output'] for case in group_cases]
    avg_output = statistics.mean(outputs)
    std_output = statistics.stdev(outputs) if len(outputs) > 1 else 0
    
    print(f"  {days_bucket}d, {miles_bucket}+mi, ${receipts_bucket}+: {len(group_cases)} cases")
    print(f"    Avg output: ${avg_output:.2f} ± ${std_output:.2f}")
    
    # Try to derive a simple formula
    avg_days = statistics.mean([case['input']['trip_duration_days'] for case in group_cases])
    avg_miles = statistics.mean([case['input']['miles_traveled'] for case in group_cases])
    avg_receipts = statistics.mean([case['input']['total_receipts_amount'] for case in group_cases])
    
    # Test simple model: a*days + b*miles + c*receipts
    # If we assume standard rates, what would c need to be?
    if avg_receipts > 0:
        remaining_after_base = avg_output - (75 * avg_days + 0.3 * avg_miles)
        implied_receipt_rate = remaining_after_base / avg_receipts
        print(f"    Implied receipt rate: {implied_receipt_rate:.3f}")

# Special analysis for the worst error cases
print(f"\n=== WORST CASES ANALYSIS ===")
worst_cases = [
    {"days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94},
    {"days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69},
    {"days": 4, "miles": 69, "receipts": 2321.49, "expected": 322.00},
]

for case in worst_cases:
    print(f"\nCase: {case['days']}d, {case['miles']:.0f}mi, ${case['receipts']:.2f} -> ${case['expected']:.2f}")
    
    # What would different models predict?
    simple_base = 75 * case['days'] + 0.3 * case['miles'] + 0.2 * case['receipts']
    print(f"  Simple model (75/d + 0.3/mi + 0.2*receipts): ${simple_base:.2f}")
    
    # What if we cap receipts heavily?
    capped_receipts = min(case['receipts'], 500)  # Cap at $500
    capped_model = 75 * case['days'] + 0.3 * case['miles'] + 0.4 * capped_receipts
    print(f"  Capped receipts model: ${capped_model:.2f}")
    
    # What rate would make it match?
    remaining = case['expected'] - (75 * case['days'] + 0.3 * case['miles'])
    needed_rate = remaining / case['receipts'] if case['receipts'] > 0 else 0
    print(f"  Required receipt rate to match: {needed_rate:.3f}")
    
    # Check if it's actually a different formula entirely
    per_day_rate = case['expected'] / case['days']
    per_mile_rate = case['expected'] / case['miles'] if case['miles'] > 0 else 0
    print(f"  Total per day: ${per_day_rate:.2f}, per mile: ${per_mile_rate:.3f}")