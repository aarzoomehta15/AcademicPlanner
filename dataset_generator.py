import pandas as pd
import numpy as np
import os

def generate_data():
    if not os.path.exists("ml"): os.makedirs("ml")
    
    data = []
    for _ in range(2000):
        current = np.random.randint(20, 95)
        if current < 90:
            target = np.random.randint(current + 5, 100)
        else:
            target = 100
            
        gap = target - current
        attendance = np.random.randint(40, 100)
        
        # Logic: Base Gap + Weak Penalty + Attendance Penalty
        hours = (gap / 10) * 1.0 
        if current < 40: hours += 2.5
        elif current < 60: hours += 1.5
        if attendance < 60: hours += 1.0
            
        hours += np.random.normal(0, 0.2)
        hours = max(0.5, min(6.0, round(hours, 2)))
        
        data.append([current, target, gap, attendance, hours])

    df = pd.DataFrame(data, columns=["current_score", "target_score", "gap", "attendance", "recommended_hours"])
    df.to_csv("ml/student_study_data.csv", index=False)
    print("✅ New Dataset Generated")

if __name__ == "__main__":
    generate_data()