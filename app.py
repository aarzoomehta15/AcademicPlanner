import customtkinter as ctk
import hashlib
from tkinter import messagebox
from datetime import datetime, timedelta

# Database Modules
from modules.users_db import UsersDB
from modules.subjects_db import SubjectsDB
from modules.goals_db import GoalsHelper
from modules.attendance_db import AttendanceDB
from modules.planner_logic import PlannerLogic

# Global Configuration
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AcademicMentorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Academic Mentor - Smart Study Planner")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        # Theme Colors
        self.primary_blue = "#5B8DF6"
        self.sidebar_bg = "#E5ECFF"
        self.dark_text = "#1F2A44"

        self.current_user = None
        self.active_frame = None

        # Initialize Core User DB
        self.users_db = UsersDB()
        
        # Start at Login
        self.show_login_frame()

    def register_user(self, name, username, email, password):
        # Hash password for security (basic)
        hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return self.users_db.register_user(name, username, email, hashed)

    def authenticate_user(self, username, password):
        hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return self.users_db.authenticate_user(username, hashed)

    def switch_frame(self, frame_class, **kwargs):
        if self.active_frame:
            self.active_frame.destroy()
        # frame_class is instantiated with (self, **kwargs)
        # self here is the AcademicMentorApp instance
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


# ---------------------------------------------------------
# LOGIN & SIGNUP FRAMES
# ---------------------------------------------------------

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self.configure(fg_color="white")

        # Header
        ctk.CTkLabel(self, text="Academic Mentor", font=("Segoe UI", 28, "bold"), 
                     text_color=self.app.dark_text).pack(pady=(80, 5))
        ctk.CTkLabel(self, text="Smart Study Planner powered by ML", font=("Segoe UI", 14), 
                     text_color="gray").pack(pady=(0, 30))

        # Inputs
        self.username = ctk.CTkEntry(self, placeholder_text="Username", width=300, height=40)
        self.username.pack(pady=10)
        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300, height=40)
        self.password.pack(pady=10)

        # Buttons
        ctk.CTkButton(self, text="Login", width=300, height=40, 
                      fg_color=self.app.primary_blue, command=self.login).pack(pady=20)
        
        ctk.CTkButton(self, text="Create New Account", width=300, fg_color="transparent", 
                      text_color=self.app.primary_blue, hover=False,
                      command=self.app.show_signup_frame).pack()

    def login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showwarning("Required", "Please enter username and password")
            return
        
        user = self.app.authenticate_user(u, p)
        if user:
            self.app.current_user = user
            self.app.show_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


class SignupFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Create Account", font=("Segoe UI", 28, "bold"), 
                     text_color=self.app.dark_text).pack(pady=(50, 20))

        self.name = ctk.CTkEntry(self, placeholder_text="Full Name", width=300)
        self.name.pack(pady=5)
        self.user = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.user.pack(pady=5)
        self.email = ctk.CTkEntry(self, placeholder_text="Email", width=300)
        self.email.pack(pady=5)
        self.pwd = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self.pwd.pack(pady=5)

        ctk.CTkButton(self, text="Sign Up", width=300, height=40, 
                      fg_color=self.app.primary_blue, command=self.signup).pack(pady=20)
        
        ctk.CTkButton(self, text="Back to Login", width=300, fg_color="transparent", 
                      text_color=self.app.primary_blue, hover=False,
                      command=self.app.show_login_frame).pack()

    def signup(self):
        if not all([self.name.get(), self.user.get(), self.email.get(), self.pwd.get()]):
            messagebox.showwarning("Error", "All fields are required")
            return
        
        success = self.app.register_user(self.name.get(), self.user.get(), self.email.get(), self.pwd.get())
        if success:
            messagebox.showinfo("Success", "Account created! Please login.")
            self.app.show_login_frame()
        else:
            messagebox.showerror("Error", "Username already exists")


