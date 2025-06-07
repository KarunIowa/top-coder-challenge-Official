
def extract_features_v2(days, miles, receipts):
    """Extract features for improved ML model"""
    import numpy as np
    
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    features = [
        days, miles, receipts, miles_per_day, receipts_per_day,
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        np.sqrt(days), np.sqrt(miles), np.sqrt(receipts),
        days * miles, days * receipts, miles * receipts,
        days * miles_per_day, days * receipts_per_day,
        days * days, miles * miles, receipts * receipts,
        (days * miles * receipts) / 10000,
        1 if days == 1 else 0, 1 if days == 5 else 0, 1 if days >= 10 else 0,
        1 if receipts < 50 else 0, 1 if receipts > 1500 else 0, 1 if receipts > 2000 else 0,
        1 if miles > 800 else 0, 1 if miles_per_day > 200 else 0, 1 if miles_per_day < 30 else 0,
        receipts / miles if miles > 0 else 0, miles / receipts if receipts > 0 else 0,
        min(receipts // 200, 10), min(miles // 100, 15), min(days, 14),
    ]
    
    return features
