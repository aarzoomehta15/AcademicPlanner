# Task List for Academic Mentor Improvements

## 1. Database Migration to PostgreSQL with SQLAlchemy
- Modify app.py to use SQLAlchemy for DB connection.
- Create DB models in modules using SQLAlchemy ORM replacing direct SQLite usage.
- Configure DB connection string and support environment config.
- Test DB connection and CRUD operations.

## 2. Planner Logic Enhancement
- Modify modules/planner_logic.py:
  - Generate detailed daily schedule assigning subjects to actual time slots.
  - Respect user's timetable and class schedules.
- Modify PlannerPage UI in app.py:
  - Display generated detailed daily schedule with times and subjects.
  - Improve user interaction with planner results.

## 3. ML Agent Refactor
- Refactor ml/rl_agent.py to support multiple ML model plugins.
- Provide interface to plug in additional ML agents.
- Update planner to select or switch ML decision agents.

## 4. New ML Models File (ml/performance_predictor.py)
- Create ml/performance_predictor.py
- Implement models for:
  - Predicting student performance using past data (MST scores, attendance).
  - Detecting weak subjects for focused study recommendations.
- Provide interface or functions to integrate with planner and UI.

## Followup Steps After Edits
- Run DB migration scripts and validate.
- Test full daily schedule generation and UI rendering.
- Validate ML model predictions and planner improvements.
- Gather user feedback for further refinements.

---

Proceeding step-by-step in the above order.
