import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pickle

# Load dataset
df = pd.read_csv("water_data_big.csv")

# Convert date into useful features
df["date"] = pd.to_datetime(df["date"])
df["day"] = df["date"].dt.day
df["month"] = df["date"].dt.month

# Convert zone into numbers
df["zone"] = df["zone"].map({
    "Residential_A": 0,
    "Commercial_B": 1,
    "Industrial_C": 2
})

# Features and target
X = df[["zone","population","temperature","rainfall","is_weekend","is_festival","day","month"]]
y = df["water_supply"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("Model trained successfully")
print("MAE:", int(mae))

# Save model
pickle.dump(model, open("model.pkl","wb"))