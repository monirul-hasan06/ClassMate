from datetime import datetime, timedelta
from typing import Dict, List, Set
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QSystemTrayIcon

from database.db_manager import DatabaseManager


class NotificationService(QObject):
    """
    Background Smart Notification & Alert Engine for ClassMate.
    Periodically checks SQLite schedules and exams against user-configured offsets
    and granular pause controls (classes, exams, nightly routine summary).
    """

    alert_triggered = pyqtSignal(str, str, str)  # title, message, category

    def __init__(self, db: DatabaseManager, tray_icon: QSystemTrayIcon = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.tray_icon = tray_icon
        self.dispatched_keys: Set[str] = set()

        self.timer = QTimer(self)
        self.timer.setInterval(30 * 1000)  # Check every 30 seconds
        self.timer.timeout.connect(self.check_alerts)
        self.timer.start()

    def set_tray_icon(self, tray_icon: QSystemTrayIcon) -> None:
        self.tray_icon = tray_icon

    def send_notification(self, title: str, message: str, category: str = "info") -> None:
        """Send OS system tray notification and emit in-app alert signal."""
        if self.tray_icon and self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                6000,
            )
        self.alert_triggered.emit(title, message, category)

    def check_alerts(self) -> None:
        """Evaluate class reminders, exam reminders, and nightly routine summary."""
        settings = self.db.get_notification_settings()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A")
        current_hm = now.strftime("%H:%M")

        # 1. Check Class Reminders (if not paused)
        if not settings.get("pause_class_alerts", 0):
            offset_mins = int(settings.get("class_reminder_offset", 30))
            schedules = self.db.get_schedules(day_of_week=current_day, include_archived=False)
            for s in schedules:
                try:
                    class_dt = datetime.strptime(f"{today_str} {s['start_time']}", "%Y-%m-%d %H:%M")
                    diff_minutes = (class_dt - now).total_seconds() / 60.0
                    key = f"class_{today_str}_{s['schedule_id']}_{offset_mins}"
                    if 0 < diff_minutes <= offset_mins and key not in self.dispatched_keys:
                        self.dispatched_keys.add(key)
                        mins_int = max(1, int(round(diff_minutes)))
                        title = f"Upcoming Class in {mins_int} mins: {s['course_code']}"
                        msg = (
                            f"{s['course_name']}\n"
                            f"Time: {self.db.format_time(s['start_time'])} - {self.db.format_time(s['end_time'])}\n"
                            f"Venue: {s['building_number']}, Room {s['room_number']} • {s['faculty_name']} [{s['faculty_short_name']}]"
                        )
                        self.send_notification(title, msg, "class")
                except ValueError:
                    continue

        # 2. Check Exam Reminders (if not paused)
        if not settings.get("pause_exam_alerts", 0):
            exam_offset_mins = int(settings.get("exam_reminder_offset", 720))
            exams = self.db.get_exams(archived=False)
            for ex in exams:
                try:
                    exam_dt = datetime.strptime(f"{ex['exam_date']} {ex['exam_time']}", "%Y-%m-%d %H:%M")
                    diff_minutes = (exam_dt - now).total_seconds() / 60.0
                    key = f"exam_{ex['exam_id']}_{exam_offset_mins}"
                    if 0 < diff_minutes <= exam_offset_mins and key not in self.dispatched_keys:
                        self.dispatched_keys.add(key)
                        hrs = int(diff_minutes // 60)
                        mins = int(diff_minutes % 60)
                        time_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"
                        title = f"Exam Alert ({ex['exam_type']}): {ex['course_code']}"
                        msg = (
                            f"{ex['course_name']} ({ex['exam_type']}) in {time_str}\n"
                            f"Date: {ex['exam_date']} at {self.db.format_time(ex['exam_time'])} | {ex['room_number']}"
                        )
                        self.send_notification(title, msg, "exam")
                except ValueError:
                    continue

        # 3. Check Nightly Daily Schedule Summary (if not paused)
        if not settings.get("pause_routine_alerts", 0):
            summary_time = settings.get("daily_summary_time", "21:00")
            key = f"summary_{today_str}_{summary_time}"
            if current_hm == summary_time and key not in self.dispatched_keys:
                self.dispatched_keys.add(key)
                tomorrow_day = (now + timedelta(days=1)).strftime("%A")
                tomorrow_classes = self.db.get_schedules(day_of_week=tomorrow_day, include_archived=False)
                if tomorrow_classes:
                    first_cls = tomorrow_classes[0]
                    title = f"Tomorrow's Routine Summary ({tomorrow_day})"
                    msg = (
                        f"You have {len(tomorrow_classes)} class(es) scheduled for {tomorrow_day}.\n"
                        f"First Class: {first_cls['course_code']} at {self.db.format_time(first_cls['start_time'])} "
                        f"({first_cls['building_number']}, Room {first_cls['room_number']})."
                    )
                else:
                    title = f"Tomorrow's Routine Summary ({tomorrow_day})"
                    msg = f"No classes scheduled for {tomorrow_day}! Great time for self-study and exam prep."
                self.send_notification(title, msg, "summary")

    def trigger_demo_notification(self, alert_type: str = "class") -> None:
        """Trigger an immediate demonstration notification for presentation/testing."""
        if alert_type == "class":
            next_cls = self.db.get_next_class()
            if next_cls:
                title = f"Class Reminder: {next_cls['course_code']}"
                msg = (
                    f"{next_cls['course_name']}\n"
                    f"Schedule: {next_cls['formatted_range']} | {next_cls['venue']}\n"
                    f"Instructor: {next_cls['instructor_display']}"
                )
            else:
                title = "Class Reminder: CSE 208"
                msg = "Database Management System Lab\n8:15 AM - 11:15 AM | Building 2, Room 417\nInstructor: Farah Akter Munmun [FAM]"
            self.send_notification(title, msg, "class")
        elif alert_type == "exam":
            exams = self.db.get_exams(archived=False)
            if exams:
                ex = exams[0]
                title = f"Upcoming Exam Alert: {ex['course_code']} ({ex['exam_type']})"
                msg = (
                    f"Date: {ex['exam_date']} at {self.db.format_time(ex['exam_time'])}\n"
                    f"Venue: {ex['room_number']} | Syllabus: {ex['syllabus'][:70]}..."
                )
            else:
                title = "Upcoming Exam Alert: CSE 207 (CT-2)"
                msg = "SQL Joins, Subqueries, Views & Indexing | Building 2, Room 402"
            self.send_notification(title, msg, "exam")
        else:
            tomorrow_day = (datetime.now() + timedelta(days=1)).strftime("%A")
            tomorrow_classes = self.db.get_schedules(day_of_week=tomorrow_day, include_archived=False)
            title = f"Nightly Schedule Summary ({tomorrow_day})"
            msg = f"You have {len(tomorrow_classes)} class(es) scheduled for {tomorrow_day}. Stay prepared!"
            self.send_notification(title, msg, "summary")

