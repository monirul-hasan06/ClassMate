from datetime import datetime
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
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
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager


class CourseDialog(QDialog):
    """Dialog to Add or Edit a Course in the `courses` table."""

    def __init__(self, db: DatabaseManager, course_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.course_data = course_data
        self.setWindowTitle("Edit Course" if course_data else "Add New Course")
        self.setMinimumWidth(440)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.code_edit = QLineEdit(self.course_data.get("course_code", "") if self.course_data else "")
        self.code_edit.setPlaceholderText("e.g., CSE 208")

        self.name_edit = QLineEdit(self.course_data.get("course_name", "") if self.course_data else "")
        self.name_edit.setPlaceholderText("e.g., Database Management System Lab")

        self.sec_edit = QLineEdit(self.course_data.get("section", "01") if self.course_data else "01")
        self.bldg_edit = QLineEdit(self.course_data.get("building_number", "Building 2") if self.course_data else "Building 2")
        self.room_edit = QLineEdit(self.course_data.get("room_number", "417") if self.course_data else "417")

        self.faculty_combo = QComboBox()
        self.faculty_combo.addItem("TBA / Unassigned", None)
        for f in self.db.get_all_faculty():
            self.faculty_combo.addItem(f"{f['name']} [{f['short_name']}]", f["faculty_id"])

        if self.course_data and self.course_data.get("faculty_id"):
            idx = self.faculty_combo.findData(self.course_data["faculty_id"])
            if idx >= 0:
                self.faculty_combo.setCurrentIndex(idx)

        form.addRow("Course Code:", self.code_edit)
        form.addRow("Course Name:", self.name_edit)
        form.addRow("Section:", self.sec_edit)
        form.addRow("Building:", self.bldg_edit)
        form.addRow("Room Number:", self.room_edit)
        form.addRow("Instructor:", self.faculty_combo)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Course")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        code = self.code_edit.text().strip()
        name = self.name_edit.text().strip()
        if not code or not name:
            QMessageBox.warning(self, "Validation Error", "Course Code and Course Name are required.")
            return
        user = self.db.get_user()
        if self.course_data:
            self.db.update_course(
                course_id=self.course_data["course_id"],
                course_code=code,
                course_name=name,
                section=self.sec_edit.text().strip() or "01",
                building_number=self.bldg_edit.text().strip() or "Building 2",
                room_number=self.room_edit.text().strip() or "401",
                faculty_id=self.faculty_combo.currentData(),
            )
        else:
            self.db.add_course(
                course_code=code,
                course_name=name,
                section=self.sec_edit.text().strip() or "01",
                building_number=self.bldg_edit.text().strip() or "Building 2",
                room_number=self.room_edit.text().strip() or "401",
                faculty_id=self.faculty_combo.currentData(),
                semester=user.get("semester", "Fall 2026"),
            )
        self.accept()


class ScheduleSlotDialog(QDialog):
    """Dialog to Add or Edit a Class Schedule Slot in the `schedules` table."""

    def __init__(
        self,
        db: DatabaseManager,
        schedule_data: Optional[Dict[str, Any]] = None,
        default_day: str = "Saturday",
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.schedule_data = schedule_data
        self.default_day = default_day
        self.setWindowTitle("Edit Class Slot" if schedule_data else "Add Class Schedule Slot")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.course_combo = QComboBox()
        for c in self.db.get_courses(include_archived=False):
            self.course_combo.addItem(f"{c['course_code']} – {c['course_name']} (Sec {c['section']})", c["course_id"])

        self.day_combo = QComboBox()
        self.day_combo.addItems(self.db.DAYS_ALL)
        self.day_combo.setCurrentText(
            self.schedule_data.get("day_of_week", self.default_day) if self.schedule_data else self.default_day
        )

        self.start_edit = QLineEdit(self.schedule_data.get("start_time", "08:15") if self.schedule_data else "08:15")
        self.start_edit.setPlaceholderText("HH:MM in 24h format (e.g. 08:15 or 13:30)")

        self.end_edit = QLineEdit(self.schedule_data.get("end_time", "11:15") if self.schedule_data else "11:15")
        self.end_edit.setPlaceholderText("HH:MM in 24h format (e.g. 11:15 or 15:00)")

        if self.schedule_data:
            idx = self.course_combo.findData(self.schedule_data["course_id"])
            if idx >= 0:
                self.course_combo.setCurrentIndex(idx)

        form.addRow("Course:", self.course_combo)
        form.addRow("Day of Week:", self.day_combo)
        form.addRow("Start Time (24h HH:MM):", self.start_edit)
        form.addRow("End Time (24h HH:MM):", self.end_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Class Slot")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        cid = self.course_combo.currentData()
        if cid is None:
            QMessageBox.warning(self, "No Course", "Please add a course first before creating a schedule slot.")
            return
        st = self.start_edit.text().strip()
        et = self.end_edit.text().strip()
        try:
            datetime.strptime(st, "%H:%M")
            datetime.strptime(et, "%H:%M")
        except ValueError:
            QMessageBox.warning(self, "Invalid Time", "Please enter times in HH:MM format (e.g., 08:15, 14:00).")
            return

        if self.schedule_data:
            self.db.update_schedule(
                schedule_id=self.schedule_data["schedule_id"],
                course_id=cid,
                day_of_week=self.day_combo.currentText(),
                start_time=st,
                end_time=et,
            )
        else:
            self.db.add_schedule(
                course_id=cid,
                day_of_week=self.day_combo.currentText(),
                start_time=st,
                end_time=et,
            )
        self.accept()


class SemesterTransitionDialog(QDialog):
    """Dialog to transition to a new semester (clearing or archiving old routines)."""

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Semester Management – Transition to New Semester")
        self.setMinimumWidth(450)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        info = QLabel(
            "Transitioning to a new semester lets you archive or clear your current class routines "
            "and start fresh for the upcoming academic term."
        )
        info.setWordWrap(True)
        info.setProperty("class", "MutedText")
        layout.addWidget(info)

        form = QFormLayout()
        self.sem_edit = QLineEdit("Spring 2027")
        self.archive_chk = QCheckBox("Archive current courses & exams (uncheck to permanently delete)")
        self.archive_chk.setChecked(True)
        form.addRow("New Semester Title:", self.sem_edit)
        form.addRow("", self.archive_chk)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm = QPushButton("Start New Semester")
        btn_confirm.setProperty("class", "PrimaryBtn")
        btn_confirm.clicked.connect(self._confirm)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_confirm)
        layout.addLayout(btn_row)

    def _confirm(self) -> None:
        new_sem = self.sem_edit.text().strip()
        if not new_sem:
            QMessageBox.warning(self, "Required", "Please enter the new semester name.")
            return
        self.db.transition_new_semester(new_sem, archive_old=self.archive_chk.isChecked())
        self.accept()


class RoutinePage(QWidget):
    """
    Class Routine & Weekly Scheduler Page (Proposal Section 4.2).
    Features:
      - Day-Wise Tabs (Saturday to Friday, ordered by user's week_start_day setting)
      - Full Weekly Consolidated Grid Overview
      - Course Catalog & Attendance Log Manager
      - Semester Management (New Semester transition)
      - Routine Sharing (Export & Import JSON Routine Templates)
    """

    def __init__(self, db: DatabaseManager, on_data_changed: Optional[Callable[[], None]] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.on_data_changed = on_data_changed
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Header & Toolbar
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        lbl_title = QLabel("📅 Class Routine & Weekly Scheduler")
        lbl_title.setProperty("class", "PageTitle")
        self.lbl_subtitle = QLabel("Day-wise schedule tabs, full weekly grid overview, semester management & routine sharing")
        self.lbl_subtitle.setProperty("class", "MutedText")
        title_col.addWidget(lbl_title)
        title_col.addWidget(self.lbl_subtitle)
        header_row.addLayout(title_col, 1)

        btn_add_course = QPushButton("＋ Add Course")
        btn_add_course.clicked.connect(self._open_add_course)

        btn_add_slot = QPushButton("＋ Add Class Slot")
        btn_add_slot.setProperty("class", "PrimaryBtn")
        btn_add_slot.clicked.connect(self._open_add_slot)

        btn_export = QPushButton("📤 Share / Export Routine")
        btn_export.clicked.connect(self._export_routine)

        btn_import = QPushButton("📥 Import Routine")
        btn_import.clicked.connect(self._import_routine)

        btn_semester = QPushButton("🎓 New Semester")
        btn_semester.clicked.connect(self._open_semester_transition)

        header_row.addWidget(btn_add_course)
        header_row.addWidget(btn_add_slot)
        header_row.addWidget(btn_export)
        header_row.addWidget(btn_import)
        header_row.addWidget(btn_semester)
        layout.addLayout(header_row)

        # Main Tabs:
        #   Tab 0: Day-Wise Schedule Tabs (Saturday..Friday)
        #   Tab 1: Full Weekly Overview Grid
        #   Tab 2: Enrolled Courses Catalog
        #   Tab 3: Attendance Log History
        self.mode_tabs = QTabWidget()

        # --- Sub-view 1: Day-Wise Tabs ---
        self.day_tabs_container = QWidget()
        dt_layout = QVBoxLayout(self.day_tabs_container)
        dt_layout.setContentsMargins(12, 12, 12, 12)
        self.day_sub_tabs = QTabWidget()
        dt_layout.addWidget(self.day_sub_tabs)
        self.mode_tabs.addTab(self.day_tabs_container, "🗂️ Day-Wise Tabs (Sat - Fri)")

        # --- Sub-view 2: Full Weekly Overview Grid ---
        self.weekly_grid_container = QWidget()
        wg_layout = QVBoxLayout(self.weekly_grid_container)
        wg_layout.setContentsMargins(12, 12, 12, 12)
        self.weekly_table = QTableWidget()
        self.weekly_table.setAlternatingRowColors(True)
        self.weekly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        wg_layout.addWidget(self.weekly_table)
        self.mode_tabs.addTab(self.weekly_grid_container, "🌐 Full Weekly Overview Grid")

        # --- Sub-view 3: Enrolled Courses Catalog ---
        self.courses_container = QWidget()
        cc_layout = QVBoxLayout(self.courses_container)
        cc_layout.setContentsMargins(12, 12, 12, 12)
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(7)
        self.courses_table.setHorizontalHeaderLabels([
            "Course Code", "Course Name", "Section", "Building", "Room", "Instructor", "Actions"
        ])
        self.courses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.courses_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.courses_table.setAlternatingRowColors(True)
        self.courses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cc_layout.addWidget(self.courses_table)
        self.mode_tabs.addTab(self.courses_container, "📚 Enrolled Courses")

        # --- Sub-view 4: Attendance Log History ---
        self.att_container = QWidget()
        ac_layout = QVBoxLayout(self.att_container)
        ac_layout.setContentsMargins(12, 12, 12, 12)
        self.att_table = QTableWidget()
        self.att_table.setColumnCount(6)
        self.att_table.setHorizontalHeaderLabels([
            "Date", "Course", "Day & Slot", "Status", "Remarks", "Action"
        ])
        self.att_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.att_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.att_table.setAlternatingRowColors(True)
        self.att_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        ac_layout.addWidget(self.att_table)
        self.mode_tabs.addTab(self.att_container, "✅ Attendance Logs")

        layout.addWidget(self.mode_tabs, 1)

    def refresh_data(self) -> None:
        user = self.db.get_user()
        ordered_days = self.db.get_ordered_days()
        self.lbl_subtitle.setText(
            f"Semester: {user.get('semester', 'Fall 2026')}  •  Week Start Day: {ordered_days[0]}  •  Time Format: {user.get('clock_format', '12h')}"
        )

        self._populate_day_wise_tabs(ordered_days)
        self._populate_weekly_overview_grid(ordered_days)
        self._populate_courses_table()
        self._populate_attendance_table()

    def _populate_day_wise_tabs(self, ordered_days: list) -> None:
        current_day_text = None
        if self.day_sub_tabs.count() > 0:
            current_day_text = self.day_sub_tabs.tabText(self.day_sub_tabs.currentIndex()).split(" ")[0]
        else:
            current_day_text = datetime.now().strftime("%A")

        self.day_sub_tabs.clear()

        for day_name in ordered_days:
            day_schedules = self.db.get_schedules(day_of_week=day_name, include_archived=False)
            page = QWidget()
            p_layout = QVBoxLayout(page)
            p_layout.setContentsMargins(10, 10, 10, 10)

            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "Time & Duration", "Course Code", "Course Name", "Venue (Building & Room)", "Instructor", "Quick Actions"
            ])
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setRowCount(len(day_schedules))

            for row_idx, s in enumerate(day_schedules):
                time_str = f"{self.db.format_time(s['start_time'])} - {self.db.format_time(s['end_time'])}"
                venue_str = f"{s['building_number']}, Room {s['room_number']} (Sec {s['section']})"
                inst_str = f"{s['faculty_name']} [{s['faculty_short_name']}]"

                table.setItem(row_idx, 0, QTableWidgetItem(time_str))
                table.setItem(row_idx, 1, QTableWidgetItem(s["course_code"]))
                table.setItem(row_idx, 2, QTableWidgetItem(s["course_name"]))
                table.setItem(row_idx, 3, QTableWidgetItem(venue_str))
                table.setItem(row_idx, 4, QTableWidgetItem(inst_str))

                # Action buttons cell
                action_w = QWidget()
                al = QHBoxLayout(action_w)
                al.setContentsMargins(4, 2, 4, 2)
                al.setSpacing(6)

                btn_att = QPushButton("✓ Attended")
                btn_att.setProperty("class", "SuccessBtn")
                btn_att.clicked.connect(lambda _, sid=s["schedule_id"], cc=s["course_code"]: self._log_slot_att(sid, cc, "Attended"))

                btn_miss = QPushButton("✗ Missed")
                btn_miss.setProperty("class", "DangerBtn")
                btn_miss.clicked.connect(lambda _, sid=s["schedule_id"], cc=s["course_code"]: self._log_slot_att(sid, cc, "Missed"))

                btn_edit = QPushButton("Edit")
                btn_edit.clicked.connect(lambda _, item=s: self._edit_slot(item))

                btn_del = QPushButton("Delete")
                btn_del.clicked.connect(lambda _, sid=s["schedule_id"]: self._delete_slot(sid))

                al.addWidget(btn_att)
                al.addWidget(btn_miss)
                al.addWidget(btn_edit)
                al.addWidget(btn_del)
                table.setCellWidget(row_idx, 5, action_w)
                table.setRowHeight(row_idx, 44)

            p_layout.addWidget(table)
            tab_title = f"{day_name} ({len(day_schedules)})"
            self.day_sub_tabs.addTab(page, tab_title)

        # Restore selected day tab
        for i in range(self.day_sub_tabs.count()):
            if self.day_sub_tabs.tabText(i).startswith(current_day_text or ""):
                self.day_sub_tabs.setCurrentIndex(i)
                break

    def _populate_weekly_overview_grid(self, ordered_days: list) -> None:
        self.weekly_table.clear()
        self.weekly_table.setRowCount(len(ordered_days))
        self.weekly_table.setColumnCount(4)
        self.weekly_table.setHorizontalHeaderLabels([
            "Day of Week", "Slot 1 (Morning)", "Slot 2 (Midday)", "Slot 3 (Afternoon)"
        ])
        for col in range(1, 4):
            self.weekly_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        for r_idx, day_name in enumerate(ordered_days):
            day_item = QTableWidgetItem(day_name)
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weekly_table.setItem(r_idx, 0, day_item)

            day_classes = self.db.get_schedules(day_of_week=day_name, include_archived=False)
            for c_idx in range(3):
                if c_idx < len(day_classes):
                    s = day_classes[c_idx]
                    cell_text = (
                        f"{s['course_code']}: {s['course_name']}\n"
                        f"🕒 {self.db.format_time(s['start_time'])} - {self.db.format_time(s['end_time'])}\n"
                        f"📍 {s['building_number']}, Rm {s['room_number']} • [{s['faculty_short_name']}]"
                    )
                    item = QTableWidgetItem(cell_text)
                else:
                    item = QTableWidgetItem("— Free Slot —")
                    item.setForeground(Qt.GlobalColor.gray)
                self.weekly_table.setItem(r_idx, c_idx + 1, item)
            self.weekly_table.setRowHeight(r_idx, 72)

    def _populate_courses_table(self) -> None:
        courses = self.db.get_courses(include_archived=False)
        self.courses_table.setRowCount(len(courses))
        for r_idx, c in enumerate(courses):
            self.courses_table.setItem(r_idx, 0, QTableWidgetItem(c["course_code"]))
            self.courses_table.setItem(r_idx, 1, QTableWidgetItem(c["course_name"]))
            self.courses_table.setItem(r_idx, 2, QTableWidgetItem(c["section"]))
            self.courses_table.setItem(r_idx, 3, QTableWidgetItem(c["building_number"]))
            self.courses_table.setItem(r_idx, 4, QTableWidgetItem(c["room_number"]))
            inst = f"{c.get('faculty_name') or 'TBA'} [{c.get('faculty_short_name') or 'TBA'}]"
            self.courses_table.setItem(r_idx, 5, QTableWidgetItem(inst))

            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(6)
            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda _, item=c: self._edit_course(item))
            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.clicked.connect(lambda _, cid=c["course_id"]: self._delete_course(cid))
            al.addWidget(btn_edit)
            al.addWidget(btn_del)
            self.courses_table.setCellWidget(r_idx, 6, act_w)
            self.courses_table.setRowHeight(r_idx, 42)

    def _populate_attendance_table(self) -> None:
        logs = self.db.get_recent_attendance_logs(limit=40)
        self.att_table.setRowCount(len(logs))
        for r_idx, lg in enumerate(logs):
            self.att_table.setItem(r_idx, 0, QTableWidgetItem(lg["date"]))
            self.att_table.setItem(r_idx, 1, QTableWidgetItem(f"{lg['course_code']} – {lg['course_name']}"))
            slot_str = f"{lg['day_of_week']} ({self.db.format_time(lg['start_time'])})"
            self.att_table.setItem(r_idx, 2, QTableWidgetItem(slot_str))
            status_item = QTableWidgetItem(lg["status"])
            self.att_table.setItem(r_idx, 3, status_item)
            self.att_table.setItem(r_idx, 4, QTableWidgetItem(lg.get("remarks", "")))

            btn_del = QPushButton("Remove")
            btn_del.clicked.connect(lambda _, lid=lg["log_id"]: self._delete_att_log(lid))
            self.att_table.setCellWidget(r_idx, 5, btn_del)
            self.att_table.setRowHeight(r_idx, 38)

    def _notify_change(self) -> None:
        self.refresh_data()
        if self.on_data_changed:
            self.on_data_changed()

    def _open_add_course(self) -> None:
        dlg = CourseDialog(self.db, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify_change()

    def _edit_course(self, course_data: Dict[str, Any]) -> None:
        dlg = CourseDialog(self.db, course_data=course_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify_change()

    def _delete_course(self, course_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Course",
            "Deleting this course will also remove its scheduled slots and exam logs. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_course(course_id)
            self._notify_change()

    def _open_add_slot(self) -> None:
        current_tab_text = self.day_sub_tabs.tabText(self.day_sub_tabs.currentIndex()).split(" ")[0]
        dlg = ScheduleSlotDialog(self.db, default_day=current_tab_text or "Saturday", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify_change()

    def _edit_slot(self, schedule_data: Dict[str, Any]) -> None:
        dlg = ScheduleSlotDialog(self.db, schedule_data=schedule_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify_change()

    def _delete_slot(self, schedule_id: int) -> None:
        self.db.delete_schedule(schedule_id)
        self._notify_change()

    def _log_slot_att(self, schedule_id: int, course_code: str, status: str) -> None:
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.db.log_attendance(schedule_id, status, today_str, f"Marked {status} from Routine tab")
        self._notify_change()
        QMessageBox.information(self, "Attendance Updated", f"{course_code} marked as {status} for {today_str}.")

    def _delete_att_log(self, log_id: int) -> None:
        self.db.delete_attendance_log(log_id)
        self._notify_change()

    def _export_routine(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export ClassMate Routine Template",
            "ClassMate_BUBT_Routine.json",
            "JSON Routine Template (*.json)",
        )
        if path:
            self.db.export_routine_template(path)
            QMessageBox.information(
                self,
                "Routine Exported",
                f"Your class routine template has been exported to:\n{path}\n\nYou can share this file with your classmates!",
            )

    def _import_routine(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Shared ClassMate Routine Template",
            "",
            "JSON Routine Template (*.json)",
        )
        if path:
            try:
                c_added, s_added = self.db.import_routine_template(path)
                self._notify_change()
                QMessageBox.information(
                    self,
                    "Routine Imported",
                    f"Imported {c_added} new course(s) and {s_added} schedule slot(s)!",
                )
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Failed to import routine file:\n{e}")

    def _open_semester_transition(self) -> None:
        dlg = SemesterTransitionDialog(self.db, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify_change()
            QMessageBox.information(self, "New Semester Started", "Your semester transition is complete!")

