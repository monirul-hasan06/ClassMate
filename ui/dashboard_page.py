from datetime import datetime
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager


class DashboardPage(QWidget):
    """
    Smart Time-Aware Dashboard Page (Proposal Section 4.1).
    Features:
      - Contextual Time-of-Day Greeting (e.g., "Good Afternoon, Md. Monirul Hasan")
      - Prominent "Next Class" Widget Card with Course Code & Name, Schedule & Duration,
        Venue (Building & Room), Instructor Name & Short Name [FAM], and Quick Attendance Logger
      - Per-Course Attendance Tracker with <75% Shortfall Warning
      - Today's Class Timeline & Upcoming Assessments
    """

    def __init__(self, db: DatabaseManager, on_navigate: Optional[Callable[[str], None]] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.on_navigate = on_navigate
        self.current_card_schedule: Optional[Dict[str, Any]] = None
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(24, 20, 24, 24)
        self.main_layout.setSpacing(18)

        # 1. Top Greeting & Summary Banner
        greeting_frame = QFrame()
        greeting_frame.setProperty("class", "Card")
        greeting_layout = QHBoxLayout(greeting_frame)
        greeting_layout.setContentsMargins(20, 16, 20, 16)

        greet_left = QVBoxLayout()
        self.lbl_greeting = QLabel("Good Afternoon, Md. Monirul Hasan")
        self.lbl_greeting.setProperty("class", "PageTitle")
        self.lbl_sub_greeting = QLabel("Student ID: 20255103087 • Department of CSE • BUBT")
        self.lbl_sub_greeting.setProperty("class", "MutedText")
        greet_left.addWidget(self.lbl_greeting)
        greet_left.addWidget(self.lbl_sub_greeting)

        greet_right = QVBoxLayout()
        greet_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_date = QLabel("")
        self.lbl_date.setStyleSheet("font-weight: 700; font-size: 14px;")
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_semester_badge = QLabel("Semester: Fall 2026")
        self.lbl_semester_badge.setProperty("class", "MutedText")
        self.lbl_semester_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        greet_right.addWidget(self.lbl_date)
        greet_right.addWidget(self.lbl_semester_badge)

        greeting_layout.addLayout(greet_left, 1)
        greeting_layout.addLayout(greet_right)
        self.main_layout.addWidget(greeting_frame)

        # 2. Next Class Hero Widget Card
        self.next_class_card = QFrame()
        self.next_class_card.setProperty("class", "HeroCard")
        nc_layout = QVBoxLayout(self.next_class_card)
        nc_layout.setContentsMargins(22, 18, 22, 18)
        nc_layout.setSpacing(12)

        # Top row of Next Class Card: Status Badge + Class Selector for Demo/Viva flexibility
        nc_top_row = QHBoxLayout()
        self.lbl_nc_badge = QLabel("⚡ NEXT UPCOMING CLASS")
        self.lbl_nc_badge.setStyleSheet(
            "background-color: #4F46E5; color: #FFFFFF; font-weight: 800; font-size: 11px; "
            "padding: 5px 12px; border-radius: 12px; letter-spacing: 0.6px;"
        )
        nc_top_row.addWidget(self.lbl_nc_badge)
        nc_top_row.addStretch()

        lbl_pin = QLabel("Card View:")
        lbl_pin.setProperty("class", "MutedText")
        self.combo_class_pin = QComboBox()
        self.combo_class_pin.setMinimumWidth(290)
        self.combo_class_pin.currentIndexChanged.connect(self._on_pin_changed)
        nc_top_row.addWidget(lbl_pin)
        nc_top_row.addWidget(self.combo_class_pin)
        nc_layout.addLayout(nc_top_row)

        # Course Code & Course Name
        self.lbl_nc_title = QLabel("CSE 208: Database Management System Lab")
        self.lbl_nc_title.setStyleSheet("font-size: 22px; font-weight: 800;")
        self.lbl_nc_title.setWordWrap(True)
        nc_layout.addWidget(self.lbl_nc_title)

        # Details Grid: Schedule & Duration | Venue | Instructor
        details_grid = QGridLayout()
        details_grid.setHorizontalSpacing(24)
        details_grid.setVerticalSpacing(6)

        self.lbl_nc_schedule = QLabel("🕒 Schedule: 8:15 AM - 11:15 AM (Tuesday)")
        self.lbl_nc_schedule.setStyleSheet("font-size: 14px; font-weight: 600;")

        self.lbl_nc_venue = QLabel("🏢 Venue: Building 2, Room 417")
        self.lbl_nc_venue.setStyleSheet("font-size: 14px; font-weight: 600;")

        self.lbl_nc_instructor = QLabel("👩‍🏫 Instructor: Farah Akter Munmun [FAM]")
        self.lbl_nc_instructor.setStyleSheet("font-size: 14px; font-weight: 600;")

        self.lbl_nc_status = QLabel("📋 Today's Log: Not marked yet")
        self.lbl_nc_status.setStyleSheet("font-size: 13px; font-weight: 700; color: #F59E0B;")

        details_grid.addWidget(self.lbl_nc_schedule, 0, 0)
        details_grid.addWidget(self.lbl_nc_venue, 0, 1)
        details_grid.addWidget(self.lbl_nc_instructor, 1, 0)
        details_grid.addWidget(self.lbl_nc_status, 1, 1)
        nc_layout.addLayout(details_grid)

        # Quick Attendance Logger Action Bar
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        lbl_quick = QLabel("Quick Attendance Logger:")
        lbl_quick.setStyleSheet("font-weight: 700;")

        self.btn_mark_attended = QPushButton("✓ Mark Attended")
        self.btn_mark_attended.setProperty("class", "SuccessBtn")
        self.btn_mark_attended.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mark_attended.clicked.connect(lambda: self._quick_log_attendance("Attended"))

        self.btn_mark_missed = QPushButton("✗ Mark Missed")
        self.btn_mark_missed.setProperty("class", "DangerBtn")
        self.btn_mark_missed.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mark_missed.clicked.connect(lambda: self._quick_log_attendance("Missed"))

        btn_view_routine = QPushButton("📅 Full Weekly Routine →")
        btn_view_routine.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view_routine.clicked.connect(lambda: self.on_navigate("routine") if self.on_navigate else None)

        action_row.addWidget(lbl_quick)
        action_row.addWidget(self.btn_mark_attended)
        action_row.addWidget(self.btn_mark_missed)
        action_row.addStretch()
        action_row.addWidget(btn_view_routine)
        nc_layout.addLayout(action_row)

        self.main_layout.addWidget(self.next_class_card)

        # 3. Middle Row: Today's Classes + Upcoming Exams
        mid_row = QHBoxLayout()
        mid_row.setSpacing(18)

        # Left: Today's Schedule Card
        today_card = QFrame()
        today_card.setProperty("class", "Card")
        today_layout = QVBoxLayout(today_card)
        today_layout.setContentsMargins(18, 16, 18, 16)
        today_layout.setSpacing(10)

        self.lbl_today_header = QLabel("📚 Today's Class Schedule")
        self.lbl_today_header.setProperty("class", "SectionTitle")
        today_layout.addWidget(self.lbl_today_header)

        self.today_list_layout = QVBoxLayout()
        self.today_list_layout.setSpacing(8)
        today_layout.addLayout(self.today_list_layout)
        today_layout.addStretch()

        # Right: Upcoming Exams & Assessments Card
        exams_card = QFrame()
        exams_card.setProperty("class", "Card")
        exams_layout = QVBoxLayout(exams_card)
        exams_layout.setContentsMargins(18, 16, 18, 16)
        exams_layout.setSpacing(10)

        ex_header_row = QHBoxLayout()
        lbl_ex_header = QLabel("📝 Upcoming Exams & Assessments")
        lbl_ex_header.setProperty("class", "SectionTitle")
        btn_all_exams = QPushButton("Manage Exams →")
        btn_all_exams.clicked.connect(lambda: self.on_navigate("exams") if self.on_navigate else None)
        ex_header_row.addWidget(lbl_ex_header)
        ex_header_row.addStretch()
        ex_header_row.addWidget(btn_all_exams)
        exams_layout.addLayout(ex_header_row)

        self.upcoming_exams_layout = QVBoxLayout()
        self.upcoming_exams_layout.setSpacing(8)
        exams_layout.addLayout(self.upcoming_exams_layout)
        exams_layout.addStretch()

        mid_row.addWidget(today_card, 1)
        mid_row.addWidget(exams_card, 1)
        self.main_layout.addLayout(mid_row)

        # 4. Bottom Card: Course Attendance Percentage Tracker
        att_card = QFrame()
        att_card.setProperty("class", "Card")
        att_layout = QVBoxLayout(att_card)
        att_layout.setContentsMargins(18, 16, 18, 16)
        att_layout.setSpacing(12)

        att_top = QHBoxLayout()
        lbl_att_title = QLabel("📊 Course-Wise Attendance Analytics (Minimum 75% Target)")
        lbl_att_title.setProperty("class", "SectionTitle")
        self.lbl_overall_att = QLabel("Overall Attendance: --%")
        self.lbl_overall_att.setStyleSheet("font-weight: 800; color: #10B981;")
        att_top.addWidget(lbl_att_title)
        att_top.addStretch()
        att_top.addWidget(self.lbl_overall_att)
        att_layout.addLayout(att_top)

        self.att_bars_layout = QVBoxLayout()
        self.att_bars_layout.setSpacing(10)
        att_layout.addLayout(self.att_bars_layout)

        self.main_layout.addWidget(att_card)
        self.main_layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

    def _get_time_greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        elif 17 <= hour < 21:
            return "Good Evening"
        else:
            return "Good Night"

    def refresh_data(self) -> None:
        user = self.db.get_user()
        greeting = self._get_time_greeting()
        self.lbl_greeting.setText(f"👋 {greeting}, {user.get('full_name', 'Student')}")
        self.lbl_sub_greeting.setText(
            f"Student ID: {user.get('student_id', '')}  •  {user.get('department', 'CSE')}  •  {user.get('institution', 'BUBT')}"
        )
        now = datetime.now()
        self.lbl_date.setText(now.strftime("%A, %B %d, %Y"))
        self.lbl_semester_badge.setText(
            f"Semester: {user.get('semester', 'Fall 2026')}  •  Week Starts: {user.get('week_start_day', 'Saturday')}"
        )

        # Populate Class Pin Selector
        all_schedules = self.db.get_schedules(include_archived=False)
        self.combo_class_pin.blockSignals(True)
        current_data = self.combo_class_pin.currentData()
        self.combo_class_pin.clear()
        self.combo_class_pin.addItem("⚡ Auto (Immediate Upcoming Class)", None)
        for s in all_schedules:
            label = f"{s['course_code']}: {s['course_name']} ({s['day_of_week']} {self.db.format_time(s['start_time'])})"
            self.combo_class_pin.addItem(label, s["schedule_id"])
        if current_data is not None:
            idx = self.combo_class_pin.findData(current_data)
            if idx >= 0:
                self.combo_class_pin.setCurrentIndex(idx)
        self.combo_class_pin.blockSignals(False)

        self._update_next_class_card()
        self._populate_today_classes()
        self._populate_upcoming_exams()
        self._populate_attendance_bars()

    def _on_pin_changed(self) -> None:
        self._update_next_class_card()

    def _update_next_class_card(self) -> None:
        pinned_sid = self.combo_class_pin.currentData()
        if pinned_sid is not None:
            all_schedules = self.db.get_schedules(include_archived=False)
            chosen = next((s for s in all_schedules if s["schedule_id"] == pinned_sid), None)
            if chosen:
                chosen = dict(chosen)
                chosen["badge_text"] = f"PINNED PREVIEW • {chosen['day_of_week']}"
                chosen["formatted_range"] = f"{self.db.format_time(chosen['start_time'])} - {self.db.format_time(chosen['end_time'])}"
                chosen["venue"] = f"{chosen['building_number']}, Room {chosen['room_number']}"
                chosen["instructor_display"] = f"{chosen['faculty_name']} [{chosen['faculty_short_name']}]"
                today_str = datetime.now().strftime("%Y-%m-%d")
                with self.db.get_connection() as conn:
                    log = conn.execute(
                        "SELECT status FROM attendance_logs WHERE schedule_id = ? AND date = ? ORDER BY log_id DESC LIMIT 1;",
                        (chosen["schedule_id"], today_str),
                    ).fetchone()
                    chosen["today_attendance"] = log["status"] if log else None
                next_cls = chosen
            else:
                next_cls = self.db.get_next_class()
        else:
            next_cls = self.db.get_next_class()

        self.current_card_schedule = next_cls
        if not next_cls:
            self.lbl_nc_badge.setText("NO SCHEDULED CLASSES")
            self.lbl_nc_title.setText("No active classes found in your routine")
            self.lbl_nc_schedule.setText("🕒 Schedule: --")
            self.lbl_nc_venue.setText("🏢 Venue: --")
            self.lbl_nc_instructor.setText("👩‍🏫 Instructor: --")
            self.lbl_nc_status.setText("Add courses & schedules in the Class Routine tab")
            self.btn_mark_attended.setEnabled(False)
            self.btn_mark_missed.setEnabled(False)
            return

        self.btn_mark_attended.setEnabled(True)
        self.btn_mark_missed.setEnabled(True)

        self.lbl_nc_badge.setText(f"⚡ {next_cls['badge_text']}")
        self.lbl_nc_title.setText(f"{next_cls['course_code']}: {next_cls['course_name']}")
        self.lbl_nc_schedule.setText(
            f"🕒 Schedule & Duration: {next_cls['formatted_range']} ({next_cls['day_of_week']})"
        )
        self.lbl_nc_venue.setText(f"🏢 Venue: {next_cls['venue']} (Sec {next_cls['section']})")
        self.lbl_nc_instructor.setText(f"👩‍🏫 Instructor: {next_cls['instructor_display']}")

        att = next_cls.get("today_attendance")
        if att == "Attended":
            self.lbl_nc_status.setText("✅ Today's Attendance: Marked as ATTENDED")
            self.lbl_nc_status.setStyleSheet("font-size: 13px; font-weight: 700; color: #10B981;")
        elif att == "Missed":
            self.lbl_nc_status.setText("❌ Today's Attendance: Marked as MISSED")
            self.lbl_nc_status.setStyleSheet("font-size: 13px; font-weight: 700; color: #EF4444;")
        else:
            self.lbl_nc_status.setText("📋 Today's Attendance: Not logged yet")
            self.lbl_nc_status.setStyleSheet("font-size: 13px; font-weight: 700; color: #F59E0B;")

    def _quick_log_attendance(self, status: str) -> None:
        if not self.current_card_schedule:
            return
        sid = self.current_card_schedule["schedule_id"]
        course_code = self.current_card_schedule["course_code"]
        course_name = self.current_card_schedule["course_name"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        self.db.log_attendance(
            schedule_id=sid,
            status=status,
            log_date=today_str,
            remarks=f"Logged via Dashboard Quick Logger ({today_str})",
        )
        self._update_next_class_card()
        self._populate_attendance_bars()
        QMessageBox.information(
            self,
            "Attendance Logged",
            f"Marked '{course_code}: {course_name}' as {status.upper()} for today ({today_str}).",
        )

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _populate_today_classes(self) -> None:
        self._clear_layout(self.today_list_layout)
        today_name = datetime.now().strftime("%A")
        self.lbl_today_header.setText(f"📚 Today's Class Schedule ({today_name})")

        classes = self.db.get_schedules(day_of_week=today_name, include_archived=False)
        if not classes:
            empty_lbl = QLabel(f"🎉 No classes scheduled for {today_name}. Enjoy your study day!")
            empty_lbl.setProperty("class", "MutedText")
            empty_lbl.setWordWrap(True)
            self.today_list_layout.addWidget(empty_lbl)
            return

        for c in classes:
            row_card = QFrame()
            row_card.setProperty("class", "SubCard")
            rl = QHBoxLayout(row_card)
            rl.setContentsMargins(12, 10, 12, 10)

            left_col = QVBoxLayout()
            t_lbl = QLabel(f"{c['course_code']} • {c['course_name']}")
            t_lbl.setStyleSheet("font-weight: 700;")
            s_lbl = QLabel(
                f"🕒 {self.db.format_time(c['start_time'])} - {self.db.format_time(c['end_time'])}  |  "
                f"🏢 {c['building_number']}, Room {c['room_number']}  |  👩‍🏫 {c['faculty_short_name']}"
            )
            s_lbl.setProperty("class", "MutedText")
            left_col.addWidget(t_lbl)
            left_col.addWidget(s_lbl)
            rl.addLayout(left_col, 1)

            self.today_list_layout.addWidget(row_card)

    def _populate_upcoming_exams(self) -> None:
        self._clear_layout(self.upcoming_exams_layout)
        exams = self.db.get_exams(archived=False)
        if not exams:
            empty_lbl = QLabel("No upcoming exams scheduled.")
            empty_lbl.setProperty("class", "MutedText")
            self.upcoming_exams_layout.addWidget(empty_lbl)
            return

        today = datetime.now().date()
        for ex in exams[:4]:
            row_card = QFrame()
            row_card.setProperty("class", "SubCard")
            rl = QHBoxLayout(row_card)
            rl.setContentsMargins(12, 10, 12, 10)

            left = QVBoxLayout()
            title = QLabel(f"[{ex['exam_type']}] {ex['course_code']}: {ex['course_name']}")
            title.setStyleSheet("font-weight: 700;")
            sub = QLabel(
                f"📅 {ex['exam_date']} at {self.db.format_time(ex['exam_time'])}  •  📍 {ex['room_number']}"
            )
            sub.setProperty("class", "MutedText")
            left.addWidget(title)
            left.addWidget(sub)

            badge = QLabel("")
            try:
                ex_dt = datetime.strptime(ex["exam_date"], "%Y-%m-%d").date()
                days_left = (ex_dt - today).days
                if days_left == 0:
                    badge.setText("TODAY")
                    badge.setStyleSheet("color: #EF4444; font-weight: 800;")
                elif days_left > 0:
                    badge.setText(f"In {days_left}d")
                    badge.setStyleSheet("color: #F59E0B; font-weight: 800;")
                else:
                    badge.setText("Completed")
            except ValueError:
                badge.setText(ex["exam_date"])

            rl.addLayout(left, 1)
            rl.addWidget(badge)
            self.upcoming_exams_layout.addWidget(row_card)

    def _populate_attendance_bars(self) -> None:
        self._clear_layout(self.att_bars_layout)
        summaries = self.db.get_course_attendance_summary()
        if not summaries:
            return

        total_att = sum(s["attended_count"] or 0 for s in summaries)
        total_cls = sum(s["total_classes"] or 0 for s in summaries)
        overall_pct = round((total_att / total_cls) * 100, 1) if total_cls > 0 else 100.0
        self.lbl_overall_att.setText(
            f"Overall Term Attendance: {overall_pct}% ({total_att}/{total_cls} classes)"
        )

        for s in summaries:
            row_w = QWidget()
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(12)

            pct = s["percentage"]
            status_tag = "⚠️ Below 75%" if pct < 75.0 else "✓ Good Standing"
            lbl_course = QLabel(
                f"{s['course_code']}: {s['course_name']} [{s['faculty_short_name']}]"
            )
            lbl_course.setMinimumWidth(310)
            lbl_course.setStyleSheet("font-weight: 600;")

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(round(pct)))
            bar.setFormat(f"{pct}% ({s['attended_count'] or 0}/{s['total_classes'] or 0})")
            if pct < 75.0:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #EF4444; border-radius: 5px; }")
            elif pct < 85.0:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #F59E0B; border-radius: 5px; }")
            else:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #10B981; border-radius: 5px; }")

            lbl_tag = QLabel(status_tag)
            lbl_tag.setMinimumWidth(115)
            lbl_tag.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl_tag.setStyleSheet(
                f"font-weight: 700; color: {'#EF4444' if pct < 75.0 else '#10B981'};"
            )

            rl.addWidget(lbl_course)
            rl.addWidget(bar, 1)
            rl.addWidget(lbl_tag)
            self.att_bars_layout.addWidget(row_w)
