# app.py

import customtkinter as ctk
import hashlib
import os
import sqlite3
from tkinter import messagebox
from datetime import datetime, timedelta
from modules.progress_db import ProgressDB
from modules.users_db import UsersDB
from modules.tasks_db import TasksDB
from modules.subjects_db import SubjectsDB
from modules.goals_db import GoalsHelper
from modules.goals_db import GoalsHelper



def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class AcademicMentorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Academic Mentor - Study Planner")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        from db.session import get_session
        self.db = get_session()               # SQLAlchemy session
        self.conn = sqlite3.connect("academic.db")   # TEMP sqlite fallback

        self.primary_blue = "#5B8DF6"
        self.light_blue_bg = "#F2F6FF"
        self.dark_text = "#1F2A44"
        self.sidebar_bg = "#E5ECFF"

        self.current_user = None
        self.active_frame = None

        self.users_db_helper = UsersDB()
        self.tasks_db_helper = TasksDB()
        self.subjects_db_helper = SubjectsDB()

        self.show_login_frame()

    def register_user(self, name: str, username: str, email: str, password: str) -> bool:
        return self.users_db_helper.register_user(name, username, email, password)

    def authenticate_user(self, username: str, password: str):
        return self.users_db_helper.authenticate_user(username, password)

    def switch_frame(self, frame_class, **kwargs):
        if self.active_frame is not None:
            self.active_frame.destroy()
        self.active_frame = frame_class(self, **kwargs)
        self.active_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        self.switch_frame(LoginFrame)

    def show_signup_frame(self):
        self.switch_frame(SignupFrame)

    def show_main_app(self):
        self.switch_frame(MainAppFrame, user=self.current_user)

    def logout(self):
        self.current_user = None
        self.show_login_frame()


# ---------------- LOGIN SCREEN ----------------
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master: AcademicMentorApp):
        super().__init__(master)
        self.app = master
        self.configure(fg_color="white")

        title_font = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        subtitle_font = ctk.CTkFont(family="Segoe UI", size=14)
        label_font = ctk.CTkFont(family="Segoe UI", size=13)
        button_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

        left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.app.light_blue_bg, width=380)
        left_frame.pack(side="left", fill="both")

        title_label = ctk.CTkLabel(
            left_frame,
            text="Academic Mentor",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.app.dark_text,
        )
        title_label.place(relx=0.1, rely=0.3, anchor="w")

        subtitle_label = ctk.CTkLabel(
            left_frame,
            text="Smart planner for your semester.\nPlan • Track • Improve",
            font=subtitle_font,
            text_color="#44506B",
        )
        subtitle_label.place(relx=0.1, rely=0.4, anchor="w")

        right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        right_frame.pack(side="left", fill="both", expand=True)

        inner = ctk.CTkFrame(right_frame, fg_color="white", corner_radius=20)
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)

        heading = ctk.CTkLabel(inner, text="Welcome Back", font=title_font, text_color=self.app.dark_text)
        heading.pack(pady=(10, 3))

        self.username_entry = ctk.CTkEntry(inner, placeholder_text="Username", height=36, corner_radius=12)
        self.username_entry.pack(fill="x", padx=40, pady=(20, 10))

        self.password_entry = ctk.CTkEntry(inner, placeholder_text="Password", show="*", height=36, corner_radius=12)
        self.password_entry.pack(fill="x", padx=40, pady=(0, 20))

        login_btn = ctk.CTkButton(
            inner,
            text="Login",
            height=38,
            corner_radius=20,
            font=button_font,
            fg_color=self.app.primary_blue,
            hover_color="#4A7BE0",
            command=self.handle_login,
        )
        login_btn.pack(padx=40, pady=(0, 10), fill="x")

        signup_btn = ctk.CTkButton(
            inner,
            text="Create an Account",
            height=32,
            corner_radius=16,
            font=label_font,
            fg_color="white",
            border_width=1,
            border_color=self.app.primary_blue,
            text_color=self.app.primary_blue,
            command=self.app.show_signup_frame,
        )
        signup_btn.pack(pady=(10, 10))

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        user = self.app.authenticate_user(username, password)
        if user:
            self.app.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user['name']}!")
            self.app.show_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, "end")


