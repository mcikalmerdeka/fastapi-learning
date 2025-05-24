import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the Iris dataset
datset_path = "./data/iris.csv"
df = pd.read_csv(datset_path)

# # Check the first few rows of the dataset
# print(df.head())

# # Check the value counts of the target column
# print(df["species"].value_counts())

# Change the target column to numerical values
df["species"] = df["species"].map({"setosa": 0, "versicolor": 1, "virginica": 2})

# Split the dataset into features and tatget
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Random Forest Classifier and train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict the test set results
y_pred = model.predict(X_test)
print(y_pred)

# Evaluate the model
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100}%")
print(f"Classification Report: {classification_report(y_test, y_pred)}")

# Save the model
model_path = "./models/iris_model.joblib"
joblib.dump(model, model_path)





