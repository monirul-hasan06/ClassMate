from datetime import datetime
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager
from services.notification_service import NotificationService


class ExamDialog(QDialog):
    """Dialog to Add or Edit an Exam / Assessment record."""

    def __init__(self, db: DatabaseManager, exam_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.exam_data = exam_data
        self.setWindowTitle("Edit Assessment / Exam" if exam_data else "Log New Exam / Assessment")
        self.setMinimumWidth(480)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.course_combo = QComboBox()
        for c in self.db.get_courses(include_archived=False):
            self.course_combo.addItem(f"{c['course_code']} – {c['course_name']}", c["course_id"])

        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems([
            "CT (Class Test 1)",
            "CT (Class Test 2)",
            "CT (Class Test 3)",
            "Midterm",
            "Final",
            "Lab Quiz",
            "Lab Final / Project Viva",
        ])

        today_str = datetime.now().strftime("%Y-%m-%d")
        self.date_edit = QLineEdit(self.exam_data.get("exam_date", today_str) if self.exam_data else today_str)
        self.date_edit.setPlaceholderText("YYYY-MM-DD")

        self.time_edit = QLineEdit(self.exam_data.get("exam_time", "10:00") if self.exam_data else "10:00")
        self.time_edit.setPlaceholderText("HH:MM (24h, e.g., 10:00)")

        self.room_edit = QLineEdit(
            self.exam_data.get("room_number", "Building 2, Room 402") if self.exam_data else "Building 2, Room 402"
        )

        self.syllabus_edit = QTextEdit()
        self.syllabus_edit.setMaximumHeight(75)
        self.syllabus_edit.setPlaceholderText("Topics covered (e.g., SQL Joins, Normalization, ER Diagrams)...")
        if self.exam_data:
            self.syllabus_edit.setPlainText(self.exam_data.get("syllabus", ""))

        self.total_marks_spin = QDoubleSpinBox()
        self.total_marks_spin.setRange(1.0, 200.0)
        self.total_marks_spin.setValue(float(self.exam_data.get("total_marks", 20.0)) if self.exam_data else 20.0)

        self.obtained_edit = QLineEdit(
            str(self.exam_data["marks_obtained"])
            if (self.exam_data and self.exam_data.get("marks_obtained") is not None)
            else ""
        )
        self.obtained_edit.setPlaceholderText("Leave blank if upcoming")

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(70)
        self.notes_edit.setPlaceholderText("Performance notes, reminders, or reflection...")
        if self.exam_data:
            self.notes_edit.setPlainText(self.exam_data.get("performance_notes", ""))

        self.archive_chk = QCheckBox("Archive to Exam History (Completed Exam)")
        if self.exam_data:
            idx = self.course_combo.findData(self.exam_data["course_id"])
            if idx >= 0:
                self.course_combo.setCurrentIndex(idx)
            self.type_combo.setCurrentText(self.exam_data.get("exam_type", "CT"))
            self.archive_chk.setChecked(bool(self.exam_data.get("is_archived", 0)))

        form.addRow("Course:", self.course_combo)
        form.addRow("Exam Type:", self.type_combo)
        form.addRow("Exam Date (YYYY-MM-DD):", self.date_edit)
        form.addRow("Exam Time (24h HH:MM):", self.time_edit)
        form.addRow("Venue / Room:", self.room_edit)
        form.addRow("Syllabus / Topics:", self.syllabus_edit)
        form.addRow("Total Marks:", self.total_marks_spin)
        form.addRow("Obtained Marks:", self.obtained_edit)
        form.addRow("Performance Notes:", self.notes_edit)
        form.addRow("", self.archive_chk)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Exam Record")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        cid = self.course_combo.currentData()
        if cid is None:
            QMessageBox.warning(self, "No Course", "Please add a course first.")
            return
        obtained_val = None
        if self.obtained_edit.text().strip():
            try:
                obtained_val = float(self.obtained_edit.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Invalid Marks", "Obtained marks must be a valid number.")
                return

        if self.exam_data:
            self.db.update_exam(
                exam_id=self.exam_data["exam_id"],
                course_id=cid,
                exam_type=self.type_combo.currentText().strip(),
                exam_date=self.date_edit.text().strip(),
                exam_time=self.time_edit.text().strip(),
                room_number=self.room_edit.text().strip(),
                syllabus=self.syllabus_edit.toPlainText().strip(),
                performance_notes=self.notes_edit.toPlainText().strip(),
                marks_obtained=obtained_val,
                total_marks=self.total_marks_spin.value(),
                is_archived=1 if self.archive_chk.isChecked() else 0,
            )
        else:
            self.db.add_exam(
                course_id=cid,
                exam_type=self.type_combo.currentText().strip(),
                exam_date=self.date_edit.text().strip(),
                exam_time=self.time_edit.text().strip(),
                room_number=self.room_edit.text().strip(),
                syllabus=self.syllabus_edit.toPlainText().strip(),
                performance_notes=self.notes_edit.toPlainText().strip(),
                marks_obtained=obtained_val,
                total_marks=self.total_marks_spin.value(),
                is_archived=1 if self.archive_chk.isChecked() else 0,
            )
        self.accept()


class ExamsPage(QWidget):
    """
    Assessment & Exam Management Page (Proposal Section 4.3).
    Features:
      - Exam Tracker for CTs, Midterms, and Final Exams
      - Exam History archiving past exam records with marks and performance notes
      - Dedicated Exam Reminder controls & test notification trigger
    """

    def __init__(
        self,
        db: DatabaseManager,
        notification_service: NotificationService,
        on_data_changed: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.notification_service = notification_service
        self.on_data_changed = on_data_changed
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Header & Reminder Banner
        top_row = QHBoxLayout()
        title_col = QVBoxLayout()
        lbl_title = QLabel("📝 Assessment & Exam Management")
        lbl_title.setProperty("class", "PageTitle")
        lbl_sub = QLabel("Track Class Tests (CTs), Midterm Exams, Final Exams, and archive past performance notes")
        lbl_sub.setProperty("class", "MutedText")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        top_row.addLayout(title_col, 1)

        self.chk_exam_alerts = QCheckBox("🔔 Enable Exam Reminders")
        self.chk_exam_alerts.stateChanged.connect(self._toggle_exam_alerts)

        btn_test_alert = QPushButton("🔔 Test Exam Alert")
        btn_test_alert.clicked.connect(lambda: self.notification_service.trigger_demo_notification("exam"))

        btn_add_exam = QPushButton("＋ Log New Exam / CT")
        btn_add_exam.setProperty("class", "PrimaryBtn")
        btn_add_exam.clicked.connect(self._open_add_exam)

        top_row.addWidget(self.chk_exam_alerts)
        top_row.addWidget(btn_test_alert)
        top_row.addWidget(btn_add_exam)
        layout.addLayout(top_row)

        # Tabs: Upcoming Exam Tracker vs Archived Exam History
        self.tabs = QTabWidget()

        # Tab 1: Active / Upcoming Exams
        upcoming_w = QWidget()
        up_layout = QVBoxLayout(upcoming_w)
        up_layout.setContentsMargins(12, 12, 12, 12)
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(7)
        self.upcoming_table.setHorizontalHeaderLabels([
            "Countdown / Date", "Exam Type", "Course", "Time & Venue", "Syllabus / Topics", "Notes", "Actions"
        ])
        self.upcoming_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.upcoming_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.upcoming_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.upcoming_table.setAlternatingRowColors(True)
        self.upcoming_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        up_layout.addWidget(self.upcoming_table)
        self.tabs.addTab(upcoming_w, "🎯 Upcoming Exam Tracker (CT / Mid / Final)")

        # Tab 2: Archived Exam History & Performance Notes
        history_w = QWidget()
        hi_layout = QVBoxLayout(history_w)
        hi_layout.setContentsMargins(12, 12, 12, 12)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Exam Type", "Course", "Score / Marks", "Syllabus Covered", "Performance Notes", "Actions"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        hi_layout.addWidget(self.history_table)
        self.tabs.addTab(history_w, "🏛️ Exam History & Performance Archive")

        layout.addWidget(self.tabs, 1)

    def refresh_data(self) -> None:
        settings = self.db.get_notification_settings()
        self.chk_exam_alerts.blockSignals(True)
        self.chk_exam_alerts.setChecked(not bool(settings.get("pause_exam_alerts", 0)))
        self.chk_exam_alerts.blockSignals(False)

        self._populate_upcoming_table()
        self._populate_history_table()

    def _populate_upcoming_table(self) -> None:
        exams = self.db.get_exams(archived=False)
        self.upcoming_table.setRowCount(len(exams))
        today = datetime.now().date()

        for r_idx, ex in enumerate(exams):
            try:
                ex_dt = datetime.strptime(ex["exam_date"], "%Y-%m-%d").date()
                diff = (ex_dt - today).days
                if diff == 0:
                    date_str = f"🔥 TODAY ({ex['exam_date']})"
                elif diff > 0:
                    date_str = f"⏳ In {diff} days ({ex['exam_date']})"
                else:
                    date_str = f"{ex['exam_date']} (Past)"
            except ValueError:
                date_str = ex["exam_date"]

            self.upcoming_table.setItem(r_idx, 0, QTableWidgetItem(date_str))
            self.upcoming_table.setItem(r_idx, 1, QTableWidgetItem(ex["exam_type"]))
            self.upcoming_table.setItem(r_idx, 2, QTableWidgetItem(f"{ex['course_code']}: {ex['course_name']}"))
            tv_str = f"{self.db.format_time(ex['exam_time'])} • {ex['room_number']}"
            self.upcoming_table.setItem(r_idx, 3, QTableWidgetItem(tv_str))
            self.upcoming_table.setItem(r_idx, 4, QTableWidgetItem(ex.get("syllabus", "")))
            self.upcoming_table.setItem(r_idx, 5, QTableWidgetItem(ex.get("performance_notes", "")))

            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(6)

            btn_edit = QPushButton("Edit / Archive")
            btn_edit.clicked.connect(lambda _, item=ex: self._edit_exam(item))

            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.clicked.connect(lambda _, eid=ex["exam_id"]: self._delete_exam(eid))

            al.addWidget(btn_edit)
            al.addWidget(btn_del)
            self.upcoming_table.setCellWidget(r_idx, 6, act_w)
            self.upcoming_table.setRowHeight(r_idx, 46)

    def _populate_history_table(self) -> None:
        exams = self.db.get_exams(archived=True)
        self.history_table.setRowCount(len(exams))

        for r_idx, ex in enumerate(exams):
            self.history_table.setItem(r_idx, 0, QTableWidgetItem(ex["exam_date"]))
            self.history_table.setItem(r_idx, 1, QTableWidgetItem(ex["exam_type"]))
            self.history_table.setItem(r_idx, 2, QTableWidgetItem(f"{ex['course_code']}: {ex['course_name']}"))

            if ex.get("marks_obtained") is not None:
                score_str = f"{ex['marks_obtained']} / {ex.get('total_marks', 20.0)}"
            else:
                score_str = f"N/A / {ex.get('total_marks', 20.0)}"
            self.history_table.setItem(r_idx, 3, QTableWidgetItem(score_str))
            self.history_table.setItem(r_idx, 4, QTableWidgetItem(ex.get("syllabus", "")))
            self.history_table.setItem(r_idx, 5, QTableWidgetItem(ex.get("performance_notes", "")))

            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(6)

            btn_edit = QPushButton("Update Notes")
            btn_edit.clicked.connect(lambda _, item=ex: self._edit_exam(item))
            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.clicked.connect(lambda _, eid=ex["exam_id"]: self._delete_exam(eid))
            al.addWidget(btn_edit)
            al.addWidget(btn_del)
            self.history_table.setCellWidget(r_idx, 6, act_w)
            self.history_table.setRowHeight(r_idx, 44)

    def _toggle_exam_alerts(self) -> None:
        s = self.db.get_notification_settings()
        pause_val = 0 if self.chk_exam_alerts.isChecked() else 1
        self.db.update_notification_settings(
            class_reminder_offset=int(s.get("class_reminder_offset", 30)),
            exam_reminder_offset=int(s.get("exam_reminder_offset", 720)),
            daily_summary_time=s.get("daily_summary_time", "21:00"),
            pause_class_alerts=int(s.get("pause_class_alerts", 0)),
            pause_exam_alerts=pause_val,
            pause_routine_alerts=int(s.get("pause_routine_alerts", 0)),
            youtube_api_key=s.get("youtube_api_key", ""),
            google_classroom_connected=int(s.get("google_classroom_connected", 1)),
        )
        if self.on_data_changed:
            self.on_data_changed()

    def _open_add_exam(self) -> None:
        dlg = ExamDialog(self.db, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()

    def _edit_exam(self, exam_data: Dict[str, Any]) -> None:
        dlg = ExamDialog(self.db, exam_data=exam_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()

    def _delete_exam(self, exam_id: int) -> None:
        self.db.delete_exam(exam_id)
        self.refresh_data()
        if self.on_data_changed:
            self.on_data_changed()

