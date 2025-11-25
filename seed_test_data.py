import sqlite3
from datetime import date, timedelta
import random

DB_PATH = "academic.db"   # same file your app uses


SUBJECTS = ["CAO", "ML", "IP", "CN", "SE"]
WEAK_SUBJECTS = ["CN", "SE"]   # lower attendance & marks here


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) Clean existing data (so we start fresh)
    #    If a table doesn't exist yet, ignore the error.
    for table in ["todo", "progress", "timetable", "attendance", "subjects", "users"]:
        try:
            cur.execute(f"DELETE FROM {table};")
        except sqlite3.OperationalError:
            # table might not exist yet, that's fine
            pass

    # 2) Insert 2 users
    users = [
        (1, "Anshika", "anshika", "anshika@example.com", "anshika"),
        (2, "Rahul", "rahul", "rahul@example.com", "rahul123"),
    ]
    cur.executemany(
        "INSERT INTO users(id, name, username, email, password) VALUES (?,?,?,?,?)",
        users,
    )

    # 3) Insert subjects for both users
    subject_rows = []
    for uid in [1, 2]:
        for s in SUBJECTS:
            subject_rows.append((uid, s))
    cur.executemany(
        "INSERT INTO subjects(user_id, subject) VALUES (?,?)",
        subject_rows,
    )

    # 4) Attendance per subject (CN, SE < 75%, others >= 80%)
    #    Schema assumed: attendance(user_id, subject, attended, total)
    attendance_rows = []
    for uid in [1, 2]:
        for s in SUBJECTS:
            total = 40
            if s in WEAK_SUBJECTS:
                attended = random.randint(20, 28)  # ~50–70%
            else:
                attended = random.randint(32, 38)  # >= 80%
            attendance_rows.append((uid, s, attended, total))

    try:
        cur.executemany(
            "INSERT INTO attendance(user_id, subject, attended, total) VALUES (?,?,?,?)",
            attendance_rows,
        )
    except sqlite3.OperationalError:
        # If your attendance table has a different schema, just skip seeding it.
        pass

    # 5) Simple weekly timetable (Mon–Fri: 4–5 slots/day)
    #    Schema assumed: timetable(user_id, weekday, slot, subject)
    timetable_rows = []
    # weekday: 0=Mon ... 6=Sun
    week_pattern = {
        0: ["CAO", "ML", "IP", "CN"],         # Mon
        1: ["ML", "CN", "SE", "CAO"],         # Tue
        2: ["CAO", "IP", "ML", "SE"],         # Wed
        3: ["ML", "IP", "CN"],                # Thu
        4: ["SE", "CN", "CAO", "ML"],         # Fri
    }

    for uid in [1, 2]:
        for weekday, subs in week_pattern.items():
            for slot_index, subj in enumerate(subs):
                timetable_rows.append((uid, weekday, slot_index, subj))

    try:
        cur.executemany(
            "INSERT INTO timetable(user_id, weekday, slot, subject) VALUES (?,?,?,?)",
            timetable_rows,
        )
    except sqlite3.OperationalError:
        # If schema differs, just skip.
        pass

    # 6) Progress / marks for last 30 days
    #    Schema: progress(user_id, subject, score, date)
    today = date.today()
    progress_rows = []
    for uid in [1, 2]:
        for s in SUBJECTS:
            for i in range(10):  # 10 assessments per subject
                d = today - timedelta(days=random.randint(0, 29))
                if s in WEAK_SUBJECTS:
                    score = random.randint(40, 65)  # weaker
                else:
                    score = random.randint(70, 95)  # stronger
                progress_rows.append((uid, s, score, d.strftime("%Y-%m-%d")))

    try:
        cur.executemany(
            "INSERT INTO progress(user_id, subject, score, date) VALUES (?,?,?,?)",
            progress_rows,
        )
    except sqlite3.OperationalError:
        # If the progress table schema is different, just skip.
        pass

    # 7) To-Do tasks for last 30 days for user 1 only
    #    Schema: todo(user_id, date, task_name, subject, duration, priority, status)
    todo_rows = []
    for days_ago in range(30):
        dt = today - timedelta(days=days_ago)
        dt_str = dt.strftime("%Y-%m-%d")

        # 2–4 tasks per day
        for _ in range(random.randint(2, 4)):
            subj = random.choice(SUBJECTS + [None, None])  # some tasks without subject
            if subj:
                task_name = f"Study {subj}"
            else:
                task_name = random.choice(
                    ["Gym", "Walk", "Read book", "Club meeting", "Watch lecture"]
                )
            duration = random.choice([30, 45, 60, 90])
            priority = random.choice(["Low", "Medium", "High"])
            status = random.choice(["pending", "half-done", "done"])
            todo_rows.append(
                (1, dt_str, task_name, subj, duration, priority, status)
            )

    try:
        cur.executemany(
            """
            INSERT INTO todo(user_id, date, task_name, subject, duration, priority, status)
            VALUES (?,?,?,?,?,?,?)
            """,
            todo_rows,
        )
    except sqlite3.OperationalError:
        # If todo schema changed, adjust manually later.
        pass

    conn.commit()
    conn.close()
    print("✅ Test data inserted into academic.db")


if __name__ == "__main__":
    main()
