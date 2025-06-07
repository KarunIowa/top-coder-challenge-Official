#!/usr/bin/env python3

import json
import statistics
import numpy as np
from collections import defaultdict

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== DEEPER PATTERN ANALYSIS ===")

# Check if it's a base per diem + mileage model
print("\n1. Testing base per diem hypothesis:")
base_per_diems = [100, 120, 150]  # Test different bases
for base in base_per_diems:
    total_error = 0
    for case in cases[:50]:  # Test on subset
        inp = case['input']
        expected = case['expected_output']
        
        # Simple model: base_per_diem * days + mileage_rate * miles
        simple_estimate = base * inp['trip_duration_days'] + 0.6 * inp['miles_traveled']
        error = abs(expected - simple_estimate)
        total_error += error
    
    avg_error = total_error / 50
    print(f"  Base ${base}/day + $0.60/mile: avg error ${avg_error:.2f}")

# Analyze receipt impact
print("\n2. Receipt impact analysis:")
receipt_ranges = [(0, 50), (50, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 3000)]
for min_r, max_r in receipt_ranges:
    matching_cases = [c for c in cases if min_r <= c['input']['total_receipts_amount'] < max_r]
    if matching_cases:
        # Calculate what portion of receipts seem to be reimbursed
        receipt_portions = []
        for case in matching_cases:
            inp = case['input']
            output = case['expected_output']
            # Assume base: 100/day + 0.6/mile, then see what's left for receipts
            base_estimate = 100 * inp['trip_duration_days'] + 0.6 * inp['miles_traveled']
            receipt_portion = output - base_estimate
            if inp['total_receipts_amount'] > 0:
                receipt_rate = receipt_portion / inp['total_receipts_amount']
                receipt_portions.append(receipt_rate)
        
        if receipt_portions:
            avg_rate = statistics.mean(receipt_portions)
            print(f"  ${min_r}-${max_r}: {len(matching_cases)} cases, avg receipt rate: {avg_rate:.2f}")

# Look for the 5-day bonus mentioned in interviews
print("\n3. Trip duration bonuses:")
duration_analysis = {}
for duration in range(1, 11):
    duration_cases = [c for c in cases if c['input']['trip_duration_days'] == duration]
    if duration_cases:
        # Calculate average "per day rate" for each duration
        rates = []
        for case in duration_cases:
            rate = case['expected_output'] / case['input']['trip_duration_days']
            rates.append(rate)
        duration_analysis[duration] = {
            'count': len(duration_cases),
            'avg_rate': statistics.mean(rates),
            'cases': duration_cases[:3]  # Store a few examples
        }

print("  Duration -> Avg $/day:")
for duration in sorted(duration_analysis.keys()):
    data = duration_analysis[duration]
    print(f"    {duration} days: ${data['avg_rate']:.2f}/day ({data['count']} cases)")

# Check efficiency sweet spot mentioned by Kevin (180-220 miles/day)
print("\n4. Efficiency bonus analysis:")
efficiency_bonuses = {}
for case in cases:
    inp = case['input']
    if inp['trip_duration_days'] > 0:
        miles_per_day = inp['miles_traveled'] / inp['trip_duration_days']
        efficiency_range = int(miles_per_day // 20) * 20  # Group by 20s
        if efficiency_range not in efficiency_bonuses:
            efficiency_bonuses[efficiency_range] = []
        
        # Calculate bonus over base model
        base_estimate = 100 * inp['trip_duration_days'] + 0.6 * inp['miles_traveled']
        bonus = case['expected_output'] - base_estimate
        efficiency_bonuses[efficiency_range].append(bonus)

print("  Miles/day range -> Avg bonus over base:")
for efficiency in sorted(efficiency_bonuses.keys())[:10]:
    bonuses = efficiency_bonuses[efficiency]
    avg_bonus = statistics.mean(bonuses)
    print(f"    {efficiency}-{efficiency+19}: ${avg_bonus:.2f} bonus ({len(bonuses)} cases)")

# Look for specific patterns mentioned in interviews
print("\n5. Special patterns:")

# Check for the "small receipts penalty" mentioned
small_receipt_cases = [c for c in cases if c['input']['total_receipts_amount'] < 50]
print(f"Small receipt cases (<$50): {len(small_receipt_cases)}")
if small_receipt_cases:
    for case in small_receipt_cases[:5]:
        inp = case['input']
        output = case['expected_output']
        base_est = 100 * inp['trip_duration_days'] + 0.6 * inp['miles_traveled']
        print(f"    {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} -> ${output:.2f} (base est: ${base_est:.2f})")