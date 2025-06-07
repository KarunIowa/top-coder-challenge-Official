#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation 
    Balanced model based on comprehensive analysis
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base model: $75/day + $0.30/mile
    base_per_diem = 75 * days
    mileage_amount = 0.30 * miles
    
    # Receipt handling - the key insight is that high mileage justifies high receipts
    miles_per_day = miles / days if days > 0 else 0
    
    # Calculate receipt rate based on work intensity (miles)
    if miles < 200:
        # Low mileage trips get lower receipt rates
        if receipts <= 500:
            receipt_rate = 0.4
        elif receipts <= 1000:
            receipt_rate = 0.3
        else:
            receipt_rate = 0.1  # Heavy penalty for high receipts with low work
    elif miles < 500:
        # Medium mileage trips get moderate rates
        if receipts <= 1000:
            receipt_rate = 0.5
        elif receipts <= 1500:
            receipt_rate = 0.4
        else:
            receipt_rate = 0.2
    else:
        # High mileage trips can justify high receipts
        if receipts <= 1500:
            receipt_rate = 0.6
        elif receipts <= 2000:
            receipt_rate = 0.5
        else:
            receipt_rate = 0.4  # Still good rate even for very high receipts
    
    receipt_contribution = receipts * receipt_rate
    
    # Base calculation
    total = base_per_diem + mileage_amount + receipt_contribution
    
    # Additional bonuses and adjustments based on interview insights
    
    # 5-day bonus (mentioned multiple times in interviews)
    if days == 5:
        total += 100
    
    # Efficiency bonuses for optimal ranges (Kevin's insights)
    if 80 <= miles_per_day <= 200:
        total += 50
    elif miles_per_day > 400:
        # Very high efficiency gets bonus (high-work single days)
        total += 100
    
    # Trip duration adjustments
    if days == 1:
        # 1-day trips get bonus for being efficient
        total += 50
    elif days >= 10:
        # Long trips get slight penalty
        total *= 0.95
    
    # Small receipt penalty (Dave's observation)
    if receipts < 50:
        total -= 30
    
    # Final edge case handling
    # Only penalize the truly problematic cases (very high receipts with very low work)
    if receipts > 2000 and miles < 100:
        total *= 0.5  # This targets the real outliers like 4d, 69mi, $2321
    
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