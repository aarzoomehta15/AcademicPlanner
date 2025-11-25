# modules/planner_logic.py

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple

from ml.rl_agent import RLAgent


class PlannerLogic:
    """
    Handles:
    - Time-slot management (50-minute slots from 8 AM)
    - Estimating available study hours (simple version)
    - Using RLAgent to distribute study hours across subjects
    """

    def __init__(self):
        # RL agent shared across planner calls
        self.agent = RLAgent()

        # 50-minute slots starting at 8:00
        self.slot_length_min = 50
        self.start_time = time(8, 0)

    # ---------------------------------------------------------
    # Time slot helpers
    # ---------------------------------------------------------

    def generate_slots_for_day(self, num_slots: int = 9) -> List[Tuple[str, str]]:
        """
        Generate a list of (start_str, end_str) time slots for a day.
        Each slot is 50 minutes starting from 8:00 AM by default.
        Example: [("08:00", "08:50"), ("08:50", "09:40"), ...]
        """
        slots = []
        current = datetime.combine(datetime.today(), self.start_time)
        delta = timedelta(minutes=self.slot_length_min)

        for _ in range(num_slots):
            start_str = current.strftime("%H:%M")
            end_dt = current + delta
            end_str = end_dt.strftime("%H:%M")
            slots.append((start_str, end_str))
            current = end_dt

        return slots

    def estimate_available_study_hours(
        self,
        total_wake_hours: float = 16.0,
        class_slots_today: int = 4,
        buffer_hours: float = 3.0,
    ) -> float:
        """
        Very simple approximation:

        available_hours = total_wake_hours - class_time - buffer

        - total_wake_hours: e.g. 16 hours (8 AM to 12 AM)
        - class_slots_today: number of 50-min slots with college classes
        - buffer_hours: meals, travel, rest

        Later, you will replace class_slots_today with real value
        from the timetable grid in Settings.
        """
        class_time_hours = (class_slots_today * self.slot_length_min) / 60.0
        avail = total_wake_hours - class_time_hours - buffer_hours
        if avail < 2.0:
            avail = 2.0  # minimum study time
        return round(avail, 2)

    # ---------------------------------------------------------
    # Main planner: allocate hours to subjects
    # ---------------------------------------------------------

    def generate_daily_plan(
        self,
        subjects: List[str],
        class_slots_today: int,
        total_wake_hours: float = 16.0,
    ) -> Dict[str, float]:
        """
        Return a dict mapping subject -> allocated study hours for today.

        Steps:
        1. Estimate available study hours from timetable info.
        2. Give base_hours = available / N per subject.
        3. Ask RLAgent to adjust hours per subject.
        4. Normalise so that sum(hours) ≈ available_hours.
        """
        if not subjects:
            return {}

        available_hours = self.estimate_available_study_hours(
            total_wake_hours=total_wake_hours,
            class_slots_today=class_slots_today,
        )

        n = len(subjects)
        base_hours = available_hours / n

        # RL-adjusted hours
        raw_hours: Dict[str, float] = {}
        for subj in subjects:
            adjusted, _ = self.agent.adjust_hours(subj, base_hours)
            raw_hours[subj] = adjusted

        # Normalise so total ≈ available_hours
        total_raw = sum(raw_hours.values())
        if total_raw <= 0:
            # fallback equal distribution
            return {s: round(available_hours / n, 2) for s in subjects}

        factor = available_hours / total_raw
        plan = {s: round(h * factor, 2) for s, h in raw_hours.items()}
        return plan

    # ---------------------------------------------------------
    # Feedback to RL (to call after user marks completion)
    # ---------------------------------------------------------

    def apply_feedback_for_day(
        self,
        allocations: Dict[str, float],
        completion_map: Dict[str, str],
    ):
        """
        allocations: {subject: hours_for_today}
        completion_map: {subject: "not" / "half" / "almost"}

        This will:
        - convert completion to reward
        - update RL model
        """
        for subj, hours in allocations.items():
            completion = completion_map.get(subj, "half")
            # For now we treat prev_hours = hours and new_hours = hours,
            # because adjustment is applied the next day.
            self.agent.apply_feedback(
                subject=subj,
                prev_hours=hours,
                new_hours=hours,
                completion=completion,
            )
