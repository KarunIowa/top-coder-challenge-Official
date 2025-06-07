#!/usr/bin/env python3

import json
import statistics

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== BALANCED PATTERN ANALYSIS ===")

# Look at high-receipt cases that got GOOD vs BAD treatment
high_receipt_cases = [case for case in cases if case['input']['total_receipts_amount'] > 1500]

# Calculate simple base model for each
base_reimbursements = []
for case in high_receipt_cases:
    inp = case['input']
    output = case['expected_output']
    
    base_model = 75 * inp['trip_duration_days'] + 0.3 * inp['miles_traveled']
    receipt_contribution = output - base_model
    receipt_rate = receipt_contribution / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
    
    base_reimbursements.append({
        'case': case,
        'base_model': base_model,
        'receipt_contribution': receipt_contribution,
        'receipt_rate': receipt_rate,
        'miles_per_day': inp['miles_traveled'] / inp['trip_duration_days']
    })

# Sort by receipt rate to see which got good vs bad treatment
base_reimbursements.sort(key=lambda x: x['receipt_rate'], reverse=True)

print("\nHigh receipt cases - GOOD treatment (high receipt rates):")
for item in base_reimbursements[:10]:
    inp = item['case']['input']
    output = item['case']['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${output:.2f}")
    print(f"    Receipt rate: {item['receipt_rate']:.3f}, {item['miles_per_day']:.1f} mi/day")

print("\nHigh receipt cases - BAD treatment (low/negative receipt rates):")
for item in base_reimbursements[-10:]:
    inp = item['case']['input']
    output = item['case']['expected_output']
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f} -> ${output:.2f}")
    print(f"    Receipt rate: {item['receipt_rate']:.3f}, {item['miles_per_day']:.1f} mi/day")

# Look for patterns that distinguish good vs bad treatment
good_treatment = [item for item in base_reimbursements if item['receipt_rate'] > 0.5]
bad_treatment = [item for item in base_reimbursements if item['receipt_rate'] < 0.1]

print(f"\nGOOD treatment patterns ({len(good_treatment)} cases):")
avg_days_good = statistics.mean([item['case']['input']['trip_duration_days'] for item in good_treatment])
avg_miles_good = statistics.mean([item['case']['input']['miles_traveled'] for item in good_treatment])
avg_receipts_good = statistics.mean([item['case']['input']['total_receipts_amount'] for item in good_treatment])
avg_mpd_good = statistics.mean([item['miles_per_day'] for item in good_treatment])

print(f"  Avg: {avg_days_good:.1f}d, {avg_miles_good:.0f}mi, ${avg_receipts_good:.0f}, {avg_mpd_good:.1f} mi/day")

print(f"\nBAD treatment patterns ({len(bad_treatment)} cases):")
avg_days_bad = statistics.mean([item['case']['input']['trip_duration_days'] for item in bad_treatment])
avg_miles_bad = statistics.mean([item['case']['input']['miles_traveled'] for item in bad_treatment])
avg_receipts_bad = statistics.mean([item['case']['input']['total_receipts_amount'] for item in bad_treatment])
avg_mpd_bad = statistics.mean([item['miles_per_day'] for item in bad_treatment])

print(f"  Avg: {avg_days_bad:.1f}d, {avg_miles_bad:.0f}mi, ${avg_receipts_bad:.0f}, {avg_mpd_bad:.1f} mi/day")

# Check specific conditions
print(f"\nPattern analysis:")
print(f"Good treatment - high miles/day cases: {len([x for x in good_treatment if x['miles_per_day'] > 100])}/{len(good_treatment)}")
print(f"Bad treatment - high miles/day cases: {len([x for x in bad_treatment if x['miles_per_day'] > 100])}/{len(bad_treatment)}")

print(f"Good treatment - long trips (7+ days): {len([x for x in good_treatment if x['case']['input']['trip_duration_days'] >= 7])}/{len(good_treatment)}")
print(f"Bad treatment - long trips (7+ days): {len([x for x in bad_treatment if x['case']['input']['trip_duration_days'] >= 7])}/{len(bad_treatment)}")

print(f"Good treatment - very high receipts (>$2000): {len([x for x in good_treatment if x['case']['input']['total_receipts_amount'] > 2000])}/{len(good_treatment)}")
print(f"Bad treatment - very high receipts (>$2000): {len([x for x in bad_treatment if x['case']['input']['total_receipts_amount'] > 2000])}/{len(bad_treatment)}")

# Test the current problematic cases against this pattern
problematic_cases = [
    (1, 1002, 2320.13, 1475.40),
    (1, 872, 2420.07, 1456.34), 
    (1, 989, 2196.84, 1439.17),
]

print(f"\nProblematic cases analysis:")
for days, miles, receipts, expected in problematic_cases:
    miles_per_day = miles / days
    base_model = 75 * days + 0.3 * miles
    receipt_contribution = expected - base_model
    receipt_rate = receipt_contribution / receipts
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f} -> ${expected:.2f}")
    print(f"    Base model: ${base_model:.2f}, Receipt contrib: ${receipt_contribution:.2f}")
    print(f"    Receipt rate: {receipt_rate:.3f}, {miles_per_day:.1f} mi/day")
    
    # These are 1-day, very high mileage, very high receipt cases that got GOOD treatment
    # So the pattern might be: high mileage compensates for high receipts?