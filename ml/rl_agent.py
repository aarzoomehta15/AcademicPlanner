# ml/rl_agent.py

import os
import json
import csv
import random
from collections import defaultdict
from datetime import datetime


class RLAgent:
    """
    Simple tabular Q-learning agent to decide how to adjust
    study hours for each subject.

    - State: integer performance level per subject (0 = weak, 1 = medium, 2 = strong)
      (You can later update state based on MST scores, attendance etc.)
    - Actions: "dec", "same", "inc"
    - Reward: based on task completion feedback for that subject.

    This agent:
    - Stores Q-table in JSON (ml/rl_state.json)
    - Logs transitions in CSV (ml/data.csv)
    """

    ACTIONS = ["dec", "same", "inc"]

    def __init__(
        self,
        alpha: float = 0.3,    # learning rate
        gamma: float = 0.9,    # discount factor
        epsilon: float = 0.2,  # exploration rate
        state_path: str | None = None,
        log_path: str | None = None,
        min_hours: float = 0.5,
        max_hours: float = 4.0,
        step_size: float = 0.5,
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_hours = min_hours
        self.max_hours = max_hours
        self.step_size = step_size

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.state_path = state_path or os.path.join(base_dir, "rl_state.json")
        self.log_path = log_path or os.path.join(base_dir, "data.csv")

        # Q-table: key = (subject, state, action) -> value
        self.q_table = defaultdict(float)
        # Subject state: subject -> 0/1/2 (weak/medium/strong)
        self.subject_state = defaultdict(lambda: 1)  # default medium

        self._load_state()
        self._ensure_log_header()

    # -----------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------

    def _load_state(self):
        """Load Q-table and subject states from JSON if present."""
        if not os.path.exists(self.state_path):
            return
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Load Q-table
            q_raw = data.get("q_table", {})
            for k_str, v in q_raw.items():
                # k_str = "subject|state|action"
                parts = k_str.split("|")
                if len(parts) != 3:
                    continue
                subject, state_str, action = parts
                state = int(state_str)
                self.q_table[(subject, state, action)] = float(v)

            # Load subject states
            subj_states = data.get("subject_state", {})
            for subj, st in subj_states.items():
                self.subject_state[subj] = int(st)
        except Exception as e:
            print("RLAgent: failed to load state:", e)

    def _save_state(self):
        """Save Q-table and subject states to JSON."""
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        q_raw = {}
        for (subject, state, action), value in self.q_table.items():
            key_str = f"{subject}|{state}|{action}"
            q_raw[key_str] = value

        data = {
            "q_table": q_raw,
            "subject_state": dict(self.subject_state),
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _ensure_log_header(self):
        """Ensure the CSV file has a header row."""
        if not os.path.exists(self.log_path):
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "date",
                        "subject",
                        "prev_hours",
                        "new_hours",
                        "completion",
                        "reward",
                        "state",
                        "action",
                    ]
                )

    # -----------------------------------------------------------
    # State helpers
    # -----------------------------------------------------------

    def get_state(self, subject: str) -> int:
        """
        Get current performance state for a subject.
        0 = weak, 1 = medium, 2 = strong.
        """
        return int(self.subject_state[subject])

    def set_state(self, subject: str, level: int):
        """
        Set performance state for a subject.
        This can later be updated using MST marks.
        """
        level = max(0, min(2, int(level)))
        self.subject_state[subject] = level
        self._save_state()

    # -----------------------------------------------------------
    # Q-learning helpers
    # -----------------------------------------------------------

    def _q(self, subject: str, state: int, action: str) -> float:
        return self.q_table[(subject, state, action)]

    def _best_action(self, subject: str, state: int) -> str:
        """Return the best action for (subject, state) according to Q-table."""
        values = []
        for a in self.ACTIONS:
            values.append((self._q(subject, state, a), a))
        max_q = max(v for v, _ in values)
        best_actions = [a for v, a in values if v == max_q]
        return random.choice(best_actions)

    def select_action(self, subject: str, state: int) -> str:
        """
        ε-greedy action selection:
        - With probability ε → random action (exploration)
        - Else → best known action (exploitation)
        """
        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        return self._best_action(subject, state)

    def update_q(self, subject: str, state: int, action: str, reward: float, next_state: int | None = None):
        """
        Standard Q-learning update:
        Q(s,a) ← Q(s,a) + α [ r + γ max_a' Q(s',a') - Q(s,a) ]
        """
        if next_state is None:
            next_state = state

        old_q = self._q(subject, state, action)
        # best future value
        best_future_q = max(self._q(subject, next_state, a) for a in self.ACTIONS)

        new_q = old_q + self.alpha * (reward + self.gamma * best_future_q - old_q)
        self.q_table[(subject, state, action)] = new_q
        self._save_state()

    # -----------------------------------------------------------
    # Hour adjustment + logging
    # -----------------------------------------------------------

    def adjust_hours(self, subject: str, base_hours: float) -> tuple[float, str]:
        """
        Given base hours for a subject, choose an action (dec/same/inc)
        and return new_hours, action.
        """
        state = self.get_state(subject)
        action = self.select_action(subject, state)

        if action == "dec":
            new_hours = max(self.min_hours, base_hours - self.step_size)
        elif action == "inc":
            new_hours = min(self.max_hours, base_hours + self.step_size)
        else:
            new_hours = base_hours

        return round(new_hours, 2), action

    def log_feedback(
        self,
        subject: str,
        prev_hours: float,
        new_hours: float,
        completion: str,
        reward: float,
        state: int,
        action: str,
    ):
        """
        Store one learning example in CSV.
        completion: "not", "half", "almost"
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    today,
                    subject,
                    prev_hours,
                    new_hours,
                    completion,
                    reward,
                    state,
                    action,
                ]
            )

    def apply_feedback(self, subject: str, prev_hours: float, new_hours: float, completion: str):
        """
        High-level helper:
        - completion: "not", "half", "done"
        - "not"  -> reward = -1
        - "half" -> reward = 0
        - "done" -> reward = +1
        """
        completion = completion.lower().strip()
        state = self.get_state(subject)

        if completion == "not":
            reward = -1.0
        elif completion == "half":
            reward = 0.0
        else:  # "done" or anything else considered good
            reward = 1.0

        # We don't change state here yet; later you can change state from MST performance.
        self.update_q(subject, state, action="same", reward=reward, next_state=state)
        self.log_feedback(
            subject=subject,
            prev_hours=prev_hours,
            new_hours=new_hours,
            completion=completion,
            reward=reward,
            state=state,
            action="same",
        )
