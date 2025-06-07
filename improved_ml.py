#!/usr/bin/env python3

import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== ADVANCED ML MODEL ===")

# Prepare data with more sophisticated features
X = []
y = []

for case in cases:
    inp = case['input']
    output = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled'] 
    receipts = inp['total_receipts_amount']
    
    # Basic features
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    # Advanced features to handle extreme cases
    features = [
        days,
        miles,
        receipts,
        miles_per_day,
        receipts_per_day,
        
        # Non-linear transformations
        np.log1p(days),  # log transforms for better handling of extremes
        np.log1p(miles),
        np.log1p(receipts),
        np.sqrt(days),
        np.sqrt(miles),
        np.sqrt(receipts),
        
        # Interaction effects
        days * miles,
        days * receipts,
        miles * receipts,
        days * miles_per_day,
        days * receipts_per_day,
        
        # Higher order interactions
        days * days,
        miles * miles,
        receipts * receipts,
        (days * miles * receipts) / 10000,  # Three-way interaction scaled down
        
        # Categorical/threshold features
        1 if days == 1 else 0,
        1 if days == 5 else 0,
        1 if days >= 10 else 0,
        1 if receipts < 50 else 0,
        1 if receipts > 1500 else 0,
        1 if receipts > 2000 else 0,  # New threshold for extreme receipts
        1 if miles > 800 else 0,  # Extreme mileage flag
        1 if miles_per_day > 200 else 0,
        1 if miles_per_day < 30 else 0,  # Very low efficiency
        
        # Ratio features
        receipts / miles if miles > 0 else 0,
        miles / receipts if receipts > 0 else 0,
        
        # Binned features for better handling of non-linear relationships
        min(receipts // 200, 10),  # Receipt bucket (0-10)
        min(miles // 100, 15),     # Miles bucket (0-15)
        min(days, 14),             # Days capped at 14
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

# Try different models with more sophisticated tuning
models = {
    'Random Forest (tuned)': RandomForestRegressor(
        n_estimators=200, 
        max_depth=15, 
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=8,
        random_state=42
    ),
}

best_model = None
best_score = float('inf')

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    # Calculate error metrics
    errors = np.abs(predictions - y_test)
    avg_error = np.mean(errors)
    exact_matches = np.sum(errors < 0.01)
    close_matches = np.sum(errors < 1.0)
    max_error = np.max(errors)
    
    print(f"  Avg error: ${avg_error:.2f}")
    print(f"  Max error: ${max_error:.2f}")
    print(f"  Exact matches: {exact_matches}/{len(y_test)} ({exact_matches/len(y_test)*100:.1f}%)")
    print(f"  Close matches: {close_matches}/{len(y_test)} ({close_matches/len(y_test)*100:.1f}%)")
    
    if avg_error < best_score:
        best_score = avg_error
        best_model = model

# Test on the problematic cases
print(f"\nTesting on problematic cases:")
problematic_cases = [
    (1, 1082, 1809.49, 446.94),  # Case 996
    (8, 795, 1645.99, 644.69),   # Case 684
    (4, 69, 2321.49, 322.00),    # Case 152
]

for days, miles, receipts, expected in problematic_cases:
    # Extract features for this case
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    
    test_features = [
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
    
    predicted = best_model.predict([test_features])[0]
    error = abs(expected - predicted)
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f}: Expected ${expected:.2f}, Predicted ${predicted:.2f}, Error ${error:.2f}")

# Save the improved model
import pickle
with open('/app/trained_model_v2.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print(f"\nBest model saved to trained_model_v2.pkl")

# Also save the feature extraction function
feature_extraction_code = '''
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
'''

with open('/app/feature_extraction_v2.py', 'w') as f:
    f.write(feature_extraction_code)