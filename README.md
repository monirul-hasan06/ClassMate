# ClassMate – An Academic & Learning Assistant

**Course:** Database Management System (DBMS)  
**Target Platform:** Desktop Application (Windows 10/11)  
**Technology Stack:** Python 3, PyQt6 (GUI), SQLite3 (Embedded Normalized Local RDBMS), Google Classroom & YouTube Data API v3 Integration  

### Submitted By
- **Md. Monirul Hasan** (ID: `20255103087`)
- **Yusuf Ali** (ID: `20255103138`)

### Submitted To
- **Farah Akter Munmun [FAM]**  
  Assistant Professor, Department of Computer Science and Engineering (CSE)  
  Bangladesh University of Business and Technology (BUBT)  
  Email: `farha.akhter@bubt.edu.bd`

---

## Key Features Implemented
1. **Onboarding & Personalization (`ui/onboarding_dialog.py`)**
   - Personalized onboarding wizard with quick BUBT team profile switching (`Md. Monirul Hasan` & `Yusuf Ali`).
   - Time-aware contextual greeting on the Dashboard (`Good Morning` / `Good Afternoon` / `Good Evening`).
   - **Next Class Widget Card**: Displays Course Code & Name (`CSE 208: Database Management System Lab`), Schedule & Duration (`8:15 AM - 11:15 AM`), Venue (`Building 2, Room 417`), Instructor Name & Short Name (`Farah Akter Munmun [FAM]`), and direct **Quick Attendance Logger** buttons (`✓ Mark Attended`, `✗ Mark Missed`).
2. **Class Routine & Weekly Scheduler (`ui/routine_page.py`)**
   - **Day-Wise Tabs**: Quick selection tabs from Saturday to Friday ordered dynamically by the user's configured starting day of the week.
   - **Full Weekly Overview Grid**: Consolidated table view of the entire week's classes.
   - **Semester Management**: Transition to a new semester by archiving or clearing old routines.
   - **Routine Sharing**: Export routine template to `.json` to share with classmates and import shared `.json` routine templates.
3. **Assessment & Exam Management (`ui/exams_page.py`)**
   - **Exam Tracker**: Log Class Tests (CTs), Midterm Exams, and Final Exams with countdowns.
   - **Exam History**: Archive past exam records alongside obtained marks and performance notes.
   - **Exam Reminders**: Dedicated notification controls and test triggers.
4. **Faculty Directory (`ui/faculty_page.py`)**
   - Searchable directory storing Full Name, Short Name (`[FAM]`), Designation, Department, Email Address, Phone Number, Consulting Hours, and Office Room.
5. **Smart Notification & Alert System (`services/notification_service.py`)**
   - Configurable alert intervals (`15m`, `30m`, `1h`, `12h` prior, or nightly schedule summary).
   - Granular pause/resume controls specifically for Class Alerts, Exam Alerts, or Nightly Routine Summaries.
6. **Supplementary API Features (`services/api_service.py`, `ui/learning_hub_page.py`)**
   - **YouTube Learning Assistant**: Automatic extraction of course keywords to recommend top-ranked distraction-free playlists (supports both offline curated academic playlists and live YouTube Data API v3 keys).
   - **Google Classroom Integration**: Syncs assignment deadlines and course announcements into the local database.

---

## Normalized Relational Database Schema (`database/db_manager.py`)
- `users`: `user_id (PK)`, `full_name`, `student_id`, `department`, `semester`, `institution`, `theme_preference`, `clock_format`, `week_start_day`, `onboarded`
- `faculty`: `faculty_id (PK)`, `name`, `short_name`, `designation`, `department`, `email`, `phone`, `consulting_hours`, `office_room`
- `courses`: `course_id (PK)`, `course_code`, `course_name`, `section`, `building_number`, `room_number`, `faculty_id (FK -> faculty)`, `semester`, `is_archived`
- `schedules`: `schedule_id (PK)`, `course_id (FK -> courses)`, `day_of_week`, `start_time`, `end_time`
- `exams`: `exam_id (PK)`, `course_id (FK -> courses)`, `exam_type`, `exam_date`, `exam_time`, `room_number`, `syllabus`, `performance_notes`, `marks_obtained`, `total_marks`, `is_archived`
- `attendance_logs`: `log_id (PK)`, `schedule_id (FK -> schedules)`, `date`, `status`, `remarks`
- `notification_settings`: `setting_id (PK)`, `class_reminder_offset`, `exam_reminder_offset`, `daily_summary_time`, `pause_class_alerts`, `pause_exam_alerts`, `pause_routine_alerts`, `youtube_api_key`, `google_classroom_connected`
- `classroom_items`: `item_id (PK)`, `course_code`, `title`, `item_type`, `due_date`, `status`, `description`, `external_link`

---

## How to Run
Double-click `run_classmate.bat` or run from PowerShell/Terminal:
```powershell
.\.venv\Scripts\python.exe main.py
```

