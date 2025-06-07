#!/usr/bin/env python3

import json
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== BUILDING ULTIMATE GENERALIZATION MODEL ===")

# Create the most sophisticated feature engineering possible
X = []
y = []

for case in cases:
    inp = case['input']
    output = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled'] 
    receipts = inp['total_receipts_amount']
    
    # Comprehensive feature engineering
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    receipts_per_mile = receipts / miles if miles > 0 else 0
    
    features = [
        # Basic features
        days, miles, receipts,
        miles_per_day, receipts_per_day, receipts_per_mile,
        
        # Log transforms (handle extreme values better)
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        
        # Square root transforms
        np.sqrt(days), np.sqrt(miles), np.sqrt(receipts),
        
        # Power transforms
        days**2, miles**2, receipts**2,
        days**0.5, miles**0.5, receipts**0.5,
        
        # Interaction effects (crucial for complex business rules)
        days * miles, days * receipts, miles * receipts,
        days * miles_per_day, days * receipts_per_day,
        miles * receipts_per_mile,
        
        # Three-way interactions
        days * miles * receipts / 10000,  # Scaled down
        
        # Categorical encodings for special cases
        1 if days == 1 else 0,      # Single day trips
        1 if days == 5 else 0,      # 5-day bonus (interview insight)
        1 if days >= 7 else 0,      # Long trips
        1 if days >= 10 else 0,     # Very long trips
        
        # Receipt thresholds (interview insights)
        1 if receipts < 50 else 0,       # Small receipts penalty
        1 if receipts > 1500 else 0,     # High receipts
        1 if receipts > 2000 else 0,     # Very high receipts
        
        # Mileage thresholds
        1 if miles < 100 else 0,         # Low mileage
        1 if miles > 500 else 0,         # High mileage
        1 if miles > 800 else 0,         # Very high mileage
        
        # Efficiency thresholds (Kevin's insights)
        1 if miles_per_day < 30 else 0,         # Very low efficiency
        1 if 80 <= miles_per_day <= 200 else 0, # Optimal efficiency
        1 if miles_per_day > 300 else 0,        # Very high efficiency
        
        # Binned features for non-linear relationships
        min(days, 14),                    # Days capped
        min(miles // 100, 15),           # Miles in hundreds
        min(receipts // 200, 12),        # Receipts in 200s
        
        # Ratio features
        (receipts / (days * 100)) if days > 0 else 0,  # Receipts vs expected per diem
        (miles / (days * 100)) if days > 0 else 0,     # Miles vs reasonable daily travel
        
        # Complex business rule proxies
        min(days * 75 + miles * 0.5, 2000),     # Capped standard calculation
        max(0, receipts - days * 150),           # Excess receipts over reasonable per diem
        max(0, miles - days * 200),              # Excess mileage over reasonable daily
        
        # Seasonal/periodic patterns (if any)
        days % 7,                         # Day of week pattern proxy
        (days + miles + int(receipts)) % 12,  # Monthly pattern proxy
    ]
    
    X.append(features)
    y.append(output)

X = np.array(X)
y = np.array(y)

print(f"Created {X.shape[1]} sophisticated features from {len(X)} cases")

# Use the most powerful ensemble model
model = GradientBoostingRegressor(
    n_estimators=500,           # More trees
    learning_rate=0.05,         # Slower learning for better generalization
    max_depth=8,                # Deep enough for complex patterns
    subsample=0.8,              # Prevent overfitting
    random_state=42,
    validation_fraction=0.2,    # Use validation for early stopping
    n_iter_no_change=20        # Stop if no improvement
)

print("Training ultimate model...")
model.fit(X, y)

# Test generalization capability
print("Testing model accuracy...")
predictions = model.predict(X)
errors = np.abs(predictions - y)
exact_matches = np.sum(errors < 0.01)
close_matches = np.sum(errors < 1.0)
avg_error = np.mean(errors)

print(f"Training accuracy: {exact_matches}/{len(y)} exact, {close_matches}/{len(y)} close")
print(f"Average error: ${avg_error:.2f}")

# Feature importance
feature_names = [
    'days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day', 'receipts_per_mile',
    'log_days', 'log_miles', 'log_receipts', 'sqrt_days', 'sqrt_miles', 'sqrt_receipts',
    'days²', 'miles²', 'receipts²', 'days^0.5', 'miles^0.5', 'receipts^0.5',
    'days*miles', 'days*receipts', 'miles*receipts', 'days*mpd', 'days*rpd', 'miles*rpm',
    'days*miles*receipts', 'single_day', '5day_bonus', 'long_trip', 'very_long',
    'small_receipts', 'high_receipts', 'very_high_receipts', 'low_miles', 'high_miles', 'very_high_miles',
    'low_efficiency', 'optimal_efficiency', 'high_efficiency', 'days_capped', 'miles_binned', 'receipts_binned',
    'receipts_vs_perdiem', 'miles_vs_daily', 'capped_standard', 'excess_receipts', 'excess_miles',
    'week_pattern', 'month_pattern'
]

print(f"\\nTop 10 most important features:")
importance_pairs = list(zip(feature_names, model.feature_importances_))
importance_pairs.sort(key=lambda x: x[1], reverse=True)

for i, (name, importance) in enumerate(importance_pairs[:10]):
    print(f"  {i+1}. {name}: {importance:.3f}")

# Generate the ultimate model
def extract_ultimate_features(days, miles, receipts):
    """Extract the ultimate feature set"""
    import numpy as np
    
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    receipts_per_mile = receipts / miles if miles > 0 else 0
    
    features = [
        days, miles, receipts, miles_per_day, receipts_per_day, receipts_per_mile,
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        np.sqrt(days), np.sqrt(miles), np.sqrt(receipts),
        days**2, miles**2, receipts**2, days**0.5, miles**0.5, receipts**0.5,
        days * miles, days * receipts, miles * receipts,
        days * miles_per_day, days * receipts_per_day, miles * receipts_per_mile,
        days * miles * receipts / 10000,
        1 if days == 1 else 0, 1 if days == 5 else 0, 1 if days >= 7 else 0, 1 if days >= 10 else 0,
        1 if receipts < 50 else 0, 1 if receipts > 1500 else 0, 1 if receipts > 2000 else 0,
        1 if miles < 100 else 0, 1 if miles > 500 else 0, 1 if miles > 800 else 0,
        1 if miles_per_day < 30 else 0, 1 if 80 <= miles_per_day <= 200 else 0, 1 if miles_per_day > 300 else 0,
        min(days, 14), min(miles // 100, 15), min(receipts // 200, 12),
        (receipts / (days * 100)) if days > 0 else 0, (miles / (days * 100)) if days > 0 else 0,
        min(days * 75 + miles * 0.5, 2000), max(0, receipts - days * 150), max(0, miles - days * 200),
        days % 7, (days + miles + int(receipts)) % 12,
    ]
    
    return features

# Save the model
import pickle
with open('/app/ultimate_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"\\nUltimate model saved!")
print(f"This model should generalize much better to private cases than a lookup table.")