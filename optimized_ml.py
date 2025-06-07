#!/usr/bin/env python3

import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
import warnings
warnings.filterwarnings('ignore')

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== OPTIMIZED ML MODEL ===")

# Prepare sophisticated features
X = []
y = []

for case in cases:
    inp = case['input']
    output = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Advanced feature engineering
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    # Categorical features for different calculation paths
    short_trip = 1 if days <= 3 else 0
    medium_trip = 1 if 4 <= days <= 7 else 0
    long_trip = 1 if days >= 8 else 0
    
    low_miles = 1 if miles < 200 else 0
    medium_miles = 1 if 200 <= miles < 600 else 0
    high_miles = 1 if miles >= 600 else 0
    
    low_receipts = 1 if receipts < 500 else 0
    medium_receipts = 1 if 500 <= receipts < 1500 else 0
    high_receipts = 1 if receipts >= 1500 else 0
    
    # Binned features for non-linear relationships
    days_binned = min(days, 14)
    miles_binned = min(int(miles // 100), 15)
    receipts_binned = min(int(receipts // 200), 15)
    
    features = [
        days, miles, receipts,
        miles_per_day, receipts_per_day,
        
        # Log transforms for better scaling
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        
        # Polynomial features (but constrained)
        min(days ** 2, 200),
        min(miles ** 2 / 10000, 200),  # Scale down
        min(receipts ** 2 / 100000, 200),  # Scale down
        
        # Interaction terms (scaled)
        days * miles / 100,
        days * receipts / 1000,
        miles * receipts / 10000,
        
        # Categorical features
        short_trip, medium_trip, long_trip,
        low_miles, medium_miles, high_miles,
        low_receipts, medium_receipts, high_receipts,
        
        # Special flags
        1 if days == 5 else 0,  # 5-day bonus
        1 if receipts < 50 else 0,  # Small receipt penalty
        1 if miles_per_day > 200 else 0,  # High efficiency
        
        # Binned features
        days_binned, miles_binned, receipts_binned,
        
        # Ratio features
        receipts / max(miles, 1),
        miles / max(receipts, 1),
        receipts / max(days, 1),
    ]
    
    X.append(features)
    y.append(output)

X = np.array(X)
y = np.array(y)

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")

# Split data
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Hyperparameter tuning for Random Forest
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

print("Performing hyperparameter tuning...")
rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='neg_mean_absolute_error', n_jobs=-1, verbose=1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"Best parameters: {grid_search.best_params_}")

# Test the model
predictions = best_model.predict(X_test)
errors = np.abs(predictions - y_test)
avg_error = np.mean(errors)
exact_matches = np.sum(errors < 0.01)
close_matches = np.sum(errors < 1.0)
max_error = np.max(errors)

print(f"\nOptimized Random Forest results:")
print(f"  Average error: ${avg_error:.2f}")
print(f"  Max error: ${max_error:.2f}")
print(f"  Exact matches: {exact_matches}/{len(y_test)}")
print(f"  Close matches: {close_matches}/{len(y_test)}")

# Test on problematic cases
problematic_inputs = [
    [8, 795, 1645.99],
    [5, 516, 1878.49],
    [4, 87, 2463.92],
    [4, 84, 2243.12],
    [1, 1082, 1809.49],
]

problematic_expected = [644.69, 669.85, 1413.52, 1392.10, 446.94]

print(f"\nTesting on problematic cases:")
for i, (inp, expected) in enumerate(zip(problematic_inputs, problematic_expected)):
    days, miles, receipts = inp
    
    # Extract features for this case
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    short_trip = 1 if days <= 3 else 0
    medium_trip = 1 if 4 <= days <= 7 else 0
    long_trip = 1 if days >= 8 else 0
    
    low_miles = 1 if miles < 200 else 0
    medium_miles = 1 if 200 <= miles < 600 else 0
    high_miles = 1 if miles >= 600 else 0
    
    low_receipts = 1 if receipts < 500 else 0
    medium_receipts = 1 if 500 <= receipts < 1500 else 0
    high_receipts = 1 if receipts >= 1500 else 0
    
    days_binned = min(days, 14)
    miles_binned = min(int(miles // 100), 15)
    receipts_binned = min(int(receipts // 200), 15)
    
    test_features = [
        days, miles, receipts, miles_per_day, receipts_per_day,
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        min(days ** 2, 200), min(miles ** 2 / 10000, 200), min(receipts ** 2 / 100000, 200),
        days * miles / 100, days * receipts / 1000, miles * receipts / 10000,
        short_trip, medium_trip, long_trip, low_miles, medium_miles, high_miles,
        low_receipts, medium_receipts, high_receipts,
        1 if days == 5 else 0, 1 if receipts < 50 else 0, 1 if miles_per_day > 200 else 0,
        days_binned, miles_binned, receipts_binned,
        receipts / max(miles, 1), miles / max(receipts, 1), receipts / max(days, 1),
    ]
    
    predicted = best_model.predict([test_features])[0]
    error = abs(expected - predicted)
    
    print(f"  Case {i+1}: {days}d, {miles:.0f}mi, ${receipts:.2f}")
    print(f"    Expected: ${expected:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}")

# Save the optimized model
import pickle
with open('/app/trained_model_optimized.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print(f"\nOptimized model saved to trained_model_optimized.pkl")

# Generate feature extraction code for the optimized model
feature_code = '''
def extract_features_optimized(days, miles, receipts):
    """Extract features for optimized ML model"""
    import numpy as np
    
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    short_trip = 1 if days <= 3 else 0
    medium_trip = 1 if 4 <= days <= 7 else 0
    long_trip = 1 if days >= 8 else 0
    
    low_miles = 1 if miles < 200 else 0
    medium_miles = 1 if 200 <= miles < 600 else 0
    high_miles = 1 if miles >= 600 else 0
    
    low_receipts = 1 if receipts < 500 else 0
    medium_receipts = 1 if 500 <= receipts < 1500 else 0
    high_receipts = 1 if receipts >= 1500 else 0
    
    days_binned = min(days, 14)
    miles_binned = min(int(miles // 100), 15)
    receipts_binned = min(int(receipts // 200), 15)
    
    features = [
        days, miles, receipts, miles_per_day, receipts_per_day,
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        min(days ** 2, 200), min(miles ** 2 / 10000, 200), min(receipts ** 2 / 100000, 200),
        days * miles / 100, days * receipts / 1000, miles * receipts / 10000,
        short_trip, medium_trip, long_trip, low_miles, medium_miles, high_miles,
        low_receipts, medium_receipts, high_receipts,
        1 if days == 5 else 0, 1 if receipts < 50 else 0, 1 if miles_per_day > 200 else 0,
        days_binned, miles_binned, receipts_binned,
        receipts / max(miles, 1), miles / max(receipts, 1), receipts / max(days, 1),
    ]
    
    return features
'''

with open('/app/feature_extraction_optimized.py', 'w') as f:
    f.write(feature_code)