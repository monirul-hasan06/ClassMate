import shutil
from typing import Callable, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager
from services.notification_service import NotificationService
from ui.resources import get_app_logo_pixmap


class SettingsPage(QWidget):
    """
    Comprehensive Settings, Notification Controls & About ClassMate Page (Proposal Sections 4.5 & 4.6).
    """

    def __init__(
        self,
        db: DatabaseManager,
        notification_service: NotificationService,
        on_settings_applied: Optional[Callable[[], None]] = None,
        on_open_onboarding: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.notification_service = notification_service
        self.on_settings_applied = on_settings_applied
        self.on_open_onboarding = on_open_onboarding
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(18)

        # Page Header
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        lbl_title = QLabel("⚙️ Settings, Notification Engine & About ClassMate")
        lbl_title.setProperty("class", "PageTitle")
        lbl_sub = QLabel(
            "Configure profile, UI theme (Light/Dark/System), calendar start day, 12h/24h clock, and granular notification rules"
        )
        lbl_sub.setProperty("class", "MutedText")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header_row.addLayout(title_col, 1)

        btn_wizard = QPushButton("🎓 Launch Onboarding Wizard")
        btn_wizard.clicked.connect(lambda: self.on_open_onboarding() if self.on_open_onboarding else None)

        btn_save_all = QPushButton("💾 Save All Settings")
        btn_save_all.setProperty("class", "PrimaryBtn")
        btn_save_all.clicked.connect(self._save_all_settings)

        header_row.addWidget(btn_wizard)
        header_row.addWidget(btn_save_all)
        layout.addLayout(header_row)

        # Two-column top layout: Left = Profile + UI/Calendar/Clock | Right = Smart Notification Controls
        top_grid = QHBoxLayout()
        top_grid.setSpacing(18)

        # --- LEFT CARD: Profile, Theme, Calendar & Clock ---
        left_card = QFrame()
        left_card.setProperty("class", "Card")
        lc_layout = QVBoxLayout(left_card)
        lc_layout.setContentsMargins(18, 16, 18, 16)
        lc_layout.setSpacing(12)

        lbl_prof = QLabel("👤 Profile, Theme & Calendar Preferences")
        lbl_prof.setProperty("class", "SectionTitle")
        lc_layout.addWidget(lbl_prof)

        # Quick Team Switcher
        team_row = QHBoxLayout()
        btn_p1 = QPushButton("Switch: Md. Monirul Hasan (20255103087)")
        btn_p2 = QPushButton("Switch: Yusuf Ali (20255103138)")
        btn_p1.clicked.connect(lambda: self._quick_profile("Md. Monirul Hasan", "20255103087"))
        btn_p2.clicked.connect(lambda: self._quick_profile("Yusuf Ali", "20255103138"))
        team_row.addWidget(btn_p1)
        team_row.addWidget(btn_p2)
        lc_layout.addLayout(team_row)

        prof_form = QFormLayout()
        prof_form.setSpacing(10)

        self.name_edit = QLineEdit()
        self.id_edit = QLineEdit()
        self.dept_edit = QLineEdit()
        self.sem_edit = QLineEdit()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])

        self.clock_combo = QComboBox()
        self.clock_combo.addItems(["12h", "24h"])

        self.week_combo = QComboBox()
        self.week_combo.addItems(["Saturday", "Sunday", "Monday"])

        prof_form.addRow("Student Full Name:", self.name_edit)
        prof_form.addRow("Academic Student ID:", self.id_edit)
        prof_form.addRow("Department:", self.dept_edit)
        prof_form.addRow("Current Semester:", self.sem_edit)
        prof_form.addRow("UI Theme Mode:", self.theme_combo)
        prof_form.addRow("Clock Format (12h / 24h):", self.clock_combo)
        prof_form.addRow("Week Starting Day:", self.week_combo)
        lc_layout.addLayout(prof_form)
        lc_layout.addStretch()

        # --- RIGHT CARD: Smart Notification & Alert System ---
        right_card = QFrame()
        right_card.setProperty("class", "Card")
        rc_layout = QVBoxLayout(right_card)
        rc_layout.setContentsMargins(18, 16, 18, 16)
        rc_layout.setSpacing(12)

        lbl_notif = QLabel("🔔 Smart Notification & Granular Alert Controls")
        lbl_notif.setProperty("class", "SectionTitle")
        rc_layout.addWidget(lbl_notif)

        notif_form = QFormLayout()
        notif_form.setSpacing(10)

        self.class_offset_combo = QComboBox()
        self.class_offset_combo.addItem("15 minutes before class", 15)
        self.class_offset_combo.addItem("30 minutes before class (Recommended)", 30)
        self.class_offset_combo.addItem("1 hour (60 mins) before class", 60)
        self.class_offset_combo.addItem("2 hours (120 mins) before class", 120)
        self.class_offset_combo.addItem("12 hours (720 mins) prior", 720)

        self.exam_offset_combo = QComboBox()
        self.exam_offset_combo.addItem("1 hour (60 mins) before exam", 60)
        self.exam_offset_combo.addItem("6 hours (360 mins) before exam", 360)
        self.exam_offset_combo.addItem("12 hours (720 mins) prior (Recommended)", 720)
        self.exam_offset_combo.addItem("24 hours (1 day) prior", 1440)

        self.summary_time_edit = QLineEdit("21:00")
        self.summary_time_edit.setPlaceholderText("HH:MM (e.g., 21:00 for 9:00 PM nightly summary)")

        self.yt_key_edit = QLineEdit()
        self.yt_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.yt_key_edit.setPlaceholderText("Optional YouTube Data API v3 Key (leave blank for built-in engine)")

        notif_form.addRow("Class Reminder Interval:", self.class_offset_combo)
        notif_form.addRow("Exam Reminder Interval:", self.exam_offset_combo)
        notif_form.addRow("Nightly Routine Summary (24h):", self.summary_time_edit)

        yt_row = QHBoxLayout()
        yt_logo = QLabel()
        yt_logo.setPixmap(get_app_logo_pixmap(32, 32))
        yt_logo.setFixedSize(32, 32)
        yt_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        yt_row.addWidget(yt_logo)
        yt_row.addWidget(self.yt_key_edit, 1)
        notif_form.addRow("YouTube API v3 Key:", yt_row)
        rc_layout.addLayout(notif_form)

        # Granular Pause Controls
        self.chk_pause_class = QCheckBox("⏸️ Pause Class Reminders (Keep Exam & Global Alerts Active)")
        self.chk_pause_exam = QCheckBox("⏸️ Pause Midterm / CT / Final Exam Reminders")
        self.chk_pause_routine = QCheckBox("⏸️ Pause Nightly Weekly Routine Summary Alerts")

        rc_layout.addWidget(self.chk_pause_class)
        rc_layout.addWidget(self.chk_pause_exam)
        rc_layout.addWidget(self.chk_pause_routine)

        # Demo Test Buttons
        test_row = QHBoxLayout()
        btn_test_cls = QPushButton("🔔 Test Class Alert")
        btn_test_cls.clicked.connect(lambda: self.notification_service.trigger_demo_notification("class"))
        btn_test_ex = QPushButton("🔔 Test Exam Alert")
        btn_test_ex.clicked.connect(lambda: self.notification_service.trigger_demo_notification("exam"))
        btn_test_sum = QPushButton("🌙 Test Nightly Summary")
        btn_test_sum.clicked.connect(lambda: self.notification_service.trigger_demo_notification("summary"))
        test_row.addWidget(btn_test_cls)
        test_row.addWidget(btn_test_ex)
        test_row.addWidget(btn_test_sum)
        rc_layout.addLayout(test_row)
        rc_layout.addStretch()

        top_grid.addWidget(left_card, 1)
        top_grid.addWidget(right_card, 1)
        layout.addLayout(top_grid)

        # --- MIDDLE CARD: SQLite3 Relational Database Inspector & Backup ---
        db_card = QFrame()
        db_card.setProperty("class", "Card")
        db_layout = QVBoxLayout(db_card)
        db_layout.setContentsMargins(18, 16, 18, 16)
        db_layout.setSpacing(10)

        db_top = QHBoxLayout()
        lbl_db_title = QLabel("🗄️ SQLite3 Local RDBMS Schema & Table Statistics")
        lbl_db_title.setProperty("class", "SectionTitle")
        self.lbl_db_path = QLabel("")
        self.lbl_db_path.setProperty("class", "MutedText")
        db_top.addWidget(lbl_db_title)
        db_top.addStretch()
        db_top.addWidget(self.lbl_db_path)
        db_layout.addLayout(db_top)

        self.lbl_db_stats = QLabel("")
        self.lbl_db_stats.setStyleSheet("font-weight: 700; font-size: 13px;")
        self.lbl_db_stats.setWordWrap(True)
        db_layout.addWidget(self.lbl_db_stats)

        db_btn_row = QHBoxLayout()
        btn_backup = QPushButton("💾 Export SQLite Database Backup (.db)")
        btn_backup.clicked.connect(self._backup_database)
        btn_reseed = QPushButton("🔄 Reset & Restore BUBT Sample Database")
        btn_reseed.setProperty("class", "DangerBtn")
        btn_reseed.clicked.connect(self._reset_sample_db)
        db_btn_row.addWidget(btn_backup)
        db_btn_row.addWidget(btn_reseed)
        db_btn_row.addStretch()
        db_layout.addLayout(db_btn_row)
        layout.addWidget(db_card)

        # --- BOTTOM CARD: About ClassMate (Proposal Section 1 & 4.6) ---
        about_card = QFrame()
        about_card.setProperty("class", "HeroCard")
        ab_layout = QVBoxLayout(about_card)
        ab_layout.setContentsMargins(22, 18, 22, 18)
        ab_layout.setSpacing(12)

        ab_header_row = QHBoxLayout()
        ab_header_row.setSpacing(14)

        cm_logo_lbl = QLabel()
        cm_logo_lbl.setPixmap(get_app_logo_pixmap(60, 60))
        cm_logo_lbl.setFixedSize(60, 60)
        cm_logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ab_title_col = QVBoxLayout()
        ab_title_col.setSpacing(3)
        lbl_ab_title = QLabel("ClassMate – Academic & Learning Assistant (v1.0.0)")
        lbl_ab_title.setProperty("class", "PageTitle")
        lbl_ab_sub = QLabel("Bangladesh University of Business and Technology (BUBT) • Department of CSE")
        lbl_ab_sub.setStyleSheet("font-size: 13px; font-weight: 400; color: #818CF8;")
        ab_title_col.addWidget(lbl_ab_title)
        ab_title_col.addWidget(lbl_ab_sub)

        ab_header_row.addWidget(cm_logo_lbl)
        ab_header_row.addLayout(ab_title_col, 1)
        ab_layout.addLayout(ab_header_row)

        lbl_ab_desc = QLabel(
            "Course: Database Management System (DBMS)  •  Target Platform: Windows 10/11 Desktop Application  •  "
            "Architecture: Python PyQt6 + Normalized SQLite3 Local RDBMS + Google Classroom & YouTube Data APIs"
        )
        lbl_ab_desc.setProperty("class", "MutedText")
        lbl_ab_desc.setWordWrap(True)
        ab_layout.addWidget(lbl_ab_desc)

        credits_grid = QGridLayout()
        credits_grid.setHorizontalSpacing(30)
        credits_grid.setVerticalSpacing(6)

        sub_by_hdr = QLabel("👨‍💻 Submitted By:")
        sub_by_hdr.setStyleSheet("font-weight: 600; color: #818CF8;")
        sub_by_body = QLabel(
            "• Md. Monirul Hasan (Student ID: 20255103087)\n"
            "• Yusuf Ali (Student ID: 20255103138)\n"
            "Department of Computer Science and Engineering (CSE), BUBT"
        )
        sub_by_body.setStyleSheet("font-weight: 400;")

        sub_to_hdr = QLabel("👩‍🏫 Submitted To:")
        sub_to_hdr.setStyleSheet("font-weight: 600; color: #10B981;")
        sub_to_body = QLabel(
            "Farah Akter Munmun [FAM]\n"
            "Assistant Professor, Department of Computer Science and Engineering (CSE)\n"
            "Bangladesh University of Business and Technology (BUBT)  •  farha.akhter@bubt.edu.bd"
        )
        sub_to_body.setStyleSheet("font-weight: 400;")

        credits_grid.addWidget(sub_by_hdr, 0, 0)
        credits_grid.addWidget(sub_to_hdr, 0, 1)
        credits_grid.addWidget(sub_by_body, 1, 0)
        credits_grid.addWidget(sub_to_body, 1, 1)
        ab_layout.addLayout(credits_grid)

        layout.addWidget(about_card)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    def refresh_data(self) -> None:
        user = self.db.get_user()
        self.name_edit.setText(user.get("full_name", "Md. Monirul Hasan"))
        self.id_edit.setText(user.get("student_id", "20255103087"))
        self.dept_edit.setText(user.get("department", "Department of CSE"))
        self.sem_edit.setText(user.get("semester", "Fall 2026"))
        self.theme_combo.setCurrentText(user.get("theme_preference", "Dark"))
        self.clock_combo.setCurrentText(user.get("clock_format", "12h"))
        self.week_combo.setCurrentText(user.get("week_start_day", "Saturday"))

        s = self.db.get_notification_settings()
        c_idx = self.class_offset_combo.findData(int(s.get("class_reminder_offset", 30)))
        if c_idx >= 0:
            self.class_offset_combo.setCurrentIndex(c_idx)

        e_idx = self.exam_offset_combo.findData(int(s.get("exam_reminder_offset", 720)))
        if e_idx >= 0:
            self.exam_offset_combo.setCurrentIndex(e_idx)

        self.summary_time_edit.setText(s.get("daily_summary_time", "21:00"))
        self.yt_key_edit.setText(s.get("youtube_api_key", ""))
        self.chk_pause_class.setChecked(bool(s.get("pause_class_alerts", 0)))
        self.chk_pause_exam.setChecked(bool(s.get("pause_exam_alerts", 0)))
        self.chk_pause_routine.setChecked(bool(s.get("pause_routine_alerts", 0)))

        # Database statistics
        stats = self.db.get_db_statistics()
        self.lbl_db_path.setText(f"DB File: {self.db.db_path}")
        stats_str = "  |  ".join(f"{k}: {v} rows" for k, v in stats.items())
        self.lbl_db_stats.setText(f"Normalized Relational Tables →  {stats_str}")

    def _quick_profile(self, full_name: str, student_id: str) -> None:
        self.name_edit.setText(full_name)
        self.id_edit.setText(student_id)
        self._save_all_settings()

    def _save_all_settings(self) -> None:
        name = self.name_edit.text().strip() or "Md. Monirul Hasan"
        sid = self.id_edit.text().strip() or "20255103087"

        self.db.update_user(
            full_name=name,
            student_id=sid,
            department=self.dept_edit.text().strip() or "Department of CSE",
            semester=self.sem_edit.text().strip() or "Fall 2026",
            theme_preference=self.theme_combo.currentText(),
            clock_format=self.clock_combo.currentText(),
            week_start_day=self.week_combo.currentText(),
            onboarded=1,
        )

        self.db.update_notification_settings(
            class_reminder_offset=int(self.class_offset_combo.currentData() or 30),
            exam_reminder_offset=int(self.exam_offset_combo.currentData() or 720),
            daily_summary_time=self.summary_time_edit.text().strip() or "21:00",
            pause_class_alerts=1 if self.chk_pause_class.isChecked() else 0,
            pause_exam_alerts=1 if self.chk_pause_exam.isChecked() else 0,
            pause_routine_alerts=1 if self.chk_pause_routine.isChecked() else 0,
            youtube_api_key=self.yt_key_edit.text().strip(),
            google_classroom_connected=1,
        )

        self.refresh_data()
        if self.on_settings_applied:
            self.on_settings_applied()
        QMessageBox.information(
            self,
            "Settings Saved",
            "Profile, UI Theme, Calendar Start Day, Clock Format, and Notification rules have been updated!",
        )

    def _backup_database(self) -> None:
        dest, _ = QFileDialog.getSaveFileName(
            self,
            "Backup ClassMate SQLite Database",
            "classmate_backup.db",
            "SQLite3 Database (*.db)",
        )
        if dest:
            shutil.copy2(self.db.db_path, dest)
            QMessageBox.information(self, "Backup Complete", f"Database backed up to:\n{dest}")

    def _reset_sample_db(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset Database to BUBT Sample Data",
            "This will restore the default BUBT CSE courses, Farah Akter Munmun [FAM] faculty info, class routine, and exam data. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.seed_bubt_sample_data()
            self.refresh_data()
            if self.on_settings_applied:
                self.on_settings_applied()
            QMessageBox.information(self, "Database Restored", "BUBT sample data has been freshly loaded!")

