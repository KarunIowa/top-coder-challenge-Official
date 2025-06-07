#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation 
    Base model: $75/day + $0.50/mile + 0.5*receipts with refinements
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base calculation from analysis: $75/day + $0.50/mile + 50% of receipts
    base_per_diem = 75 * days
    mileage_amount = 0.50 * miles
    receipt_amount = 0.5 * receipts
    
    total = base_per_diem + mileage_amount + receipt_amount
    
    # From interviews, there seem to be some adjustments:
    
    # 1. Trip duration effects (from interview patterns)
    if days == 5:
        # 5-day bonus mentioned multiple times
        total *= 1.05
    elif days >= 8:
        # Longer trips seem to get penalized
        total *= 0.95
    
    # 2. Efficiency bonuses (miles per day)
    if days > 0:
        miles_per_day = miles / days
        if 100 <= miles_per_day <= 200:
            # Sweet spot mentioned by Kevin
            total *= 1.03
        elif miles_per_day > 300:
            # Too much driving penalty
            total *= 0.98
    
    # 3. Receipt handling refinements
    if receipts < 50:
        # Small receipt penalty mentioned by Dave
        total -= 20
    elif receipts > 1500:
        # High receipt diminishing returns
        total = base_per_diem + mileage_amount + 0.4 * receipts
    
    # 4. Some randomness/variation mentioned - add small adjustments
    # Based on input characteristics to simulate system quirks
    variation = (days * 3 + int(miles) % 10 + int(receipts * 100) % 7) % 20 - 10
    total += variation
    
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