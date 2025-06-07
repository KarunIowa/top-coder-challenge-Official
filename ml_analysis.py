#!/usr/bin/env python3

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("=== MACHINE LEARNING APPROACH ===")

# Prepare data
X = []
y = []

for case in cases:
    inp = case['input']
    output = case['expected_output']
    
    # Basic features
    days = inp['trip_duration_days']
    miles = inp['miles_traveled'] 
    receipts = inp['total_receipts_amount']
    
    # Engineered features based on interview insights
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
    
    X.append(features)
    y.append(output)

X = np.array(X)
y = np.array(y)

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")

# Split data
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Try different models
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
}

best_model = None
best_score = float('inf')

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    # Calculate error metrics
    errors = np.abs(predictions - y_test)
    avg_error = np.mean(errors)
    exact_matches = np.sum(errors < 0.01)
    close_matches = np.sum(errors < 1.0)
    
    print(f"\n{name}:")
    print(f"  Avg error: ${avg_error:.2f}")
    print(f"  Exact matches: {exact_matches}/{len(y_test)} ({exact_matches/len(y_test)*100:.1f}%)")
    print(f"  Close matches: {close_matches}/{len(y_test)} ({close_matches/len(y_test)*100:.1f}%)")
    
    if avg_error < best_score:
        best_score = avg_error
        best_model = model

# Use best model to analyze feature importance
if hasattr(best_model, 'feature_importances_'):
    print(f"\nFeature importance (Random Forest):")
    feature_names = ['days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day',
                    'days²', 'miles²', 'receipts²', 'days*miles', 'days*receipts', 
                    'miles*receipts', '5day_bonus', 'small_receipt', 'large_receipt', 'high_efficiency']
    
    for i, importance in enumerate(best_model.feature_importances_):
        if importance > 0.01:  # Only show important features
            print(f"  {feature_names[i]}: {importance:.3f}")

# Test on some examples
print(f"\nTesting best model on first 10 cases:")
for i in range(min(10, len(X_test))):
    actual_output = y_test[i]
    predicted_output = best_model.predict([X_test[i]])[0]
    error = abs(actual_output - predicted_output)
    
    # Get original inputs for this test case
    test_idx = train_size + i
    inp = cases[test_idx]['input']
    
    print(f"Case {test_idx+1}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${actual_output:.2f}, Predicted: ${predicted_output:.2f}, Error: ${error:.2f}")

# Try to extract simple rules from the Random Forest
if isinstance(best_model, RandomForestRegressor):
    print(f"\nTrying to extract simple rules...")
    
    # Test some simple patterns
    test_cases = [
        [5, 200, 500, 40, 100, 25, 40000, 250000, 1000, 2500, 100000, 1, 0, 0, 0],  # 5-day trip
        [3, 100, 300, 33.3, 100, 9, 10000, 90000, 300, 900, 30000, 0, 0, 0, 0],     # 3-day trip
        [1, 50, 25, 50, 25, 1, 2500, 625, 50, 25, 1250, 0, 1, 0, 0],                # 1-day, small receipt
    ]
    
    for i, test_case in enumerate(test_cases):
        pred = best_model.predict([test_case])[0]
        print(f"  Test pattern {i+1}: ${pred:.2f}")

# Export the trained model for use in our script
import pickle
with open('/app/trained_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print(f"\nBest model saved to trained_model.pkl")
print(f"To use: load the model and predict with same feature engineering")