#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation 
    New model based on deeper analysis
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Start with a much lower base - the original estimates were too high
    base_per_diem = 50 * days  # Much lower base
    
    # Mileage with more complex rules
    if miles <= 100:
        mileage_amount = miles * 0.8  # Higher rate for low mileage
    elif miles <= 300:
        mileage_amount = 100 * 0.8 + (miles - 100) * 0.5
    elif miles <= 600:
        mileage_amount = 100 * 0.8 + 200 * 0.5 + (miles - 300) * 0.3  
    else:
        mileage_amount = 100 * 0.8 + 200 * 0.5 + 300 * 0.3 + (miles - 600) * 0.6  # Higher again for very high mileage
    
    # Receipt handling with heavy penalties for high amounts
    if receipts <= 100:
        receipt_amount = receipts * 0.8  # Good rate for low receipts
    elif receipts <= 500:
        receipt_amount = 100 * 0.8 + (receipts - 100) * 0.2  # Heavy penalty for medium receipts
    elif receipts <= 1000:
        receipt_amount = 100 * 0.8 + 400 * 0.2 + (receipts - 500) * 0.4  # Better rate again
    elif receipts <= 1500:
        receipt_amount = 100 * 0.8 + 400 * 0.2 + 500 * 0.4 + (receipts - 1000) * 0.3
    else:
        # Heavy penalty for very high receipts
        receipt_amount = 100 * 0.8 + 400 * 0.2 + 500 * 0.4 + 500 * 0.3 + (receipts - 1500) * 0.1
    
    total = base_per_diem + mileage_amount + receipt_amount
    
    # Duration-based adjustments based on error analysis
    if days == 1:
        total *= 1.1  # 1-day trips seem to get bonuses
    elif days == 2:
        total *= 1.05
    elif days >= 10:
        total *= 0.9  # Long trips get penalties
    
    # Efficiency adjustments
    if days > 0:
        miles_per_day = miles / days
        if miles_per_day < 50:
            total += 30  # Low mileage bonus
        elif miles_per_day > 200:
            total -= 20  # High mileage penalty
    
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