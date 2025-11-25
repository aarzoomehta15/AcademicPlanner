# modules/ml_model.py
import numpy as np
from sklearn.linear_model import LogisticRegression
from modules.goals_db import GoalsHelper
from modules.attendance_db import AttendanceDB
from modules.todo_db import ToDoDB

class StudyPredictor:
    """ ML model recommending which subject to focus on based on
    scores, attendance & task completion """
    
    def __init__(self):
        self.model = LogisticRegression()
        self.goals = GoalsHelper()
        self.att = AttendanceDB()
        self.todo = ToDoDB()

    def prepare_training_data(self, user_id):
        """Collect the features for ML training"""
        score_rows = self.goals.get_subject_totals(user_id)  # {subject: percent}
        attendance_rows = self.att.get_attendance_percent(user_id)  # {subject: percent}
        completion_rows = self.todo.get_completion_percent(user_id)  # {subject: percent}

        data = []
        for subj, score_pct in score_rows.items():
            entry = {
                "subject": subj,
                "avg": score_pct,
                "attendance": attendance_rows.get(subj, 0),
                "completion": completion_rows.get(subj, 0)
            }
            # weak label
            entry["label"] = 1 if (entry["avg"] < 60 or entry["attendance"] < 75) else 0
            data.append(entry)
        return data

    def train(self, training_data):
        """Train logistic regression model"""
        if len(training_data) < 2:
            return False
        X = [(d["avg"], d["attendance"], d["completion"]) for d in training_data]
        y = [d["label"] for d in training_data]
        self.model.fit(X, y)
        return True

    def recommend(self, training_data):
        """Return subjects predicted as weak"""
        weak = []
        for d in training_data:
            X = np.array([[d["avg"], d["attendance"], d["completion"]]])
            prediction = self.model.predict(X)[0]
            if prediction == 1:
                weak.append(d["subject"])
        return weak
