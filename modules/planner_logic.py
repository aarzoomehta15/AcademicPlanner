from __future__ import annotations
from datetime import datetime, time, timedelta
from typing import List, Dict

from modules.goals_db import GoalsHelper
from modules.attendance_db import AttendanceDB
from ml.study_predictor import StudyHourPredictor

class PlannerLogic:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.predictor = StudyHourPredictor()
        self.predictor.load_model()
        self.slot_length_min = 50
        self.start_time = time(8, 0)

    def estimate_available_study_hours(self, total_wake_hours=16.0, class_slots_today=4, buffer_hours=3.0):
        class_time = (class_slots_today * self.slot_length_min) / 60.0
        avail = total_wake_hours - class_time - buffer_hours
        return round(max(2.0, avail), 2)

    def generate_daily_plan(self, subjects: List[str], class_slots_today: int) -> Dict[str, float]:
        if not subjects: return {}

        # Refresh Data
        goals_db = GoalsHelper()
        att_db = AttendanceDB()

        available_hours = self.estimate_available_study_hours(class_slots_today=class_slots_today)
        
        scores_map = goals_db.get_subject_totals(self.user_id)
        # This now fetches the manual percentage you saved
        att_map = att_db.get_attendance_percent(self.user_id)

        raw_predictions = {}
        for subj in subjects:
            curr_score = scores_map.get(subj, 40.0) 
            att_pct = att_map.get(subj, 75.0) # Default 75 if not set
            
            target = goals_db.get_subject_target(self.user_id, subj)
            final_target = target if target else 100.0

            # Predict
            pred = self.predictor.predict_hours(curr_score, final_target, att_pct)
            raw_predictions[subj] = pred

        # Normalize
        total_predicted = sum(raw_predictions.values())
        
        if total_predicted <= 0:
            return {s: round(available_hours / len(subjects), 2) for s in subjects}

        factor = available_hours / total_predicted
        
        final_plan = {}
        for subj, h in raw_predictions.items():
            final_plan[subj] = round(h * factor, 2)

        return final_plan