# ---------------- SIGN UP SCREEN ----------------
class SignupFrame(ctk.CTkFrame):
    def __init__(self, master: AcademicMentorApp):
        super().__init__(master)
        self.app = master
        self.configure(fg_color="white")

        title_font = ctk.CTkFont(size=24, weight="bold")
        label_font = ctk.CTkFont(size=13)
        button_font = ctk.CTkFont(size=13, weight="bold")

        card = ctk.CTkFrame(self, corner_radius=20, fg_color="white")
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

        heading = ctk.CTkLabel(card, text="Create Your Account", font=title_font, text_color=self.app.dark_text)
        heading.pack(pady=(10, 8))

        self.name_entry = ctk.CTkEntry(card, placeholder_text="Full Name")
        self.name_entry.pack(fill="x", padx=40, pady=(10, 6))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Username")
        self.username_entry.pack(fill="x", padx=40, pady=(6, 6))

        self.email_entry = ctk.CTkEntry(card, placeholder_text="Email")
        self.email_entry.pack(fill="x", padx=40, pady=(6, 6))

        self.password_entry = ctk.CTkEntry(card, show="*", placeholder_text="Password")
        self.password_entry.pack(fill="x", padx=40, pady=(6, 6))

        self.confirm_entry = ctk.CTkEntry(card, show="*", placeholder_text="Confirm Password")
        self.confirm_entry.pack(fill="x", padx=40, pady=(6, 6))

        signup_btn = ctk.CTkButton(
            card,
            text="Sign Up",
            height=36,
            corner_radius=18,
            font=button_font,
            fg_color=self.app.primary_blue,
            command=self.handle_signup,
        )
        signup_btn.pack(pady=(12, 6))

        back_btn = ctk.CTkButton(
            card,
            text="Back to Login",
            height=32,
            corner_radius=16,
            fg_color="white",
            border_color=self.app.primary_blue,
            border_width=1,
            text_color=self.app.primary_blue,
            command=self.app.show_login_frame,
        )
        back_btn.pack(pady=(4, 10))

    def handle_signup(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not (name and username and email and password and confirm):
            messagebox.showwarning("Missing Info", "Fill all fields.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        created = self.app.register_user(name, username, email, password)
        if created:
            messagebox.showinfo("Account Created", "You can now log in.")
            self.app.show_login_frame()
        else:
            messagebox.showerror("Error", "Username already taken.")


# ============================================================
# Main Application Layout (after login)
# ============================================================

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, master: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = master
        self.user = user

        self.configure(fg_color="white")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        # TOP BAR
        topbar = ctk.CTkFrame(self, fg_color=self.app.primary_blue, height=60, corner_radius=0)
        topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        topbar.grid_propagate(False)

        title_label = ctk.CTkLabel(
            topbar,
            text="Academic Mentor",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white",
        )
        title_label.pack(side="left", padx=20)

        welcome_label = ctk.CTkLabel(
            topbar,
            text=f"Welcome, {self.user['name']}",
            font=ctk.CTkFont(size=13),
            text_color="white",
        )
        welcome_label.pack(side="right", padx=20)

        # SIDEBAR
        sidebar = ctk.CTkFrame(self, fg_color=self.app.sidebar_bg, width=210, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        self.sidebar_buttons = {}

        def add_btn(text, target):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                fg_color="transparent",
                hover_color="#D7E3FF",
                text_color=self.app.dark_text,
                anchor="w",
                height=36,
                corner_radius=10,
                command=lambda: self.show_page(target),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.sidebar_buttons[text] = btn

        ctk.CTkLabel(sidebar, text="Navigation",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#4A5677").pack(anchor="w", padx=14, pady=(15, 8))

        add_btn("Dashboard", "dashboard")
        add_btn("Attendance", "attendance")
        add_btn("Planner", "planner")
        add_btn("Goals & Scores", "goals")
        add_btn("Timetable", "timetable")
        add_btn("To-Do List", "todo")

        ctk.CTkLabel(sidebar, text="").pack(expand=True)
        logout_btn = ctk.CTkButton(
            sidebar,
            text="Logout",
            fg_color="white",
            text_color="#E74C3C",
            hover_color="#FFE7E3",
            corner_radius=18,
            command=self.handle_logout,
        )
        logout_btn.pack(fill="x", padx=12, pady=(0, 15))

        # MAIN VIEW
        self.content_frame = ctk.CTkFrame(self, fg_color="white")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)

        self.current_page = None
        self.show_page("dashboard")

    def reset_sidebar(self):
        for b in self.sidebar_buttons.values():
            b.configure(fg_color="transparent", text_color=self.app.dark_text)

    def show_page(self, name):
        self.reset_sidebar()

        mapping = {
            "dashboard": ("Dashboard", DashboardPage),
            "attendance": ("Attendance", AttendancePage),
            "planner": ("Planner", PlannerPage),
            "goals": ("Goals & Scores", GoalsPage),
            "timetable": ("Timetable", SettingsPage),
            "todo": ("To-Do List", ToDoPage),
        }

        label, page = mapping.get(name, mapping["dashboard"])
        self.sidebar_buttons[label].configure(fg_color="white", text_color=self.app.primary_blue)

        if self.current_page is not None:
            self.current_page.destroy()

        self.current_page = page(self.content_frame, self.app, self.user)
        self.current_page.pack(fill="both", expand=True)

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Do you really want to logout?"):
            self.app.logout()


# ============================================================
# DASHBOARD
# ============================================================

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user

        from modules.attendance_db import AttendanceDB
        from modules.goals_db import GoalsHelper
        from modules.todo_db import ToDoDB

        self.goals_db = GoalsHelper()
        self.goals_score_helper = GoalsHelper()   # ← final correct nam

        self.att_db = AttendanceDB()
        self.todo_db = ToDoDB()


        self.configure(fg_color="white")

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.dark_text
        ).pack(anchor="w", padx=15, pady=(10, 4))

        subtitle = ctk.CTkLabel(
            self,
            text="Overview of attendance, goals and today's tasks",
            font=ctk.CTkFont(size=12),
            text_color="#7A869A",
        )
        subtitle.pack(anchor="w", padx=15, pady=(0, 12))

        cards = ctk.CTkFrame(self, fg_color="white")
        cards.pack(fill="both", expand=True, padx=12, pady=10)

        self._attendance(cards)
        self._today(cards)
        self._goals(cards)

    def _attendance(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="#F7F8FF", corner_radius=14)
        frame.pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(frame, text="📊 Attendance Summary",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(8, 2))

        rows = self.att_db.get_subject_attendance(self.user["id"])


        if not rows:
            ctk.CTkLabel(frame, text="No attendance recorded yet.",
                         font=ctk.CTkFont(size=11),
                         text_color="#7A869A").pack(anchor="w", padx=10, pady=6)
            return

        total_present = sum(r[1] for r in rows)
        total_classes = sum(r[2] for r in rows)
        pct = int((total_present / total_classes) * 100) if total_classes else 0

        ctk.CTkLabel(frame,
                     text=f"Overall: {total_present}/{total_classes}  ({pct}%)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(0, 4))

        for subj, present, total in rows:
            pct = int((present / total) * 100) if total else 0
            ctk.CTkLabel(frame,
                         text=f"• {subj}: {present}/{total} ({pct}%)",
                         font=ctk.CTkFont(size=11),
                         text_color="#555C7A").pack(anchor="w", padx=14)

    def _today(self, parent):
        from modules.todo_db import ToDoDB
        frame = ctk.CTkFrame(parent, fg_color="#F7F8FF", corner_radius=14)
        frame.pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(frame, text="🗓 Today's Tasks",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(8, 2))

        today_str = datetime.today().strftime("%Y-%m-%d")
        tasks = self.todo_db.get_tasks_for_date(self.user["id"], today_str)

        if not tasks:
            ctk.CTkLabel(frame, text="No tasks for today.",
                         font=ctk.CTkFont(size=11),
                         text_color="#7A869A").pack(anchor="w", padx=10, pady=6)
            return

        done = sum(1 for t in tasks if t["status"] == "done")
        total = len(tasks)

        ctk.CTkLabel(frame,
                     text=f"{done}/{total} tasks completed",
                     font=ctk.CTkFont(size=12),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10)

        for t in tasks[:4]:
            icon = "✔" if t["status"] == "done" else "⏳"
            ctk.CTkLabel(frame,
                         text=f"{icon} {t['task_name']}",
                         font=ctk.CTkFont(size=11),
                         text_color="#555C7A").pack(anchor="w", padx=14)

    def _goals(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="#F7F8FF", corner_radius=14)
        frame.pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(frame, text="🎯 Goals & Scores",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(8, 2))

        totals = self.goals_db.get_subject_totals(self.user["id"])

        if not totals:
            ctk.CTkLabel(frame, text="No MST scores added yet.",
                 font=ctk.CTkFont(size=11),
                 text_color="#7A869A").pack(anchor="w", padx=10, pady=6)
            return
 
        for subj, pct in totals.items():
                 ctk.CTkLabel(frame,
                 text=f"• {subj}: {pct}%",
                 font=ctk.CTkFont(size=11),
                 text_color="#555C7A").pack(anchor="w", padx=14)

        weak = [s for s, pct in totals.items() if pct < 60]

        if weak:
                ctk.CTkLabel(frame,
                 text="Weak focus subjects → " + ", ".join(weak),
                 font=ctk.CTkFont(size=11, weight="bold"),
                 text_color="#C0392B").pack(anchor="w", padx=10, pady=(2, 8))
                
                        # 🔥 Smart ML Study Suggestion (Simple & lightweight)
        from modules.ml_model import StudyPredictor

        try:
            predictor = StudyPredictor()
            training_data = predictor.prepare_training_data(self.user["id"])
            trained = predictor.train(training_data)

            recommendations = predictor.recommend(training_data) if trained else []

            if recommendations:
                msg = "Suggestion → Focus more on: " + ", ".join(recommendations)
                ctk.CTkLabel(
                    frame,
                    text=msg,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#1E3799"
                ).pack(anchor="w", padx=10, pady=(4, 6))
            else:
                ctk.CTkLabel(
                    frame,
                    text="🔥 ML Summary → Your performance is improving!",
                    font=ctk.CTkFont(size=12),
                    text_color="#2E8B57"
                ).pack(anchor="w", padx=10, pady=(4, 6))
        except Exception as e:
            print("⚠ ML error:", e)

                
        
                
    




# ============================================================
# ATTENDANCE PAGE
# ============================================================

class AttendancePage(ctk.CTkFrame):
    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user

        from modules.subjects_db import SubjectsDB
        from modules.attendance_db import AttendanceDB
        from modules.timetable_db import TimetableDB

        self.subjects_db = SubjectsDB()
        self.att_db = AttendanceDB()
        self.timetable_db = TimetableDB()

        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Attendance Manager",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=15, pady=(10, 4))

        ctk.CTkLabel(self,
                     text="Select date and subject, then mark Present/Absent.",
                     font=ctk.CTkFont(size=11),
                     text_color="#7A869A").pack(anchor="w", padx=15, pady=(0, 10))

        row1 = ctk.CTkFrame(self, fg_color="white")
        row1.pack(anchor="w", padx=15, pady=(0, 8))
        ctk.CTkLabel(row1, text="Date").pack(side="left")
        self.date_entry = ctk.CTkEntry(row1, width=120)
        self.date_entry.pack(side="left", padx=6)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        row2 = ctk.CTkFrame(self, fg_color="white")
        row2.pack(anchor="w", padx=15, pady=(0, 8))
        ctk.CTkLabel(row2, text="Subject").pack(side="left")
        self.sub_menu = ctk.CTkComboBox(row2, width=160)
        self.sub_menu.pack(side="left", padx=6)

        present_btn = ctk.CTkButton(self, text="Present", fg_color="#26A65B",
                                    command=lambda: self.mark("P"))
        present_btn.pack(anchor="w", padx=15, pady=(6, 2))

        absent_btn = ctk.CTkButton(self, text="Absent", fg_color="#D64541",
                                   command=lambda: self.mark("A"))
        absent_btn.pack(anchor="w", padx=15, pady=(0, 8))

        self.table = ctk.CTkFrame(self, fg_color="white")
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_subjects()
        self.refresh_table()

    def load_subjects(self):
        subs = self.subjects_db.get_subjects(self.user["id"])
        if not subs:
            subs = ["ML", "CAO", "CN", "IP", "SE"]
        self.sub_menu.configure(values=subs)
        self.sub_menu.set(subs[0])

    def mark(self, status):
        d = self.date_entry.get().strip()
        s = self.sub_menu.get()
        if not d or not s:
            messagebox.showwarning("Missing", "Date or subject missing.")
            return
        self.att_db.set_attendance(self.user["id"], d, s, status)
        self.refresh_table()

    def refresh_table(self):
        for w in self.table.winfo_children():
            w.destroy()

        rows = self.att_db.get_subject_attendance(self.user["id"])
        if not rows:
            ctk.CTkLabel(self.table,
                         text="No attendance yet.",
                         font=ctk.CTkFont(size=12),
                         text_color="#7A869A").pack(pady=10)
            return

        ctk.CTkLabel(self.table, text="Subject-wise Attendance",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=4)

        for subj, present, total in rows:
            pct = int((present / total) * 100) if total > 0 else 0
            ctk.CTkLabel(self.table,
                         text=f"{subj}: {present}/{total} ({pct}%)",
                         font=ctk.CTkFont(size=11),
                         text_color="#555C7A").pack(anchor="w", padx=12, pady=2)


# ============================================================
# PLANNER PAGE
# ============================================================

class PlannerPage(ctk.CTkFrame):
    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user

        self.subjects_db = SubjectsDB()
        self.progress_db = ProgressDB()


        from modules.planner_logic import PlannerLogic
        from modules.tasks_db import TasksDB
        from modules.timetable_db import TimetableDB
        from modules.todo_db import ToDoDB

        self.logic = PlannerLogic()
        self.tasks_db = TasksDB()
        self.timetable_db = TimetableDB()
        self.todo_db = ToDoDB()
        from modules.progress_db import ProgressHelper
        self.progress_db = ProgressHelper()


        self.subjects = ["ML", "CAO", "CN", "IP", "SE"]
        self.allocations = {}
        self.feedback_vars = {}

        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Daily Study Planner",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=15, pady=(10, 6))

        row = ctk.CTkFrame(self, fg_color="white")
        row.pack(anchor="w", padx=15, pady=8)

        ctk.CTkLabel(row, text="Date").pack(side="left", padx=(0, 6))
        self.date_entry = ctk.CTkEntry(row, width=120)
        self.date_entry.pack(side="left")
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        generate_btn = ctk.CTkButton(
            row,
            text="Generate Plan",
            fg_color=self.app.primary_blue,
            command=self.generate_plan,
        )
        generate_btn.pack(side="left", padx=10)

        self.plan_frame = ctk.CTkFrame(self, fg_color="white")
        self.plan_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.feedback_btn = ctk.CTkButton(
            self,
            text="Submit Feedback",
            fg_color="#26A65B",
            command=self.submit_feedback,
        )
        self.feedback_btn.pack(pady=8)
        self.feedback_btn.pack_forget()

    def get_date(self):
        try:
            dt = datetime.strptime(self.date_entry.get().strip(), "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid", "Use YYYY-MM-DD format.")
            return None

    def format_hours(self, h):
        m = int(round(h * 60))
        hh, mm = m // 60, m % 60
        if hh and mm:
            return f"{hh}h {mm}m"
        if hh:
            return f"{hh}h"
        return f"{mm}m"

    def generate_plan(self):
        from datetime import datetime, timedelta

        date = self.get_date()
        if not date:
            return

        # Clear previous content
        self.feedback_vars.clear()
        for widget in self.plan_frame.winfo_children():
            widget.destroy()

        # Title
        ctk.CTkLabel(
            self.plan_frame,
            text=f"📅 Your Study Plan for {date}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.app.dark_text
        ).pack(anchor="w", padx=10, pady=(8, 6))

        # ---------- 1) Performance based recommendation ----------
        since = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        perf_rows = self.progress_db.get_performance_since(self.user["id"], since)
        perf_dict = {}
        for row in perf_rows:
         subject, avg_score = row
         perf_dict[subject] = avg_score or 0


        subject_rows = self.subjects_db.get_subjects(self.user["id"])
        subjects = [row if isinstance(row, str) else row[0] for row in subject_rows]


        ctk.CTkLabel(
            self.plan_frame,
            text="🎯 Subject-wise Focus:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2D3B5E"
        ).pack(anchor="w", padx=10, pady=(4, 2))

        for subj in subjects:
            avg = perf_dict.get(subj)
            if avg is None:
                msg = f"{subj}: No recent tests found → Try revision + 20 questions today"
            elif avg < 70:
                msg = f"{subj}: ⚠ Weak → revise theory + solve 30 practice Qs"
            elif avg < 85:
                msg = f"{subj}: Moderate → revise 1 topic + practice 10 Qs"
            else:
                msg = f"{subj}: 👍 Strong → do quick revision only"

            ctk.CTkLabel(
                self.plan_frame,
                text="• " + msg,
                font=ctk.CTkFont(size=12),
                text_color="#39476A",
                wraplength=420,
                justify="left"
            ).pack(anchor="w", padx=18, pady=1)

        # ---------- 2) To-do tasks with checkbox ----------
        todos = self.todo_db.get_tasks_for_date(self.user["id"], date)

        ctk.CTkLabel(
            self.plan_frame,
            text="\n📝 Tasks for Today:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2D3B5E"
        ).pack(anchor="w", padx=10, pady=(8, 2))

        if not todos:
            ctk.CTkLabel(
                self.plan_frame,
                text="No tasks added yet. Add tasks to track your day!",
                font=ctk.CTkFont(size=12),
                text_color="#555"
            ).pack(anchor="w", padx=18, pady=2)
        else:
            for t in todos:
                row = ctk.CTkFrame(self.plan_frame, fg_color="#F6F8FF", corner_radius=10)
                row.pack(fill="x", padx=8, pady=3)

                chk = ctk.CTkCheckBox(row, text=f"{t['task_name']} ({t['subject']})")
                chk.pack(side="left", padx=8, pady=6)
                self.feedback_vars[t["id"]] = chk

        self.feedback_btn.pack(pady=(10, 5))



    def submit_feedback(self):
        if not self.allocations:
            messagebox.showwarning("No Plan", "Generate a plan first.")
            return

        date = self.get_date()
        if not date:
            return

        fb = {s: m.get().lower() for s, m in self.feedback_vars.items()}
        score_map = {"done": 1.0, "half": 0.5, "not": 0.0}

        for subj, status in fb.items():
            score = score_map.get(status, 0.0)
            hrs = float(self.allocations.get(subj, 0.0) or 0.0)
            self.progress_db.log_feedback(self.user["id"], date, subj, hrs, score)

        self.logic.apply_feedback_for_day(self.allocations, fb)

        ctk.CTkLabel(self.plan_frame,
                     text="✔ Feedback saved. Tomorrow's plan will adapt.",
                     font=ctk.CTkFont(size=11),
                     text_color="#1E8C4A").pack(pady=6)


# ============================================================
# GOALS PAGE
# ============================================================

class GoalsPage(ctk.CTkFrame):
    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user

        from modules.subjects_db import SubjectsDB
        

        self.subjects_db = SubjectsDB()
        self.goals_db = GoalsHelper()

        self.goals_score_helper = GoalsHelper()

        self.configure(fg_color="white")

        ctk.CTkLabel(self,
                     text="Goals & Scores",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=15, pady=(10, 4))

        ctk.CTkLabel(self,
                     text="Set CGPA target and store MST scores",
                     font=ctk.CTkFont(size=12),
                     text_color="#7A869A").pack(anchor="w", padx=15, pady=(0, 12))

        main = ctk.CTkFrame(self, fg_color="white")
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # ---- CGPA -------
        cgpa_card = ctk.CTkFrame(main, fg_color="#F7F8FF", corner_radius=14)
        cgpa_card.pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(cgpa_card, text="Target CGPA",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(8, 2))

        row = ctk.CTkFrame(cgpa_card, fg_color="#F7F8FF")
        row.pack(fill="x", padx=10, pady=(0, 8))

        self.cgpa_entry = ctk.CTkEntry(row, width=80, placeholder_text="e.g. 9.0")
        self.cgpa_entry.pack(side="left")

        save_btn = ctk.CTkButton(
            row,
            text="Save",
            fg_color=self.app.primary_blue,
            command=self.save_cgpa,
        )
        save_btn.pack(side="left", padx=8)

        val = self.goals_db.get_target_cgpa(self.user["id"])
        if val is not None:
            self.cgpa_entry.insert(0, f"{val:.2f}")

        # ---- MST SCORES -------
        sc_card = ctk.CTkFrame(main, fg_color="#F7F8FF", corner_radius=14)
        sc_card.pack(fill="both", expand=True, padx=4, pady=6)

        ctk.CTkLabel(sc_card, text="MST Scores",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=(8, 2))

        form = ctk.CTkFrame(sc_card, fg_color="#F7F8FF")
        form.pack(fill="x", padx=8, pady=(0, 8))

        self.sub_box = ctk.CTkComboBox(form, width=140)
        self._load_subjects()
        self.sub_box.pack(side="left", padx=(2, 4))

        self.exam_entry = ctk.CTkEntry(form, width=80, placeholder_text="MST1")
        self.exam_entry.pack(side="left", padx=2)

        self.score_entry = ctk.CTkEntry(form, width=80, placeholder_text="Score")
        self.score_entry.pack(side="left", padx=2)

        self.max_entry = ctk.CTkEntry(form, width=80, placeholder_text="Out of")
        self.max_entry.pack(side="left", padx=2)

        add_btn = ctk.CTkButton(
            form,
            text="Add",
            width=60,
            fg_color=self.app.primary_blue,
            command=self.add_score,
        )
        add_btn.pack(side="left", padx=4)

        self.list = ctk.CTkFrame(sc_card, fg_color="#F7F8FF")
        self.list.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        self.refresh_list()

    def save_cgpa(self):
        tx = self.cgpa_entry.get().strip()
        if not tx:
            messagebox.showwarning("Missing", "Enter a CGPA target.")
            return
        try:
            val = float(tx)
        except ValueError:
            messagebox.showerror("Invalid", "Must be numeric.")
            return
        self.goals_db.set_target_cgpa(self.user["id"], val)
        messagebox.showinfo("Saved", "CGPA target saved.")

    def _load_subjects(self):
        subs = self.subjects_db.get_subjects(self.user["id"])
        if not subs:
            subs = ["ML", "CAO", "CN", "IP", "SE"]
        self.sub_box.configure(values=subs)
        self.sub_box.set(subs[0])

    def add_score(self):
        subj = self.sub_box.get()
        exam = self.exam_entry.get().strip() or "MST"
        s = self.score_entry.get().strip()
        m = self.max_entry.get().strip()

        if not s or not m:
            messagebox.showwarning("Missing", "Enter score & max.")
            return
        try:
            score = float(s)
            max_score = float(m)
        except:
            messagebox.showerror("Invalid", "Numbers required.")
            return

        self.goals_db.add_mst_score(self.user["id"], subj, exam, score, max_score)

        self.exam_entry.delete(0, "end")
        self.score_entry.delete(0, "end")
        self.max_entry.delete(0, "end")
        self.refresh_list()

    def refresh_list(self):
     for w in self.list.winfo_children():
        w.destroy()

     scores = self.goals_db.get_scores_for_user(self.user["id"])

     if not scores:
        ctk.CTkLabel(self.list, text="No records yet",
                     font=ctk.CTkFont(size=11), text_color="#7A869A").pack(pady=20)
        return

     for row in scores:
        # Supports both 3 and 4 tuple formats
        if len(row) == 4:
            subj, exam, score, m = row
        elif len(row) == 3:
            subj, exam, score = row
            m = 100
        else:
            continue

        try: score = float(score)
        except: score = 0

        try: m = float(m)
        except: m = 100

        pct = int((score / m) * 100) if m else 0

        ctk.CTkLabel(
            self.list,
            text=f"• {subj} - {exam}: {score}/{m} ({pct}%)",
            font=ctk.CTkFont(size=11),
            text_color="#555C7A",
        ).pack(anchor="w", padx=10, pady=2)



# ============================================================
# TIMETABLE PAGE
# ============================================================

class SettingsPage(ctk.CTkFrame):
    SLOT_TIMES = [
        "08:00–08:50", "08:50–09:40", "09:40–10:30",
        "10:30–11:20", "11:20–12:10", "12:10–13:00",
        "13:00–13:50", "13:50–14:40", "14:40–15:30",
        "15:30–16:20", "16:20–17:10"
    ]
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user

        from modules.timetable_db import TimetableDB
        self.db = TimetableDB()

        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Weekly Timetable",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=15, pady=(10, 6))

        frame = ctk.CTkFrame(self, fg_color="#F7F8FF", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Click on a cell to edit subject & class type",
            font=ctk.CTkFont(size=11),
            text_color="#7A869A"
        ).grid(row=0, column=0, columnspan=7, sticky="w", pady=(4, 8))

        ctk.CTkLabel(frame, text="Time",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=4, pady=4)

        for c, day in enumerate(self.DAYS, start=1):
            ctk.CTkLabel(frame, text=day,
                         font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=c, padx=4, pady=4)

        self.cells = {}
        for r, slot in enumerate(self.SLOT_TIMES, start=2):
            ctk.CTkLabel(frame, text=slot,
                         font=ctk.CTkFont(size=11),
                         text_color="#555C7A").grid(row=r, column=0, sticky="w", padx=4)

            for c in range(len(self.DAYS)):
                b = ctk.CTkButton(
                    frame,
                    text=" " * 7,
                    width=80,
                    height=32,
                    fg_color="white",
                    corner_radius=8,
                    hover_color="#E2E7FF",
                    command=lambda w=c, s=r-2: self.edit_slot(w, s)
                )
                b.grid(row=r, column=c + 1, padx=2, pady=2)
                self.cells[(c, r-2)] = b

        save_btn = ctk.CTkButton(
            self,
            text="Save Timetable",
            fg_color=self.app.primary_blue,
            corner_radius=18,
            command=self.save
        )
        save_btn.pack(pady=6)

        self.load()

    def edit_slot(self, weekday, slot):
        popup = ctk.CTkToplevel(self)
        popup.geometry("330x290")
        popup.title("Edit Slot")
        popup.grab_set()

        entry = ctk.CTkEntry(popup, placeholder_text="Subject (e.g., ML)")
        entry.pack(padx=20, pady=(20, 10))

        class_type = ctk.StringVar(value="Lec")
        for t in ["Lec", "Tut", "Lab"]:
            ctk.CTkRadioButton(popup, text=t, variable=class_type, value=t).pack(anchor="w", padx=18)

        slots = self.db.get_slots_for_weekday(self.user["id"], weekday)
        cur = slots.get(slot, ("", ""))    # if slot missing → ("", "")
        cur_subj, cur_ctype = cur

        if cur_subj:
            entry.insert(0, cur_subj)
        if cur_ctype:
            class_type.set(cur_ctype)

        def save_slot():
            s = entry.get().strip() or None
            if not s:
                self.db.set_slot(self.user["id"], weekday, slot, None, None)
            else:
                s = s.upper().replace("  ", " ").strip()
                self.db.set_slot(self.user["id"], weekday, slot, s, class_type.get())
            popup.destroy()
            self.load()

        ctk.CTkButton(popup, text="Save", fg_color=self.app.primary_blue, command=save_slot).pack(pady=12)

    def load(self):
        for (wk, sl), btn in self.cells.items():
            btn.configure(text="     ")

        for wk in range(len(self.DAYS)):
            slots = self.db.get_slots_for_weekday(self.user["id"], wk)
            for sl, (subj, ctype) in slots.items():
                if subj:
                    self.cells[(wk, sl)].configure(text=f"{subj} ({ctype})")

    def save(self):
        messagebox.showinfo("Saved", "Timetable saved successfully!")


# ============================================================
# TO-DO PAGE
# ============================================================

from modules.todo_db import ToDoDB

class ToDoPage(ctk.CTkFrame):
    def __init__(self, master, app: AcademicMentorApp, user: dict):
        super().__init__(master)
        self.app = app
        self.user = user
        self.db = ToDoDB()

        self.configure(fg_color="white")

        ctk.CTkLabel(
            self,
            text="To-Do List",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.dark_text
        ).pack(anchor="w", padx=15, pady=(10, 4))

        row = ctk.CTkFrame(self, fg_color="white")
        row.pack(anchor="w", padx=15, pady=(0, 6))

        self.current_date = datetime.today().date()
        self.date_label = ctk.CTkLabel(
            row,
            text=self.current_date.strftime("%Y-%m-%d"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.app.dark_text
        )
        self.date_label.pack(side="left")

        add_btn = ctk.CTkButton(
            row,
            text="+ Add Task",
            fg_color=self.app.primary_blue,
            command=self.open_add_popup
        )
        add_btn.pack(side="left", padx=15)

        self.task_frame = ctk.CTkFrame(self, fg_color="white")
        self.task_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_tasks()

    def get_date_str(self):
        return self.current_date.strftime("%Y-%m-%d")

    def load_tasks(self):
        for w in self.task_frame.winfo_children():
            w.destroy()

        tasks = self.db.get_tasks_for_date(self.user["id"], self.get_date_str())
        if not tasks:
            ctk.CTkLabel(self.task_frame,
                         text="No tasks for this date",
                         font=ctk.CTkFont(size=11),
                         text_color="#7A869A").pack(pady=30)
            return

        for t in tasks:
            self.add_task_row(t)

    def add_task_row(self, t):
     row = ctk.CTkFrame(self.task_frame, fg_color="#F7F8FF", corner_radius=10)
     row.pack(fill="x", padx=4, pady=4)

     chk = ctk.CTkCheckBox(
        row,
        text=f"{t['task_name']} ({t['subject']})" if t["subject"] else t["task_name"],
    )
     chk.pack(side="left", padx=8, pady=6)

     if t["status"] == "done":
         chk.select()

     chk.configure(command=lambda tid=t["id"], c=chk: self.update_task_status(tid, c))

     del_btn = ctk.CTkButton(
        row,
        text="Delete",
        width=60,
        fg_color="#FFE8E8",
        text_color="#C0392B",
        hover_color="#FFCCCC",
        command=lambda tid=t["id"]: self.delete_task(tid)
    )
     del_btn.pack(side="right", padx=8)


    def update_task_status(self, task_id, checkbox):
        new_status = "done" if checkbox.get() else "pending"
        self.db.update_status(task_id, new_status)

    def delete_task(self, tid):
        self.db.delete_task(tid)
        self.load_tasks()

    def open_add_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.geometry("340x310")
        popup.title("Add Task")
        popup.grab_set()

        name_e = ctk.CTkEntry(popup, placeholder_text="Task name")
        name_e.pack(fill="x", padx=15, pady=(15, 8))

        subject_e = ctk.CTkEntry(popup, placeholder_text="Subject (optional)")
        subject_e.pack(fill="x", padx=15, pady=(0, 8))

        dur_e = ctk.CTkEntry(popup, placeholder_text="Duration (minutes)")
        dur_e.pack(fill="x", padx=15, pady=(0, 8))

        pr_menu = ctk.CTkOptionMenu(popup, values=["Low", "Medium", "High"])
        pr_menu.set("Medium")
        pr_menu.pack(fill="x", padx=15, pady=(0, 10))

        def save():
            name = name_e.get().strip()
            if not name:
                messagebox.showwarning("Missing", "Task name required")
                return
            try:
                dur = int(dur_e.get().strip())
                if dur <= 0:
                    raise ValueError
            except:
                messagebox.showwarning("Error", "Duration must be positive number")
                return

            self.db.add_task(
                self.user["id"],
                self.get_date_str(),
                name,
                subject_e.get().strip() or None,
                dur,
                pr_menu.get(),
                # default status
            )
            popup.destroy()
            self.load_tasks()

        ctk.CTkButton(
            popup,
            text="Save Task",
            fg_color=self.app.primary_blue,
            command=save
        ).pack(pady=5)
