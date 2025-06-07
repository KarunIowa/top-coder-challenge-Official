#!/usr/bin/env python3

import json
import statistics
import numpy as np
from collections import defaultdict

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print(f'Total cases: {len(cases)}')
print('Sample cases:')
for i in range(5):
    case = cases[i]
    inp = case['input']
    out = case['expected_output']
    print(f'  {inp["trip_duration_days"]} days, {inp["miles_traveled"]} miles, ${inp["total_receipts_amount"]} -> ${out}')

# Basic statistics
durations = [case['input']['trip_duration_days'] for case in cases]
miles = [case['input']['miles_traveled'] for case in cases]
receipts = [case['input']['total_receipts_amount'] for case in cases]
outputs = [case['expected_output'] for case in cases]

print('\nStatistics:')
print(f'Duration: min={min(durations)}, max={max(durations)}, avg={statistics.mean(durations):.1f}')
print(f'Miles: min={min(miles)}, max={max(miles)}, avg={statistics.mean(miles):.1f}')
print(f'Receipts: min=${min(receipts):.2f}, max=${max(receipts):.2f}, avg=${statistics.mean(receipts):.2f}')
print(f'Outputs: min=${min(outputs):.2f}, max=${max(outputs):.2f}, avg=${statistics.mean(outputs):.2f}')

# Look at per diem patterns
print('\nPer diem analysis (output/days):')
per_diem_by_duration = defaultdict(list)
for case in cases:
    duration = case['input']['trip_duration_days']
    output = case['expected_output']
    per_diem = output / duration
    per_diem_by_duration[duration].append(per_diem)

for duration in sorted(per_diem_by_duration.keys())[:10]:
    per_diems = per_diem_by_duration[duration]
    avg_per_diem = statistics.mean(per_diems)
    print(f'  {duration} days: avg ${avg_per_diem:.2f}/day (from {len(per_diems)} cases)')

# Look at mileage patterns  
print('\nMileage analysis (assuming some base per diem):')
base_per_diem = 100  # From Lisa's interview
for case in cases[:10]:
    inp = case['input']
    output = case['expected_output']
    base_amount = inp['trip_duration_days'] * base_per_diem
    remaining = output - base_amount
    if inp['miles_traveled'] > 0:
        per_mile = remaining / inp['miles_traveled']
        print(f'  {inp["trip_duration_days"]}d, {inp["miles_traveled"]}mi, ${inp["total_receipts_amount"]:.2f} -> remaining ${remaining:.2f}, ${per_mile:.3f}/mile')

# Look for efficiency patterns (miles per day)
print('\nEfficiency analysis:')
efficiency_groups = defaultdict(list)
for case in cases:
    inp = case['input']
    if inp['trip_duration_days'] > 0:
        miles_per_day = inp['miles_traveled'] / inp['trip_duration_days']
        efficiency_groups[int(miles_per_day // 50) * 50].append(case)

for efficiency_range in sorted(efficiency_groups.keys())[:6]:
    group_cases = efficiency_groups[efficiency_range]
    avg_output = statistics.mean([case['expected_output'] for case in group_cases])
    print(f'  {efficiency_range}-{efficiency_range+49} mi/day: {len(group_cases)} cases, avg output ${avg_output:.2f}')