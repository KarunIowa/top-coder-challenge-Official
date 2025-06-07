#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation based on pattern analysis
    """
    
    # Convert inputs to proper types
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base calculation appears to be highly dependent on trip duration
    # The per-day rate decreases dramatically as trip length increases
    
    # Duration-based per diem (from pattern analysis)
    if days == 1:
        base_per_day = 873.55
    elif days == 2:
        base_per_day = 523.12
    elif days == 3:
        base_per_day = 336.85
    elif days == 4:
        base_per_day = 304.49
    elif days == 5:
        base_per_day = 254.52
    elif days == 6:
        base_per_day = 227.75
    elif days == 7:
        base_per_day = 217.35
    elif days == 8:
        base_per_day = 180.33
    elif days == 9:
        base_per_day = 159.85
    elif days == 10:
        base_per_day = 149.61
    else:
        # Extrapolate for longer trips
        base_per_day = max(100, 200 - (days - 10) * 8)
    
    # Base amount from duration
    base_amount = base_per_day * days
    
    # Mileage calculation - appears to be tiered
    mileage_reimbursement = 0
    if miles <= 100:
        mileage_reimbursement = miles * 0.58
    elif miles <= 500:
        mileage_reimbursement = 100 * 0.58 + (miles - 100) * 0.45
    else:
        mileage_reimbursement = 100 * 0.58 + 400 * 0.45 + (miles - 500) * 0.35
    
    # Receipt handling - different treatment based on amount
    receipt_reimbursement = 0
    if receipts < 50:
        # Small receipts penalty
        receipt_reimbursement = -receipts * 0.5
    elif receipts < 200:
        # Low receipts - minimal benefit
        receipt_reimbursement = receipts * 0.1
    elif receipts < 500:
        # Medium receipts - better rate
        receipt_reimbursement = receipts * 0.3
    elif receipts < 1000:
        # Good receipt range
        receipt_reimbursement = receipts * 0.4
    elif receipts < 2000:
        # High receipts - diminishing returns
        receipt_reimbursement = receipts * 0.37
    else:
        # Very high receipts - penalty
        receipt_reimbursement = receipts * 0.22
    
    # Efficiency bonuses (miles per day)
    if days > 0:
        miles_per_day = miles / days
        efficiency_bonus = 0
        
        if 40 <= miles_per_day < 60:
            efficiency_bonus = 50
        elif 100 <= miles_per_day < 140:
            efficiency_bonus = 100
        elif 140 <= miles_per_day < 180:
            efficiency_bonus = 150
        elif 180 <= miles_per_day < 200:
            efficiency_bonus = 100  # Kevin's sweet spot
    else:
        efficiency_bonus = 0
    
    # Total calculation
    total_reimbursement = base_amount + mileage_reimbursement + receipt_reimbursement + efficiency_bonus
    
    # Ensure positive result
    total_reimbursement = max(total_reimbursement, 50)
    
    return round(total_reimbursement, 2)

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