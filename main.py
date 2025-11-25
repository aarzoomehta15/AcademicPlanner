# main.py
from db.session import init_db
# If still error, then use:
# from session import init_db
from modules.scores_db import ScoresDB



# Create tables only once
init_db()
from db.session import Base, engine
from modules.progress_db import ProgressDB
Base.metadata.create_all(bind=engine)


import customtkinter as ctk
from app import AcademicMentorApp

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = AcademicMentorApp()
    app.mainloop()
