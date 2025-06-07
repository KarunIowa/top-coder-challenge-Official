#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation 
    Based on extreme case analysis showing heavy receipt penalties
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base per diem model - appears to be around $75/day
    base_per_diem = 75 * days
    
    # Mileage calculation - around $0.30/mile base rate
    mileage_amount = 0.30 * miles
    
    # Receipt handling - CRITICAL INSIGHT: High receipts get heavily penalized
    if receipts <= 200:
        # Low receipts get good treatment
        receipt_contribution = receipts * 0.5
    elif receipts <= 500:
        # Medium receipts get moderate treatment  
        receipt_contribution = 200 * 0.5 + (receipts - 200) * 0.3
    elif receipts <= 1000:
        # Higher receipts start getting penalized
        receipt_contribution = 200 * 0.5 + 300 * 0.3 + (receipts - 500) * 0.2
    elif receipts <= 1500:
        # High receipts get more penalty
        receipt_contribution = 200 * 0.5 + 300 * 0.3 + 500 * 0.2 + (receipts - 1000) * 0.1
    else:
        # Very high receipts (>$1500) get almost nothing additional
        receipt_contribution = 200 * 0.5 + 300 * 0.3 + 500 * 0.2 + 500 * 0.1 + (receipts - 1500) * 0.02
    
    # Base calculation
    total = base_per_diem + mileage_amount + receipt_contribution
    
    # Efficiency bonuses and penalties
    if days > 0:
        miles_per_day = miles / days
        
        # Kevin's efficiency insights - moderate miles per day is optimal
        if 80 <= miles_per_day <= 150:
            total += 50  # Efficiency bonus
        elif miles_per_day > 300:
            # Very high miles per day gets penalized (like the 1-day 1082 mile case)
            total *= 0.7
        elif miles_per_day < 20:
            total += 30  # Low mileage bonus
    
    # Trip duration effects from interviews
    if days == 5:
        # 5-day bonus mentioned multiple times
        total += 100
    elif days == 1:
        # 1-day trips seem to get slight bonus for low expenses
        if receipts < 100:
            total += 30
    elif days >= 10:
        # Long trips get penalized
        total *= 0.9
    
    # Additional penalties for extreme cases
    if receipts > 2000:
        # Extreme receipt penalty (like the $2321 case)
        total *= 0.6
    
    if days == 1 and miles > 800:
        # Extreme single-day mileage penalty
        total *= 0.6
    
    # Small receipt penalty mentioned by Dave
    if receipts < 50:
        total -= 20
    
    # Ensure reasonable minimum
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