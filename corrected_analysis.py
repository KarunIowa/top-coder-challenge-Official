#!/usr/bin/env python3

import json
import statistics
import numpy as np

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== CORRECTED ANALYSIS ===")

# Let's look at the actual outputs more carefully
print("\nFirst 10 cases with detailed breakdown:")
for i, case in enumerate(cases[:10]):
    inp = case['input']
    output = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Calculate what the "per day" rate actually is
    per_day = output / days if days > 0 else 0
    
    # Calculate what the "per mile" rate would be if we subtract base per diem
    base_estimates = [50, 100, 120]  # Try different base estimates
    for base in base_estimates:
        remaining = output - (base * days)
        per_mile = remaining / miles if miles > 0 else 0
        
        if i == 0:  # Only print header once
            print(f"Base ${base}/day analysis:")
        
        if i < 3:  # Only show first few for each base
            print(f"  Case {i+1}: {days}d,{miles:.0f}mi,${receipts:.2f} -> ${output:.2f} | per_day=${per_day:.2f} | remaining=${remaining:.2f} | per_mile=${per_mile:.3f}")

# Check if it's a simpler model
print("\n=== TESTING SIMPLE MODELS ===")

# Test 1: Pure per diem model
print("\n1. Pure per diem model:")
for per_diem in [50, 75, 100, 120]:
    errors = []
    for case in cases[:100]:
        inp = case['input']
        expected = case['expected_output']
        estimate = per_diem * inp['trip_duration_days']
        error = abs(expected - estimate)
        errors.append(error)
    avg_error = statistics.mean(errors)
    print(f"   ${per_diem}/day: avg error ${avg_error:.2f}")

# Test 2: Per diem + fixed mileage rate
print("\n2. Per diem + mileage model:")
for per_diem in [50, 75, 100]:
    for mileage_rate in [0.20, 0.30, 0.40, 0.50, 0.58]:
        errors = []
        for case in cases[:100]:
            inp = case['input']
            expected = case['expected_output']
            estimate = per_diem * inp['trip_duration_days'] + mileage_rate * inp['miles_traveled']
            error = abs(expected - estimate)
            errors.append(error)
        avg_error = statistics.mean(errors)
        print(f"   ${per_diem}/day + ${mileage_rate:.2f}/mile: avg error ${avg_error:.2f}")

# Test 3: Look for simple receipt inclusion
print("\n3. Including receipts:")
best_error = float('inf')
best_params = None

for per_diem in [50, 75, 100]:
    for mileage_rate in [0.30, 0.40, 0.50]:
        for receipt_rate in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
            errors = []
            for case in cases[:100]:
                inp = case['input']
                expected = case['expected_output']
                estimate = (per_diem * inp['trip_duration_days'] + 
                           mileage_rate * inp['miles_traveled'] + 
                           receipt_rate * inp['total_receipts_amount'])
                error = abs(expected - estimate)
                errors.append(error)
            avg_error = statistics.mean(errors)
            
            if avg_error < best_error:
                best_error = avg_error
                best_params = (per_diem, mileage_rate, receipt_rate)

print(f"\nBest simple model: ${best_params[0]}/day + ${best_params[1]:.2f}/mile + {best_params[2]:.1f}*receipts")
print(f"Average error: ${best_error:.2f}")

# Test this best model on a few examples
print(f"\nTesting best model on first 10 cases:")
per_diem, mileage_rate, receipt_rate = best_params
for i, case in enumerate(cases[:10]):
    inp = case['input']
    expected = case['expected_output']
    estimate = (per_diem * inp['trip_duration_days'] + 
               mileage_rate * inp['miles_traveled'] + 
               receipt_rate * inp['total_receipts_amount'])
    error = abs(expected - estimate)
    print(f"Case {i+1}: Expected ${expected:.2f}, Estimated ${estimate:.2f}, Error ${error:.2f}")