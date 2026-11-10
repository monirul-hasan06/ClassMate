from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database.db_manager import DatabaseManager


class OnboardingDialog(QDialog):
    """
    User Onboarding & Personalization Dialog (Proposal Section 4.1).
    Allows setting Student Name, ID, Department, Semester, Theme Preference,
    Clock Format (12h/24h), and Week Start Day (Saturday/Sunday/Monday).
    """

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Welcome to ClassMate – Academic & Learning Assistant")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        user = self.db.get_user()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Card
        hero = QFrame()
        hero.setProperty("class", "HeroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(18, 16, 18, 16)

        title = QLabel("🎓 Welcome to ClassMate")
        title.setStyleSheet("font-size: 20px; font-weight: 800;")
        subtitle = QLabel(
            "Personalize your academic planner, routine preferences, and BUBT student profile."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("class", "MutedText")

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        layout.addWidget(hero)

        # Quick Team Presets (Md. Monirul Hasan & Yusuf Ali)
        preset_row = QHBoxLayout()
        preset_lbl = QLabel("Quick Team Profile:")
        preset_lbl.setProperty("class", "MutedText")
        btn_monirul = QPushButton("👤 Md. Monirul Hasan (20255103087)")
        btn_yusuf = QPushButton("👤 Yusuf Ali (20255103138)")
        btn_monirul.clicked.connect(lambda: self._fill_preset("Md. Monirul Hasan", "20255103087"))
        btn_yusuf.clicked.connect(lambda: self._fill_preset("Yusuf Ali", "20255103138"))
        preset_row.addWidget(preset_lbl)
        preset_row.addWidget(btn_monirul)
        preset_row.addWidget(btn_yusuf)
        layout.addLayout(preset_row)

        # Form Card
        card = QFrame()
        card.setProperty("class", "Card")
        form = QFormLayout(card)
        form.setContentsMargins(18, 18, 18, 18)
        form.setSpacing(12)

        self.name_input = QLineEdit(user.get("full_name", "Md. Monirul Hasan"))
        self.name_input.setPlaceholderText("Enter your full name")

        self.id_input = QLineEdit(user.get("student_id", "20255103087"))
        self.id_input.setPlaceholderText("e.g., 20255103087")

        self.dept_input = QLineEdit(user.get("department", "Department of CSE"))
        self.sem_input = QLineEdit(user.get("semester", "Fall 2026"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        self.theme_combo.setCurrentText(user.get("theme_preference", "Dark"))

        self.clock_combo = QComboBox()
        self.clock_combo.addItems(["12h", "24h"])
        self.clock_combo.setCurrentText(user.get("clock_format", "12h"))

        self.week_combo = QComboBox()
        self.week_combo.addItems(["Saturday", "Sunday", "Monday"])
        self.week_combo.setCurrentText(user.get("week_start_day", "Saturday"))

        form.addRow("Full Name:", self.name_input)
        form.addRow("Student ID:", self.id_input)
        form.addRow("Department:", self.dept_input)
        form.addRow("Current Semester:", self.sem_input)
        form.addRow("UI Theme Mode:", self.theme_combo)
        form.addRow("Clock Format:", self.clock_combo)
        form.addRow("Week Starts On:", self.week_combo)

        layout.addWidget(card)

        # Footer Buttons
        btn_row = QHBoxLayout()
        btn_reset_demo = QPushButton("🔄 Reset & Seed BUBT Sample Data")
        btn_reset_demo.clicked.connect(self._reseed_demo)

        btn_save = QPushButton("🚀 Save & Launch Dashboard")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save_and_accept)

        btn_row.addWidget(btn_reset_demo)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _fill_preset(self, full_name: str, student_id: str) -> None:
        self.name_input.setText(full_name)
        self.id_input.setText(student_id)
        self.dept_input.setText("Department of CSE")

    def _reseed_demo(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset BUBT Sample Data",
            "This will reset all tables and load the default BUBT CSE sample courses, faculty (Farah Akter Munmun [FAM]), routine, and exams. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.seed_bubt_sample_data()
            user = self.db.get_user()
            self.name_input.setText(user.get("full_name", "Md. Monirul Hasan"))
            self.id_input.setText(user.get("student_id", "20255103087"))
            QMessageBox.information(self, "Sample Data Loaded", "BUBT CSE sample database has been restored!")

    def _save_and_accept(self) -> None:
        full_name = self.name_input.text().strip()
        student_id = self.id_input.text().strip()
        if not full_name or not student_id:
            QMessageBox.warning(self, "Validation Error", "Please enter both your Full Name and Student ID.")
            return

        self.db.update_user(
            full_name=full_name,
            student_id=student_id,
            department=self.dept_input.text().strip() or "Department of CSE",
            semester=self.sem_input.text().strip() or "Fall 2026",
            theme_preference=self.theme_combo.currentText(),
            clock_format=self.clock_combo.currentText(),
            week_start_day=self.week_combo.currentText(),
            onboarded=1,
        )
        self.accept()
