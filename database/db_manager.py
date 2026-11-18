import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class DatabaseManager:
    """
    SQLite3 Relational Database Management System for ClassMate.
    Implements normalized schema:
      - users
      - faculty
      - courses
      - schedules
      - exams
      - attendance_logs
      - notification_settings
      - classroom_items (supplementary Google Classroom cache)
    """

    DAYS_ALL = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "classmate.db")
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self) -> None:
        """Create normalized relational tables if they do not exist and seed initial BUBT sample data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    department TEXT DEFAULT 'CSE',
                    semester TEXT DEFAULT 'Fall 2026',
                    institution TEXT DEFAULT 'Bangladesh University of Business and Technology (BUBT)',
                    theme_preference TEXT DEFAULT 'Dark',
                    clock_format TEXT DEFAULT '12h',
                    week_start_day TEXT DEFAULT 'Saturday',
                    onboarded INTEGER DEFAULT 1
                );
            """)

            # 2. faculty table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faculty (
                    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    short_name TEXT NOT NULL,
                    designation TEXT DEFAULT 'Assistant Professor',
                    department TEXT DEFAULT 'Department of CSE',
                    email TEXT,
                    phone TEXT,
                    consulting_hours TEXT,
                    office_room TEXT
                );
            """)

            # 3. courses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    section TEXT DEFAULT '01',
                    building_number TEXT NOT NULL,
                    room_number TEXT NOT NULL,
                    faculty_id INTEGER,
                    semester TEXT DEFAULT 'Fall 2026',
                    is_archived INTEGER DEFAULT 0,
                    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
                );
            """)

            # 4. schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    day_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                );
            """)

            # 5. exams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exams (
                    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    exam_type TEXT NOT NULL,
                    exam_date TEXT NOT NULL,
                    exam_time TEXT NOT NULL,
                    room_number TEXT NOT NULL,
                    syllabus TEXT DEFAULT '',
                    performance_notes TEXT DEFAULT '',
                    marks_obtained REAL,
                    total_marks REAL DEFAULT 20.0,
                    is_archived INTEGER DEFAULT 0,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                );
            """)

            # 6. attendance_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('Attended', 'Missed')),
                    remarks TEXT DEFAULT '',
                    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE
                );
            """)

            # 7. notification_settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_reminder_offset INTEGER DEFAULT 30,
                    exam_reminder_offset INTEGER DEFAULT 720,
                    daily_summary_time TEXT DEFAULT '21:00',
                    pause_class_alerts INTEGER DEFAULT 0,
                    pause_exam_alerts INTEGER DEFAULT 0,
                    pause_routine_alerts INTEGER DEFAULT 0,
                    youtube_api_key TEXT DEFAULT '',
                    google_classroom_connected INTEGER DEFAULT 0
                );
            """)

            # 8. classroom_items table (for Google Classroom API / Demo Sync)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classroom_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    item_type TEXT DEFAULT 'Assignment',
                    due_date TEXT,
                    status TEXT DEFAULT 'Pending',
                    description TEXT DEFAULT '',
                    external_link TEXT DEFAULT ''
                );
            """)

            conn.commit()

            # Check if database is empty; if so, seed BUBT sample data
            cursor.execute("SELECT COUNT(*) as cnt FROM users;")
            if cursor.fetchone()["cnt"] == 0:
                self.seed_bubt_sample_data(conn)

    def seed_bubt_sample_data(self, conn: Optional[sqlite3.Connection] = None) -> None:
        """Seed rich BUBT DBMS project sample data."""
        own_conn = False
        if conn is None:
            conn = self.get_connection()
            own_conn = True

        cursor = conn.cursor()

        # Clear existing data in reverse FK order
        cursor.execute("DELETE FROM attendance_logs;")
        cursor.execute("DELETE FROM schedules;")
        cursor.execute("DELETE FROM exams;")
        cursor.execute("DELETE FROM courses;")
        cursor.execute("DELETE FROM faculty;")
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM notification_settings;")
        cursor.execute("DELETE FROM classroom_items;")

        # 1. Seed User (from Proposal)
        cursor.execute("""
            INSERT INTO users (full_name, student_id, department, semester, institution, theme_preference, clock_format, week_start_day, onboarded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            "Md. Monirul Hasan",
            "20255103087",
            "Department of CSE",
            "Fall 2026",
            "Bangladesh University of Business and Technology (BUBT)",
            "Dark",
            "12h",
            "Saturday",
            1
        ))

        # 2. Seed Notification Settings
        cursor.execute("""
            INSERT INTO notification_settings (
                class_reminder_offset, exam_reminder_offset, daily_summary_time,
                pause_class_alerts, pause_exam_alerts, pause_routine_alerts,
                youtube_api_key, google_classroom_connected
            ) VALUES (30, 720, '21:00', 0, 0, 0, '', 1);
        """)

        # 3. Seed Faculty Members
        faculty_data = [
            (
                "Farah Akter Munmun",
                "FAM",
                "Assistant Professor",
                "Department of CSE",
                "farha.akhter@bubt.edu.bd",
                "+880 1711-000101",
                "Sun, Tue: 11:30 AM - 01:30 PM | Thu: 02:00 PM - 03:30 PM",
                "Building 2, Room 504"
            ),
            (
                "Dr. Md. Saifur Rahman",
                "MSR",
                "Associate Professor",
                "Department of CSE",
                "saifur.cse@bubt.edu.bd",
                "+880 1711-000202",
                "Sat, Mon: 10:00 AM - 12:00 PM",
                "Building 2, Room 501"
            ),
            (
                "Md. Ashraful Islam",
                "MAI",
                "Assistant Professor",
                "Department of CSE",
                "ashraful.islam@bubt.edu.bd",
                "+880 1711-000303",
                "Sun, Wed: 02:00 PM - 04:00 PM",
                "Building 1, Room 410"
            ),
            (
                "Nusrat Jahan",
                "NJ",
                "Lecturer",
                "Department of CSE",
                "nusrat.jahan@bubt.edu.bd",
                "+880 1711-000404",
                "Mon, Wed: 11:30 AM - 01:00 PM",
                "Building 2, Room 512"
            ),
            (
                "Tanvir Ahmed",
                "TA",
                "Lecturer",
                "Department of Mathematics & Statistics",
                "tanvir.math@bubt.edu.bd",
                "+880 1711-000505",
                "Sat, Tue: 12:30 PM - 02:00 PM",
                "Building 1, Room 604"
            ),
        ]

        faculty_ids = {}
        for f in faculty_data:
            cursor.execute("""
                INSERT INTO faculty (name, short_name, designation, department, email, phone, consulting_hours, office_room)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, f)
            faculty_ids[f[1]] = cursor.lastrowid

        # 4. Seed Courses
        courses_data = [
            ("CSE 208", "Database Management System Lab", "01", "Building 2", "417", faculty_ids["FAM"], "Fall 2026", 0),
            ("CSE 207", "Database Management System", "01", "Building 2", "402", faculty_ids["FAM"], "Fall 2026", 0),
            ("CSE 205", "Algorithms & Complexity Analysis", "01", "Building 2", "305", faculty_ids["MSR"], "Fall 2026", 0),
            ("CSE 206", "Algorithms Lab", "01", "Building 2", "418", faculty_ids["MSR"], "Fall 2026", 0),
            ("CSE 209", "Operating Systems Concepts", "01", "Building 1", "502", faculty_ids["MAI"], "Fall 2026", 0),
            ("CSE 211", "Object Oriented Design & Software Eng.", "01", "Building 2", "409", faculty_ids["NJ"], "Fall 2026", 0),
            ("MATH 203", "Linear Algebra & Differential Equations", "01", "Building 1", "601", faculty_ids["TA"], "Fall 2026", 0),
        ]

        course_ids = {}
        for c in courses_data:
            cursor.execute("""
                INSERT INTO courses (course_code, course_name, section, building_number, room_number, faculty_id, semester, is_archived)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, c)
            course_ids[c[0]] = cursor.lastrowid

        # 5. Seed Weekly Class Routine (Schedules)
        # Note: Proposal highlights CSE 208: Database Management System Lab (8:15 AM - 11:15 AM, Building 2, Room 417, Farah Akter Munmun [FAM])
        # We also place CSE 208 and CSE 207 across key days including Tuesday (today) so the Dashboard Next Class card always shines.
        schedules_data = [
            # Saturday
            (course_ids["CSE 207"], "Saturday", "08:15", "09:45"),
            (course_ids["CSE 205"], "Saturday", "10:00", "11:30"),
            (course_ids["MATH 203"], "Saturday", "11:45", "13:15"),
            # Sunday
            (course_ids["CSE 208"], "Sunday", "08:15", "11:15"),
            (course_ids["CSE 209"], "Sunday", "11:30", "13:00"),
            (course_ids["CSE 211"], "Sunday", "14:00", "15:30"),
            # Monday
            (course_ids["CSE 207"], "Monday", "09:45", "11:15"),
            (course_ids["CSE 206"], "Monday", "11:30", "14:30"),
            (course_ids["MATH 203"], "Monday", "14:45", "16:15"),
            # Tuesday
            (course_ids["CSE 208"], "Tuesday", "08:15", "11:15"),
            (course_ids["CSE 207"], "Tuesday", "13:30", "15:00"),
            (course_ids["CSE 205"], "Tuesday", "15:15", "16:45"),
            # Wednesday
            (course_ids["CSE 209"], "Wednesday", "08:15", "09:45"),
            (course_ids["CSE 211"], "Wednesday", "10:00", "11:30"),
            (course_ids["CSE 207"], "Wednesday", "13:30", "15:00"),
            # Thursday
            (course_ids["CSE 208"], "Thursday", "08:15", "11:15"),
            (course_ids["CSE 205"], "Thursday", "11:30", "13:00"),
            (course_ids["CSE 209"], "Thursday", "14:00", "15:30"),
        ]

        schedule_ids_by_course = {}
        for s in schedules_data:
            cursor.execute("""
                INSERT INTO schedules (course_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?);
            """, s)
            sid = cursor.lastrowid
            schedule_ids_by_course.setdefault(s[0], []).append(sid)

        # 6. Seed Attendance Logs (historical records for realistic percentages)
        today = datetime.now().date()
        attendance_seed = [
            # CSE 208 DBMS Lab: 11 Attended, 1 Missed (~91.7%)
            (course_ids["CSE 208"], 11, 1),
            # CSE 207 DBMS Theory: 14 Attended, 1 Missed (~93.3%)
            (course_ids["CSE 207"], 14, 1),
            # CSE 205 Algorithms: 10 Attended, 2 Missed (~83.3%)
            (course_ids["CSE 205"], 10, 2),
            # CSE 206 Algorithms Lab: 8 Attended, 1 Missed (~88.9%)
            (course_ids["CSE 206"], 8, 1),
            # CSE 209 OS: 9 Attended, 2 Missed (~81.8%)
            (course_ids["CSE 209"], 9, 2),
            # CSE 211 OOD: 10 Attended, 1 Missed (~90.9%)
            (course_ids["CSE 211"], 10, 1),
            # MATH 203 Linear Algebra: 7 Attended, 3 Missed (70.0% - below 75% alert threshold!)
            (course_ids["MATH 203"], 7, 3),
        ]

        for cid, attended_count, missed_count in attendance_seed:
            sids = schedule_ids_by_course.get(cid, [])
            if not sids:
                continue
            primary_sid = sids[0]
            day_offset = 1
            for _ in range(attended_count):
                log_date = (today - timedelta(days=day_offset * 3)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO attendance_logs (schedule_id, date, status, remarks)
                    VALUES (?, ?, 'Attended', 'Present on time');
                """, (primary_sid, log_date))
                day_offset += 1
            for _ in range(missed_count):
                log_date = (today - timedelta(days=day_offset * 3)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO attendance_logs (schedule_id, date, status, remarks)
                    VALUES (?, ?, 'Missed', 'Medical / Personal leave');
                """, (primary_sid, log_date))
                day_offset += 1

        # 7. Seed Exams (Upcoming CTs, Midterms, Finals + Archived Past Exams)
        d_plus_2 = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        d_plus_5 = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        d_plus_9 = (today + timedelta(days=9)).strftime("%Y-%m-%d")
        d_plus_14 = (today + timedelta(days=14)).strftime("%Y-%m-%d")
        d_plus_25 = (today + timedelta(days=25)).strftime("%Y-%m-%d")
        d_minus_12 = (today - timedelta(days=12)).strftime("%Y-%m-%d")
        d_minus_20 = (today - timedelta(days=20)).strftime("%Y-%m-%d")
        d_minus_28 = (today - timedelta(days=28)).strftime("%Y-%m-%d")

        exams_data = [
            # Upcoming Exams
            (
                course_ids["CSE 208"],
                "Lab Final / Project Viva",
                d_plus_2,
                "08:30",
                "Building 2, Room 417",
                "Complete ClassMate Desktop DBMS Project Demo, ER Diagram, 3NF Normalization & SQLite Queries",
                "Project teammates: Md. Monirul Hasan (20255103087) & Yusuf Ali (20255103138)",
                None,
                40.0,
                0
            ),
            (
                course_ids["CSE 207"],
                "CT (Class Test 2)",
                d_plus_5,
                "10:00",
                "Building 2, Room 402",
                "SQL Joins, Subqueries, Views, Indexing & B+ Tree Fundamentals",
                "Review lecture slides 5-8 by Farah Akter Munmun [FAM]",
                None,
                15.0,
                0
            ),
            (
                course_ids["CSE 205"],
                "Midterm",
                d_plus_9,
                "09:30",
                "Building 2, Room 305",
                "Divide & Conquer, Dynamic Programming, Greedy Algorithms, Dijkstra & Bellman-Ford",
                "Bring scientific calculator",
                None,
                30.0,
                0
            ),
            (
                course_ids["CSE 209"],
                "CT (Class Test 2)",
                d_plus_14,
                "11:30",
                "Building 1, Room 502",
                "Deadlocks, Banker's Algorithm, Memory Paging & Virtual Memory",
                "",
                None,
                15.0,
                0
            ),
            (
                course_ids["CSE 207"],
                "Final",
                d_plus_25,
                "09:00",
                "Building 2, Hall 201",
                "Transaction Processing, ACID Properties, Concurrency Control, Two-Phase Locking & Recovery",
                "Comprehensive Term Final Examination",
                None,
                40.0,
                0
            ),
            # Past / Archived Exams (Exam History)
            (
                course_ids["CSE 207"],
                "CT (Class Test 1)",
                d_minus_20,
                "09:45",
                "Building 2, Room 402",
                "ER Modeling, Relational Algebra & Keys (Super, Candidate, Primary, Foreign)",
                "Scored highest in section! Great feedback on ER cardinality notation.",
                14.5,
                15.0,
                1
            ),
            (
                course_ids["CSE 208"],
                "Lab Quiz 1",
                d_minus_12,
                "08:30",
                "Building 2, Room 417",
                "DDL, DML Constraints, INNER/LEFT JOIN & Aggregate GROUP BY HAVING Queries",
                "Solved all 5 SQL queries within 35 minutes.",
                19.0,
                20.0,
                1
            ),
            (
                course_ids["MATH 203"],
                "CT (Class Test 1)",
                d_minus_28,
                "11:45",
                "Building 1, Room 601",
                "Matrix Inversion, Eigenvalues, Eigenvectors & Cayley-Hamilton Theorem",
                "Need more practice on diagonalization steps.",
                11.5,
                15.0,
                1
            ),
        ]

        for ex in exams_data:
            cursor.execute("""
                INSERT INTO exams (
                    course_id, exam_type, exam_date, exam_time, room_number,
                    syllabus, performance_notes, marks_obtained, total_marks, is_archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, ex)

        # 8. Seed Google Classroom Sync Items
        classroom_seed = [
            (
                "CSE 208",
                "Final DBMS Project Submission: ClassMate Desktop App + Proposal Report",
                "Assignment",
                d_plus_2,
                "In Progress",
                "Submit full Python source code, SQLite schema script, ER diagram, and presentation slides to Google Classroom.",
                "https://classroom.google.com"
            ),
            (
                "CSE 207",
                "Assignment 3: Normalization (1NF, 2NF, 3NF, BCNF) Practice Set",
                "Assignment",
                d_plus_5,
                "Pending",
                "Decompose the given unnormalized university hospital relation into 3NF/BCNF preserving dependency.",
                "https://classroom.google.com"
            ),
            (
                "CSE 207",
                "Announcement: Consultation Hours Updated Before CT-2",
                "Announcement",
                today.strftime("%Y-%m-%d"),
                "Posted",
                "Farah Akter Munmun [FAM]: Extra consultation slot opened on Tuesday 11:30 AM - 1:00 PM at Building 2, Room 504.",
                "https://classroom.google.com"
            ),
            (
                "CSE 205",
                "Lab Report 4: Dynamic Programming (0/1 Knapsack & LCS)",
                "Assignment",
                d_plus_9,
                "Pending",
                "Upload C++/Python implementation along with time & space complexity comparison table.",
                "https://classroom.google.com"
            ),
            (
                "CSE 208",
                "Lab Task 3: SQL Triggers, Views & Stored Procedures",
                "Assignment",
                d_minus_12,
                "Submitted",
                "Turned in by Md. Monirul Hasan (ID: 20255103087).",
                "https://classroom.google.com"
            ),
        ]

        for ci in classroom_seed:
            cursor.execute("""
                INSERT INTO classroom_items (course_code, title, item_type, due_date, status, description, external_link)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, ci)

        conn.commit()
        if own_conn:
            conn.close()

    # =========================================================================
    # USER & PREFERENCES
    # =========================================================================

    def get_user(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM users ORDER BY user_id ASC LIMIT 1;").fetchone()
            if row:
                return dict(row)
            return {
                "user_id": 1,
                "full_name": "Md. Monirul Hasan",
                "student_id": "20255103087",
                "department": "Department of CSE",
                "semester": "Fall 2026",
                "institution": "Bangladesh University of Business and Technology (BUBT)",
                "theme_preference": "Dark",
                "clock_format": "12h",
                "week_start_day": "Saturday",
                "onboarded": 0,
            }

    def update_user(
        self,
        full_name: str,
        student_id: str,
        department: str,
        semester: str,
        theme_preference: str,
        clock_format: str,
        week_start_day: str,
        onboarded: int = 1,
    ) -> None:
        with self.get_connection() as conn:
            row = conn.execute("SELECT user_id FROM users ORDER BY user_id ASC LIMIT 1;").fetchone()
            if row:
                conn.execute("""
                    UPDATE users
                    SET full_name = ?, student_id = ?, department = ?, semester = ?,
                        theme_preference = ?, clock_format = ?, week_start_day = ?, onboarded = ?
                    WHERE user_id = ?;
                """, (
                    full_name, student_id, department, semester,
                    theme_preference, clock_format, week_start_day, onboarded, row["user_id"]
                ))
            else:
                conn.execute("""
                    INSERT INTO users (full_name, student_id, department, semester, theme_preference, clock_format, week_start_day, onboarded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (full_name, student_id, department, semester, theme_preference, clock_format, week_start_day, onboarded))
            conn.commit()

    def get_ordered_days(self) -> List[str]:
        """Return the 7 days of the week starting from the user's configured week_start_day."""
        user = self.get_user()
        start_day = user.get("week_start_day", "Saturday")
        if start_day not in self.DAYS_ALL:
            start_day = "Saturday"
        idx = self.DAYS_ALL.index(start_day)
        return self.DAYS_ALL[idx:] + self.DAYS_ALL[:idx]

    def format_time(self, time_24h: str) -> str:
        """Convert 'HH:MM' 24-hour string into user's preferred 12h or 24h display format."""
        if not time_24h:
            return ""
        user = self.get_user()
        fmt = user.get("clock_format", "12h")
        try:
            dt = datetime.strptime(time_24h.strip(), "%H:%M")
            if fmt == "24h":
                return dt.strftime("%H:%M")
            return dt.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            return time_24h

    # =========================================================================
    # FACULTY DIRECTORY CRUD
    # =========================================================================

    def get_all_faculty(self, search_query: str = "") -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if search_query.strip():
                q = f"%{search_query.strip()}%"
                rows = conn.execute("""
                    SELECT * FROM faculty
                    WHERE name LIKE ? OR short_name LIKE ? OR department LIKE ? OR email LIKE ? OR designation LIKE ?
                    ORDER BY name ASC;
                """, (q, q, q, q, q)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM faculty ORDER BY faculty_id ASC;").fetchall()
            return [dict(r) for r in rows]

    def add_faculty(
        self,
        name: str,
        short_name: str,
        designation: str,
        department: str,
        email: str,
        phone: str,
        consulting_hours: str,
        office_room: str = "",
    ) -> int:
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO faculty (name, short_name, designation, department, email, phone, consulting_hours, office_room)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (name, short_name, designation, department, email, phone, consulting_hours, office_room))
            conn.commit()
            return cur.lastrowid

    def update_faculty(
        self,
        faculty_id: int,
        name: str,
        short_name: str,
        designation: str,
        department: str,
        email: str,
        phone: str,
        consulting_hours: str,
        office_room: str = "",
    ) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE faculty
                SET name = ?, short_name = ?, designation = ?, department = ?,
                    email = ?, phone = ?, consulting_hours = ?, office_room = ?
                WHERE faculty_id = ?;
            """, (name, short_name, designation, department, email, phone, consulting_hours, office_room, faculty_id))
            conn.commit()

    def delete_faculty(self, faculty_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM faculty WHERE faculty_id = ?;", (faculty_id,))
            conn.commit()

    # =========================================================================
    # COURSES & SCHEDULES (ROUTINE) CRUD
    # =========================================================================

    def get_courses(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            query = """
                SELECT c.*,
                       f.name AS faculty_name,
                       f.short_name AS faculty_short_name,
                       f.email AS faculty_email
                FROM courses c
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
            """
            if not include_archived:
                query += " WHERE c.is_archived = 0 "
            query += " ORDER BY c.course_code ASC;"
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def add_course(
        self,
        course_code: str,
        course_name: str,
        section: str,
        building_number: str,
        room_number: str,
        faculty_id: Optional[int],
        semester: str = "Fall 2026",
    ) -> int:
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO courses (course_code, course_name, section, building_number, room_number, faculty_id, semester, is_archived)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0);
            """, (course_code, course_name, section, building_number, room_number, faculty_id, semester))
            conn.commit()
            return cur.lastrowid

    def update_course(
        self,
        course_id: int,
        course_code: str,
        course_name: str,
        section: str,
        building_number: str,
        room_number: str,
        faculty_id: Optional[int],
    ) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE courses
                SET course_code = ?, course_name = ?, section = ?, building_number = ?, room_number = ?, faculty_id = ?
                WHERE course_id = ?;
            """, (course_code, course_name, section, building_number, room_number, faculty_id, course_id))
            conn.commit()

    def delete_course(self, course_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM courses WHERE course_id = ?;", (course_id,))
            conn.commit()

    def get_schedules(self, day_of_week: Optional[str] = None, include_archived: bool = False) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            query = """
                SELECT s.schedule_id, s.course_id, s.day_of_week, s.start_time, s.end_time,
                       c.course_code, c.course_name, c.section, c.building_number, c.room_number,
                       c.semester, c.is_archived,
                       COALESCE(f.name, 'TBA') AS faculty_name,
                       COALESCE(f.short_name, 'TBA') AS faculty_short_name
                FROM schedules s
                INNER JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE 1=1
            """
            params: List[Any] = []
            if not include_archived:
                query += " AND c.is_archived = 0"
            if day_of_week:
                query += " AND s.day_of_week = ?"
                params.append(day_of_week)
            query += " ORDER BY s.start_time ASC;"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def add_schedule(self, course_id: int, day_of_week: str, start_time: str, end_time: str) -> int:
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO schedules (course_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?);
            """, (course_id, day_of_week, start_time, end_time))
            conn.commit()
            return cur.lastrowid

    def update_schedule(self, schedule_id: int, course_id: int, day_of_week: str, start_time: str, end_time: str) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE schedules
                SET course_id = ?, day_of_week = ?, start_time = ?, end_time = ?
                WHERE schedule_id = ?;
            """, (course_id, day_of_week, start_time, end_time, schedule_id))
            conn.commit()

    def delete_schedule(self, schedule_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM schedules WHERE schedule_id = ?;", (schedule_id,))
            conn.commit()

    def get_next_class(self) -> Optional[Dict[str, Any]]:
        """
        Determine the immediate upcoming or currently ongoing class across the week.
        Returns enriched dictionary with status ('Ongoing now', 'Today', 'Upcoming on <Day>'),
        formatted times, venue, faculty details, and attendance status for today.
        """
        all_schedules = self.get_schedules(include_archived=False)
        if not all_schedules:
            return None

        now = datetime.now()
        current_day_name = now.strftime("%A")
        current_hm = now.strftime("%H:%M")
        today_str = now.strftime("%Y-%m-%d")

        # 1. Check today's classes that are currently ongoing or upcoming later today
        todays_classes = [s for s in all_schedules if s["day_of_week"] == current_day_name]
        todays_classes.sort(key=lambda x: x["start_time"])

        chosen = None
        badge_text = ""

        for s in todays_classes:
            if s["start_time"] <= current_hm <= s["end_time"]:
                chosen = s
                badge_text = "LIVE NOW • Ongoing Class"
                break
            elif s["start_time"] > current_hm:
                chosen = s
                # Calculate minutes until start
                try:
                    st = datetime.strptime(s["start_time"], "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    diff_mins = max(1, int((st - now).total_seconds() // 60))
                    if diff_mins < 60:
                        badge_text = f"UPCOMING TODAY • Starts in {diff_mins} min"
                    else:
                        hrs = diff_mins // 60
                        mins = diff_mins % 60
                        badge_text = f"UPCOMING TODAY • In {hrs}h {mins}m"
                except ValueError:
                    badge_text = "UPCOMING TODAY"
                break

        # 2. If all of today's classes have ended (or none today), look ahead 1..7 days
        if chosen is None:
            for offset in range(1, 8):
                next_dt = now + timedelta(days=offset)
                next_day_name = next_dt.strftime("%A")
                day_classes = [s for s in all_schedules if s["day_of_week"] == next_day_name]
                if day_classes:
                    day_classes.sort(key=lambda x: x["start_time"])
                    chosen = day_classes[0]
                    if offset == 1:
                        badge_text = f"TOMORROW ({next_day_name})"
                    else:
                        badge_text = f"NEXT UP • {next_day_name}"
                    break

        if chosen is None:
            return None

        result = dict(chosen)
        result["badge_text"] = badge_text
        result["formatted_range"] = f"{self.format_time(result['start_time'])} - {self.format_time(result['end_time'])}"
        result["venue"] = f"{result['building_number']}, Room {result['room_number']}"
        result["instructor_display"] = f"{result['faculty_name']} [{result['faculty_short_name']}]"

        # Check if attendance was already logged today for this schedule
        with self.get_connection() as conn:
            log = conn.execute("""
                SELECT status FROM attendance_logs
                WHERE schedule_id = ? AND date = ?
                ORDER BY log_id DESC LIMIT 1;
            """, (result["schedule_id"], today_str)).fetchone()
            result["today_attendance"] = log["status"] if log else None

        return result

    # =========================================================================
    # ATTENDANCE LOGS & ANALYTICS
    # =========================================================================

    def log_attendance(self, schedule_id: int, status: str, log_date: Optional[str] = None, remarks: str = "") -> int:
        if log_date is None:
            log_date = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            # Check if a log already exists for the same schedule_id and date; if so, update it
            existing = conn.execute("""
                SELECT log_id FROM attendance_logs WHERE schedule_id = ? AND date = ?;
            """, (schedule_id, log_date)).fetchone()
            if existing:
                conn.execute("""
                    UPDATE attendance_logs SET status = ?, remarks = ? WHERE log_id = ?;
                """, (status, remarks, existing["log_id"]))
                conn.commit()
                return existing["log_id"]
            else:
                cur = conn.execute("""
                    INSERT INTO attendance_logs (schedule_id, date, status, remarks)
                    VALUES (?, ?, ?, ?);
                """, (schedule_id, log_date, status, remarks))
                conn.commit()
                return cur.lastrowid

    def get_course_attendance_summary(self) -> List[Dict[str, Any]]:
        """Return attendance statistics per active course (attended, missed, total, percentage)."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT c.course_id, c.course_code, c.course_name, c.section,
                       COALESCE(f.short_name, 'TBA') AS faculty_short_name,
                       SUM(CASE WHEN a.status = 'Attended' THEN 1 ELSE 0 END) AS attended_count,
                       SUM(CASE WHEN a.status = 'Missed' THEN 1 ELSE 0 END) AS missed_count,
                       COUNT(a.log_id) AS total_classes
                FROM courses c
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                LEFT JOIN schedules s ON c.course_id = s.course_id
                LEFT JOIN attendance_logs a ON s.schedule_id = a.schedule_id
                WHERE c.is_archived = 0
                GROUP BY c.course_id
                ORDER BY c.course_code ASC;
            """).fetchall()

            results = []
            for r in rows:
                d = dict(r)
                total = d["total_classes"] or 0
                attended = d["attended_count"] or 0
                pct = round((attended / total) * 100, 1) if total > 0 else 100.0
                d["percentage"] = pct
                results.append(d)
            return results

    def get_recent_attendance_logs(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT a.log_id, a.schedule_id, a.date, a.status, a.remarks,
                       s.day_of_week, s.start_time, s.end_time,
                       c.course_code, c.course_name
                FROM attendance_logs a
                INNER JOIN schedules s ON a.schedule_id = s.schedule_id
                INNER JOIN courses c ON s.course_id = c.course_id
                ORDER BY a.date DESC, a.log_id DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def delete_attendance_log(self, log_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM attendance_logs WHERE log_id = ?;", (log_id,))
            conn.commit()

    # =========================================================================
    # SEMESTER MANAGEMENT & ROUTINE SHARING (EXPORT / IMPORT)
    # =========================================================================

    def transition_new_semester(self, new_semester_name: str, archive_old: bool = True) -> None:
        """Transition to a new semester by archiving or clearing old routines and updating user semester."""
        with self.get_connection() as conn:
            if archive_old:
                conn.execute("UPDATE courses SET is_archived = 1 WHERE is_archived = 0;")
                conn.execute("UPDATE exams SET is_archived = 1 WHERE is_archived = 0;")
            else:
                conn.execute("DELETE FROM courses;")
            conn.execute("UPDATE users SET semester = ?;", (new_semester_name,))
            conn.commit()

    def export_routine_template(self, file_path: str) -> None:
        """Export active courses, faculty references, and weekly schedules to a shareable JSON file."""
        courses = self.get_courses(include_archived=False)
        schedules = self.get_schedules(include_archived=False)
        user = self.get_user()
        payload = {
            "app": "ClassMate – Academic & Learning Assistant",
            "exported_by": user.get("full_name", ""),
            "student_id": user.get("student_id", ""),
            "semester": user.get("semester", "Fall 2026"),
            "exported_at": datetime.now().isoformat(),
            "courses": courses,
            "schedules": schedules,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def import_routine_template(self, file_path: str) -> Tuple[int, int]:
        """Import courses and schedules from a shared JSON routine template."""
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        courses_in = payload.get("courses", [])
        schedules_in = payload.get("schedules", [])

        old_to_new_course_id: Dict[int, int] = {}
        courses_added = 0
        schedules_added = 0

        with self.get_connection() as conn:
            for c in courses_in:
                # Check if course with same code already exists
                existing = conn.execute(
                    "SELECT course_id FROM courses WHERE course_code = ? AND is_archived = 0;",
                    (c.get("course_code", ""),)
                ).fetchone()
                if existing:
                    old_to_new_course_id[c["course_id"]] = existing["course_id"]
                else:
                    cur = conn.execute("""
                        INSERT INTO courses (course_code, course_name, section, building_number, room_number, faculty_id, semester, is_archived)
                        VALUES (?, ?, ?, ?, ?, NULL, ?, 0);
                    """, (
                        c.get("course_code", "CSE 000"),
                        c.get("course_name", "Imported Course"),
                        c.get("section", "01"),
                        c.get("building_number", "Building 2"),
                        c.get("room_number", "401"),
                        c.get("semester", payload.get("semester", "Fall 2026")),
                    ))
                    old_to_new_course_id[c["course_id"]] = cur.lastrowid
                    courses_added += 1

            for s in schedules_in:
                new_cid = old_to_new_course_id.get(s.get("course_id"))
                if new_cid:
                    conn.execute("""
                        INSERT INTO schedules (course_id, day_of_week, start_time, end_time)
                        VALUES (?, ?, ?, ?);
                    """, (new_cid, s.get("day_of_week", "Saturday"), s.get("start_time", "08:15"), s.get("end_time", "09:45")))
                    schedules_added += 1

            conn.commit()
        return courses_added, schedules_added

    # =========================================================================
    # EXAMS & ASSESSMENTS CRUD
    # =========================================================================

    def get_exams(self, archived: Optional[bool] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            query = """
                SELECT e.*,
                       c.course_code, c.course_name, c.section,
                       COALESCE(f.short_name, 'TBA') AS faculty_short_name
                FROM exams e
                INNER JOIN courses c ON e.course_id = c.course_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE 1=1
            """
            params: List[Any] = []
            if archived is not None:
                query += " AND e.is_archived = ?"
                params.append(1 if archived else 0)
            query += " ORDER BY e.exam_date ASC, e.exam_time ASC;"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def add_exam(
        self,
        course_id: int,
        exam_type: str,
        exam_date: str,
        exam_time: str,
        room_number: str,
        syllabus: str = "",
        performance_notes: str = "",
        marks_obtained: Optional[float] = None,
        total_marks: float = 20.0,
        is_archived: int = 0,
    ) -> int:
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO exams (
                    course_id, exam_type, exam_date, exam_time, room_number,
                    syllabus, performance_notes, marks_obtained, total_marks, is_archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                course_id, exam_type, exam_date, exam_time, room_number,
                syllabus, performance_notes, marks_obtained, total_marks, is_archived
            ))
            conn.commit()
            return cur.lastrowid

    def update_exam(
        self,
        exam_id: int,
        course_id: int,
        exam_type: str,
        exam_date: str,
        exam_time: str,
        room_number: str,
        syllabus: str,
        performance_notes: str,
        marks_obtained: Optional[float],
        total_marks: float,
        is_archived: int,
    ) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE exams
                SET course_id = ?, exam_type = ?, exam_date = ?, exam_time = ?, room_number = ?,
                    syllabus = ?, performance_notes = ?, marks_obtained = ?, total_marks = ?, is_archived = ?
                WHERE exam_id = ?;
            """, (
                course_id, exam_type, exam_date, exam_time, room_number,
                syllabus, performance_notes, marks_obtained, total_marks, is_archived, exam_id
            ))
            conn.commit()

    def archive_exam_with_notes(self, exam_id: int, marks_obtained: Optional[float], performance_notes: str) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE exams
                SET is_archived = 1, marks_obtained = ?, performance_notes = ?
                WHERE exam_id = ?;
            """, (marks_obtained, performance_notes, exam_id))
            conn.commit()

    def delete_exam(self, exam_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM exams WHERE exam_id = ?;", (exam_id,))
            conn.commit()

    # =========================================================================
    # NOTIFICATION SETTINGS
    # =========================================================================

    def get_notification_settings(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM notification_settings ORDER BY setting_id ASC LIMIT 1;").fetchone()
            if row:
                return dict(row)
            return {
                "setting_id": 1,
                "class_reminder_offset": 30,
                "exam_reminder_offset": 720,
                "daily_summary_time": "21:00",
                "pause_class_alerts": 0,
                "pause_exam_alerts": 0,
                "pause_routine_alerts": 0,
                "youtube_api_key": "",
                "google_classroom_connected": 1,
            }

    def update_notification_settings(
        self,
        class_reminder_offset: int,
        exam_reminder_offset: int,
        daily_summary_time: str,
        pause_class_alerts: int,
        pause_exam_alerts: int,
        pause_routine_alerts: int,
        youtube_api_key: str = "",
        google_classroom_connected: int = 1,
    ) -> None:
        with self.get_connection() as conn:
            row = conn.execute("SELECT setting_id FROM notification_settings ORDER BY setting_id ASC LIMIT 1;").fetchone()
            if row:
                conn.execute("""
                    UPDATE notification_settings
                    SET class_reminder_offset = ?, exam_reminder_offset = ?, daily_summary_time = ?,
                        pause_class_alerts = ?, pause_exam_alerts = ?, pause_routine_alerts = ?,
                        youtube_api_key = ?, google_classroom_connected = ?
                    WHERE setting_id = ?;
                """, (
                    class_reminder_offset, exam_reminder_offset, daily_summary_time,
                    pause_class_alerts, pause_exam_alerts, pause_routine_alerts,
                    youtube_api_key, google_classroom_connected, row["setting_id"]
                ))
            else:
                conn.execute("""
                    INSERT INTO notification_settings (
                        class_reminder_offset, exam_reminder_offset, daily_summary_time,
                        pause_class_alerts, pause_exam_alerts, pause_routine_alerts,
                        youtube_api_key, google_classroom_connected
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    class_reminder_offset, exam_reminder_offset, daily_summary_time,
                    pause_class_alerts, pause_exam_alerts, pause_routine_alerts,
                    youtube_api_key, google_classroom_connected
                ))
            conn.commit()

    # =========================================================================
    # GOOGLE CLASSROOM ITEMS
    # =========================================================================

    def get_classroom_items(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM classroom_items ORDER BY due_date ASC, item_id DESC;").fetchall()
            return [dict(r) for r in rows]

    def add_classroom_item(
        self,
        course_code: str,
        title: str,
        item_type: str,
        due_date: str,
        status: str = "Pending",
        description: str = "",
        external_link: str = "https://classroom.google.com",
    ) -> int:
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO classroom_items (course_code, title, item_type, due_date, status, description, external_link)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (course_code, title, item_type, due_date, status, description, external_link))
            conn.commit()
            return cur.lastrowid

    def update_classroom_item_status(self, item_id: int, status: str) -> None:
        with self.get_connection() as conn:
            conn.execute("UPDATE classroom_items SET status = ? WHERE item_id = ?;", (status, item_id))
            conn.commit()

    def delete_classroom_item(self, item_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM classroom_items WHERE item_id = ?;", (item_id,))
            conn.commit()

    # =========================================================================
    # DBMS STATS & SCHEMA DIAGNOSTICS
    # =========================================================================

    def get_db_statistics(self) -> Dict[str, int]:
        tables = [
            "users",
            "faculty",
            "courses",
            "schedules",
            "exams",
            "attendance_logs",
            "notification_settings",
            "classroom_items",
        ]
        stats: Dict[str, int] = {}
        with self.get_connection() as conn:
            for t in tables:
                row = conn.execute(f"SELECT COUNT(*) AS cnt FROM {t};").fetchone()
                stats[t] = row["cnt"] if row else 0
        return stats

