#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation 
    Conservative tiered approach - best performing formula
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base calculation: $75/day + $0.40/mile
    base = 75 * days + 0.4 * miles
    
    # Conservative tiered receipt handling
    if receipts <= 200:
        receipt_contrib = receipts * 0.6
    elif receipts <= 800:
        receipt_contrib = 200 * 0.6 + (receipts - 200) * 0.4
    elif receipts <= 1500:
        receipt_contrib = 200 * 0.6 + 600 * 0.4 + (receipts - 800) * 0.2
    else:
        receipt_contrib = 200 * 0.6 + 600 * 0.4 + 700 * 0.2 + (receipts - 1500) * 0.1
    
    total = base + receipt_contrib
    
    # 5-day bonus (from interviews)
    if days == 5:
        total += 50
    
    return round(max(total, 50), 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = calculate_reimbursement(days, miles, receipts)
        print(result)
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)