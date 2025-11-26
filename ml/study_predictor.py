import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class StudyHourPredictor:
    def __init__(self):
        self.model = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.base_dir, "student_study_data.csv")
        self.model_path = os.path.join(self.base_dir, "study_model.pkl")

    def train_model(self):
        if not os.path.exists(self.data_path):
            print("Dataset not found. Please run dataset_generator.py first.")
            return

        df = pd.read_csv(self.data_path)
        X = df[["current_score", "target_score", "gap", "attendance"]]
        y = df["recommended_hours"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        joblib.dump(self.model, self.model_path)
        print("✅ Model Trained Successfully")

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            print("Model not found, training new one...")
            self.train_model()

    def predict_hours(self, current_score, target_score, attendance_pct):
        if self.model is None:
            self.load_model()
        
        gap = max(0, target_score - current_score)
        features = pd.DataFrame([{
            "current_score": current_score,
            "target_score": target_score,
            "gap": gap,
            "attendance": attendance_pct
        }])
        
        prediction = self.model.predict(features)[0]
        return round(prediction, 2)