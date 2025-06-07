#!/usr/bin/env python3

import sys
import math
import pickle
import numpy as np

# Try to load the trained model, fall back to simple model if not available
try:
    with open('/app/trained_model.pkl', 'rb') as f:
        trained_model = pickle.load(f)
    use_ml_model = True
except:
    use_ml_model = False

def extract_features(days, miles, receipts):
    """Extract features for ML model"""
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    features = [
        days,
        miles,
        receipts,
        miles_per_day,
        receipts_per_day,
        days * days,  # Non-linear day effects
        miles * miles,  # Non-linear mile effects
        receipts * receipts,  # Non-linear receipt effects
        days * miles,  # Interaction effects
        days * receipts,
        miles * receipts,
        1 if days == 5 else 0,  # 5-day bonus flag
        1 if receipts < 50 else 0,  # Small receipt flag
        1 if receipts > 1500 else 0,  # Large receipt flag
        1 if miles_per_day > 200 else 0,  # High efficiency flag
    ]
    
    return features

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Reverse-engineered reimbursement calculation using ML model
    """
    
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    if use_ml_model:
        # Use trained ML model
        features = extract_features(days, miles, receipts)
        prediction = trained_model.predict([features])[0]
        return round(max(prediction, 50), 2)
    else:
        # Fallback to improved hand-crafted model based on ML insights
        # The ML model showed interaction effects are very important
        
        # Base components
        base_amount = 50 * days  # Low base
        mileage_amount = 0.3 * miles  # Lower mileage rate
        
        # Receipt handling - non-linear based on ML insights  
        if receipts <= 500:
            receipt_amount = receipts * 0.4
        elif receipts <= 1000:
            receipt_amount = 500 * 0.4 + (receipts - 500) * 0.6
        else:
            receipt_amount = 500 * 0.4 + 500 * 0.6 + (receipts - 1000) * 0.3
        
        # Interaction effects (most important from ML)
        interaction_1 = (days * miles) * 0.02  # days*miles was important
        interaction_2 = (days * receipts) * 0.001  # days*receipts was important
        interaction_3 = (receipts * receipts) * 0.00001  # receipts² was important
        
        total = base_amount + mileage_amount + receipt_amount + interaction_1 + interaction_2 + interaction_3
        
        # 5-day bonus (was flagged as important)
        if days == 5:
            total += 50
            
        # Small receipt penalty
        if receipts < 50:
            total -= 30
            
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