# ---------------------------------------------------------
# MAIN APPLICATION (SIDEBAR + CONTENT)
# ---------------------------------------------------------

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master)
        self.app = master # The master IS the app instance
        self.user = user
        self.configure(fg_color="white")

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.app.sidebar_bg)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="Academic Mentor", font=("Segoe UI", 20, "bold"), 
                     text_color=self.app.primary_blue).pack(pady=(30, 10))
        
        ctk.CTkLabel(self.sidebar, text=f"Hi, {user['name']}", font=("Segoe UI", 14), 
                     text_color="gray").pack(pady=(0, 30))

        self.buttons = {}
        # Navigation Buttons
        self.add_sidebar_btn("Dashboard", DashboardPage)
        self.add_sidebar_btn("Goals & Subjects", GoalsPage)
        self.add_sidebar_btn("Attendance", AttendancePage)
        # Timetable button removed
        self.add_sidebar_btn("ML Planner", PlannerPage)

        # Logout
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#FF6B6B", hover_color="#FF5252", 
                      command=self.app.logout).pack(side="bottom", pady=30, padx=20, fill="x")

        # 2. Content Area
        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.pack(side="right", fill="both", expand=True)
        
        # Default Page
        self.show_page("Dashboard", DashboardPage)

    def add_sidebar_btn(self, text, frame_class):
        btn = ctk.CTkButton(self.sidebar, text=text, height=40, fg_color="transparent", 
                            text_color=self.app.dark_text, anchor="w", hover_color="#D1E0FF",
                            font=("Segoe UI", 14),
                            command=lambda: self.show_page(text, frame_class))
        btn.pack(fill="x", pady=5, padx=10)
        self.buttons[text] = btn

    def show_page(self, name, frame_class):
        # Reset button styles
        for btn in self.buttons.values(): 
            btn.configure(fg_color="transparent", text_color=self.app.dark_text)
        
        # Highlight active
        self.buttons[name].configure(fg_color="white", text_color=self.app.primary_blue)

        # Clear content area
        for widget in self.content.winfo_children(): 
            widget.destroy()
        
        # Load new page
        frame = frame_class(self.content, self.app, self.user)
        frame.pack(fill="both", expand=True, padx=20, pady=20)


# ---------------------------------------------------------
# PAGE CLASSES
# ---------------------------------------------------------

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app, user):
        super().__init__(master)
        self.configure(fg_color="white")
        self.goals_db = GoalsHelper()
        self.att_db = AttendanceDB()
        
        ctk.CTkLabel(self, text="Dashboard", font=("Segoe UI", 24, "bold"), 
                     text_color=app.dark_text).pack(anchor="w")
        ctk.CTkLabel(self, text="Your academic snapshot", font=("Segoe UI", 14), 
                     text_color="gray").pack(anchor="w", pady=(0, 20))

        # Stats Container
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x")

        # 1. Attendance Stat (Updated for Manual Percentage)
        att_data = self.att_db.get_attendance_percent(user["id"])
        if att_data:
            # Average of all subject percentages
            att_pct = int(sum(att_data.values()) / len(att_data))
        else:
            att_pct = 0
        
        self.create_card(stats_frame, "Attendance", f"{att_pct}%", "#E3F2FD", "#1565C0")

        # 2. Average Score Stat
        scores = self.goals_db.get_subject_totals(user["id"]) # returns {subj: pct}
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            self.create_card(stats_frame, "Avg Score", f"{int(avg_score)}%", "#E8F5E9", "#2E7D32")
        else:
            self.create_card(stats_frame, "Avg Score", "N/A", "#FFF3E0", "#EF6C00")

    def create_card(self, parent, title, value, bg, text_color):
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=12, height=100)
        card.pack(side="left", padx=10, expand=True, fill="x")
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, text_color=text_color, font=("Segoe UI", 14)).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Segoe UI", 28, "bold"), text_color=text_color).pack(pady=(0, 10))


class GoalsPage(ctk.CTkFrame):
    def __init__(self, master, app, user):
        super().__init__(master)
        self.user = user
        self.app = app
        self.configure(fg_color="white")
        
        self.subjects_db = SubjectsDB()
        self.goals_db = GoalsHelper()

        ctk.CTkLabel(self, text="Goals & Subjects", font=("Segoe UI", 22, "bold"), 
                     text_color=app.dark_text).pack(anchor="w", pady=10)

        # --- SECTION 1: ADD SUBJECT ---
        sub_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=10)
        sub_frame.pack(fill="x", pady=10)
        
        self.new_sub_entry = ctk.CTkEntry(sub_frame, placeholder_text="Enter Subject Name (e.g. Mathematics)")
        self.new_sub_entry.pack(side="left", padx=15, pady=15, expand=True, fill="x")
        
        ctk.CTkButton(sub_frame, text="+ Add Subject", width=120, 
                      command=self.add_subject).pack(side="left", padx=15)

        # --- SECTION 2: SET TARGETS & VIEW SCORES ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        self.scroll.pack(fill="both", expand=True)
        
        self.refresh_data()

    def add_subject(self):
        name = self.new_sub_entry.get().strip()
        if name:
            self.subjects_db.add_subject(self.user["id"], name)
            self.new_sub_entry.delete(0, "end")
            self.refresh_data()
            messagebox.showinfo("Success", f"Subject '{name}' added!")
        else:
            messagebox.showwarning("Input Error", "Subject name cannot be empty.")

    def refresh_data(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        subjects = self.subjects_db.get_subjects(self.user["id"])
        
        if not subjects:
            ctk.CTkLabel(self.scroll, text="No subjects added yet.", text_color="gray").pack(pady=20)
            return

        # 2A. Target Marks Input
        target_frame = ctk.CTkFrame(self.scroll, fg_color="#E3F2FD", corner_radius=10)
        target_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(target_frame, text="Set Target Marks (Out of 100)", font=("Segoe UI", 14, "bold"), 
                     text_color="#1565C0").pack(anchor="w", padx=10, pady=10)

        self.target_entries = {}
        grid_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, subj in enumerate(subjects):
            ctk.CTkLabel(grid_frame, text=subj, width=100, anchor="w").grid(row=i, column=0, padx=10, pady=5)
            ent = ctk.CTkEntry(grid_frame, width=80, placeholder_text="90")
            ent.grid(row=i, column=1, padx=10, pady=5)
            
            saved_target = self.goals_db.get_subject_target(self.user["id"], subj)
            if saved_target: ent.insert(0, int(saved_target))
            
            self.target_entries[subj] = ent

        ctk.CTkButton(target_frame, text="Save Targets", fg_color="#1565C0", height=32, 
                      command=self.save_targets).pack(pady=10)

        # 2B. MST Scores Input
        score_frame = ctk.CTkFrame(self.scroll, fg_color="#F1F3F5", corner_radius=10)
        score_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(score_frame, text="Log Exam Scores", font=("Segoe UI", 14, "bold"),
                     text_color=self.app.dark_text).pack(anchor="w", padx=10, pady=10)
        
        input_row = ctk.CTkFrame(score_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=10)
        
        self.score_sub = ctk.CTkComboBox(input_row, values=subjects, width=150)
        self.score_sub.pack(side="left", padx=5)
        
        self.score_val = ctk.CTkEntry(input_row, placeholder_text="Marks", width=80)
        self.score_val.pack(side="left", padx=5)
        
        self.score_max = ctk.CTkEntry(input_row, placeholder_text="Max", width=80)
        self.score_max.pack(side="left", padx=5)
        
        ctk.CTkButton(input_row, text="Add", width=60, command=self.add_score).pack(side="left", padx=10)

        # List recent scores
        hist_frame = ctk.CTkFrame(score_frame, fg_color="white")
        hist_frame.pack(fill="x", padx=10, pady=10)
        
        scores = self.goals_db.get_scores_for_user(self.user["id"])
        if not scores:
            ctk.CTkLabel(hist_frame, text="No scores logged yet.").pack()
        else:
            for s in scores[:5]: # Show last 5
                if len(s) == 4: subj, exam, sc, mx = s
                else: continue
                pct = int((sc/mx)*100) if mx else 0
                ctk.CTkLabel(hist_frame, text=f"• {subj} ({exam}): {sc}/{mx} ({pct}%)", anchor="w").pack(fill="x", padx=5)

    def save_targets(self):
        count = 0
        for subj, ent in self.target_entries.items():
            val = ent.get().strip()
            if val:
                try:
                    target = float(val)
                    self.goals_db.set_subject_target(self.user["id"], subj, target)
                    count += 1
                except ValueError:
                    continue
        if count > 0:
            messagebox.showinfo("Saved", f"Updated targets for {count} subjects.")
        else:
            messagebox.showwarning("Info", "No valid targets entered.")

    def add_score(self):
        try:
            s = float(self.score_val.get())
            m = float(self.score_max.get())
            if m <= 0: raise ValueError
            self.goals_db.add_mst_score(self.user["id"], self.score_sub.get(), "Exam", s, m)
            self.refresh_data()
            self.score_val.delete(0, "end")
            self.score_max.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric marks.")


class AttendancePage(ctk.CTkFrame):
    def __init__(self, master, app, user):
        super().__init__(master)
        self.configure(fg_color="white")
        self.user = user
        self.att_db = AttendanceDB()
        self.sub_db = SubjectsDB()

        ctk.CTkLabel(self, text="Attendance Manager", font=("Segoe UI", 22, "bold"), 
                     text_color=app.dark_text).pack(anchor="w", pady=10)

        # Check subjects
        subjects = self.sub_db.get_subjects(user["id"])
        if not subjects:
            ctk.CTkLabel(self, text="No subjects found. Please add them in 'Goals & Subjects' page.", 
                         text_color="red").pack(pady=20)
            return

        # Controls (Updated for Manual Entry)
        ctrl_frame = ctk.CTkFrame(self, fg_color="#F8F9FA")
        ctrl_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(ctrl_frame, text="Select Subject:").pack(side="left", padx=10)
        self.sub_menu = ctk.CTkComboBox(ctrl_frame, values=subjects, width=200)
        self.sub_menu.pack(side="left", padx=10)

        ctk.CTkLabel(ctrl_frame, text="Current %:").pack(side="left", padx=10)
        self.pct_entry = ctk.CTkEntry(ctrl_frame, placeholder_text="85", width=60)
        self.pct_entry.pack(side="left", padx=5)

        ctk.CTkButton(ctrl_frame, text="Update", fg_color="#4CAF50", width=100,
                      command=self.update_attendance).pack(side="left", padx=15)

        # Stats Display
        self.stats_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.stats_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_stats()

    def update_attendance(self):
        subj = self.sub_menu.get()
        try:
            val = float(self.pct_entry.get())
            if 0 <= val <= 100:
                self.att_db.set_attendance_percentage(self.user["id"], subj, val)
                self.refresh_stats()
                self.pct_entry.delete(0, "end")
            else:
                messagebox.showwarning("Invalid Input", "Percentage must be between 0 and 100.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def refresh_stats(self):
        for w in self.stats_frame.winfo_children(): w.destroy()
        
        # Now returns {Subject: Percentage}
        data = self.att_db.get_attendance_percent(self.user["id"])
        
        if not data:
            ctk.CTkLabel(self.stats_frame, text="No attendance records updated yet.").pack(pady=20)
            return

        ctk.CTkLabel(self.stats_frame, text="Current Attendance Status:", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=10, padx=10)

        for subj, pct in data.items():
            color = "#4CAF50" if pct >= 75 else "#F44336"
            
            row = ctk.CTkFrame(self.stats_frame, fg_color="#F1F3F5")
            row.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(row, text=subj, font=("Segoe UI", 14, "bold"), width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{pct}%", text_color=color, font=("Segoe UI", 14, "bold")).pack(side="right", padx=20)


# SettingsPage (Timetable) removed


class PlannerPage(ctk.CTkFrame):
    def __init__(self, master, app, user):
        super().__init__(master)
        self.configure(fg_color="white")
        self.user = user
        # Initialize Logic with User ID
        self.logic = PlannerLogic(user["id"])
        self.sub_db = SubjectsDB()
        self.goals_db = GoalsHelper()

        ctk.CTkLabel(self, text="AI Study Planner", font=("Segoe UI", 22, "bold"), 
                     text_color="#1F2A44").pack(anchor="w", pady=10)
        
        ctk.CTkLabel(self, text=f"Plan for Today: {datetime.today().strftime('%A, %d %B')}", 
                     text_color="gray").pack(anchor="w", pady=(0, 10))

        # Main Action
        ctk.CTkButton(self, text="⚡ Generate New Plan", height=45, font=("Segoe UI", 16, "bold"),
                      fg_color=app.primary_blue, command=self.generate).pack(fill="x", padx=10, pady=10)

        # Results Area
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="#F8F9FA")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def generate(self):
        # Clean old results
        for w in self.results_frame.winfo_children(): w.destroy()

        # 1. Fetch Subjects
        subjects = self.sub_db.get_subjects(self.user["id"])
        if not subjects:
            ctk.CTkLabel(self.results_frame, text="No subjects found.\nGo to 'Goals & Subjects' to add them first.",
                         font=("Segoe UI", 14), text_color="red").pack(pady=40)
            return

        # 2. Check for Missing Targets
        missing_targets = []
        for s in subjects:
            if not self.goals_db.get_subject_target(self.user["id"], s):
                missing_targets.append(s)
        
        if missing_targets:
            msg = f"Target Marks missing for:\n{', '.join(missing_targets)}\n\nPlease set them in 'Goals & Subjects' page."
            ctk.CTkLabel(self.results_frame, text=msg, text_color="#C62828", font=("Segoe UI", 14)).pack(pady=20)
            return

        # 3. Generate Plan (ML Magic)
        # Note: We assume 4 slots occupied for now, or fetch from timetable
        try:
            # Force refresh db helpers inside logic
            plan = self.logic.generate_daily_plan(subjects, class_slots_today=5)
        except Exception as e:
            ctk.CTkLabel(self.results_frame, text=f"Error generating plan: {str(e)}", text_color="red").pack()
            return

        if not plan:
            ctk.CTkLabel(self.results_frame, text="Could not generate plan. Check inputs.").pack()
            return

        # 4. Display Results
        ctk.CTkLabel(self.results_frame, text="Recommended Study Hours", font=("Segoe UI", 16, "bold"), 
                     text_color="#1565C0").pack(anchor="w", pady=(10, 15), padx=10)

        for subj, hours in plan.items():
            # Color coding based on intensity
            if hours < 1.0: 
                color = "#81C784" # Light Green (Easy)
                note = "Quick Revision"
            elif hours < 2.0: 
                color = "#FFB74D" # Orange (Moderate)
                note = "Deep Study"
            else: 
                color = "#E57373" # Red (Heavy)
                note = "Intense Focus Needed"

            card = ctk.CTkFrame(self.results_frame, fg_color="white", border_color=color, border_width=2)
            card.pack(fill="x", pady=5, padx=10)
            
            # Subject Name
            ctk.CTkLabel(card, text=subj, font=("Segoe UI", 16, "bold"), width=150, anchor="w").pack(side="left", padx=15, pady=10)
            
            # Hours
            ctk.CTkLabel(card, text=f"{hours} hrs", font=("Segoe UI", 18, "bold"), text_color="#37474F").pack(side="right", padx=20)
            
            # Note
            ctk.CTkLabel(card, text=note, text_color="gray", font=("Segoe UI", 12)).pack(side="left", padx=10)

if __name__ == "__main__":
    app = AcademicMentorApp()
    app.mainloop()