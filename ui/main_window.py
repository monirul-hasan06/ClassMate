from datetime import datetime
from typing import Dict
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager
from services.api_service import APIService
from services.notification_service import NotificationService
from ui.dashboard_page import DashboardPage
from ui.exams_page import ExamsPage
from ui.faculty_page import FacultyPage
from ui.learning_hub_page import LearningHubPage
from ui.onboarding_dialog import OnboardingDialog
from ui.resources import (
    get_action_icon,
    get_app_icon,
    get_app_logo_pixmap,
    get_code_font,
    get_nav_icon,
)
from ui.routine_page import RoutinePage
from ui.settings_page import SettingsPage
from ui.styles import build_stylesheet


class MainWindow(QMainWindow):
    """
    Main Application Window for ClassMate – An Academic & Learning Assistant.
    Combines Sidebar Navigation, Live Top Bar Clock, In-App Alert Toast Banner,
    System Tray Notifications, and Stacked Feature Pages.
    """

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.api_service = APIService(self.db)

        self.setWindowTitle("ClassMate – An Academic & Learning Assistant (BUBT DBMS Project)")
        self.resize(1340, 840)
        self.setMinimumSize(1100, 700)

        # System Tray & Application Window Icon
        self.tray_icon = QSystemTrayIcon(self)
        app_icon = get_app_icon()
        self.setWindowIcon(app_icon)
        self.tray_icon.setIcon(app_icon)
        self.tray_icon.setToolTip("ClassMate – Academic & Learning Assistant")
        self.tray_icon.show()

        self.notification_service = NotificationService(self.db, self.tray_icon, self)
        self.notification_service.alert_triggered.connect(self._show_in_app_toast)

        self.nav_buttons: Dict[str, QPushButton] = {}
        self._build_ui()
        self.apply_user_theme()

        # Live Clock Timer (ticks every second)
        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self._update_live_clock)
        self.clock_timer.start()
        self._update_live_clock()

        # Check if onboarding should be shown on first launch
        user = self.db.get_user()
        if not user.get("onboarded", 1):
            QTimer.singleShot(200, self.open_onboarding_dialog)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================================================
        # LEFT SIDEBAR NAVIGATION
        # =====================================================================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(250)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(16, 22, 16, 18)
        sb_layout.setSpacing(8)

        # Modern Brand Header with High-Resolution ClassMate Logo + Typography
        brand_container = QWidget()
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 4, 0, 8)
        brand_layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)

        logo_label = QLabel()
        logo_label.setPixmap(get_app_logo_pixmap(40, 40, dark=True))
        logo_label.setFixedSize(40, 40)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand_titles = QVBoxLayout()
        brand_titles.setSpacing(2)
        brand_title = QLabel("ClassMate")
        brand_title.setObjectName("BrandTitle")
        brand_tagline = QLabel("Academic Assistant")
        brand_tagline.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        brand_titles.addWidget(brand_title)
        brand_titles.addWidget(brand_tagline)

        brand_row.addWidget(logo_label)
        brand_row.addLayout(brand_titles, 1)
        brand_layout.addLayout(brand_row)

        # University affiliation badge
        bubt_badge = QFrame()
        bubt_badge.setStyleSheet(
            "background-color: #1E293B; border: 1px solid #334155; border-radius: 8px;"
        )
        bubt_layout = QHBoxLayout(bubt_badge)
        bubt_layout.setContentsMargins(8, 6, 8, 6)
        bubt_layout.setSpacing(8)

        brand_logo_lbl = QLabel()
        brand_logo_lbl.setPixmap(get_app_logo_pixmap(32, 32, dark=True))
        brand_logo_lbl.setFixedSize(32, 32)
        brand_logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bubt_text = QLabel("Dept. of CSE • BUBT")
        bubt_text.setStyleSheet("color: #CBD5E1; font-size: 13px; font-weight: 400;")
        bubt_layout.addWidget(brand_logo_lbl)
        bubt_layout.addWidget(bubt_text, 1)

        brand_layout.addWidget(bubt_badge)
        sb_layout.addWidget(brand_container)
        sb_layout.addSpacing(10)

        nav_items = [
            ("dashboard", "Smart Dashboard"),
            ("routine", "Class Routine && Grid"),
            ("exams", "Exams && Assessments"),
            ("faculty", "Faculty Directory"),
            ("learning", "Learning Hub (API)"),
            ("settings", "Settings && About"),
        ]

        for key, label in nav_items:
            btn = QPushButton(f"  {label}")
            btn.setProperty("class", "NavButton")
            btn.setIcon(get_nav_icon(key))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.navigate_to(k))
            sb_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sb_layout.addStretch()

        # Sidebar Footer Credits Card
        credit_box = QFrame()
        credit_box.setStyleSheet(
            "background-color: #1E293B; border: 1px solid #334155; border-radius: 10px;"
        )
        cb_layout = QVBoxLayout(credit_box)
        cb_layout.setContentsMargins(10, 8, 10, 8)
        cb_layout.setSpacing(4)

        cb_hdr = QHBoxLayout()
        cb_hdr.setSpacing(6)
        footer_logo_lbl = QLabel()
        footer_logo_lbl.setPixmap(get_app_logo_pixmap(32, 32, dark=True))
        footer_logo_lbl.setFixedSize(32, 32)
        footer_logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_course = QLabel("DBMS Course Project")
        lbl_course.setStyleSheet("color: #818CF8; font-weight: 600; font-size: 13px;")
        cb_hdr.addWidget(footer_logo_lbl)
        cb_hdr.addWidget(lbl_course, 1)
        cb_layout.addLayout(cb_hdr)

        lbl_authors = QLabel(
            "Md. Monirul Hasan (20255103087)\n"
            "Yusuf Ali (20255103138)\n"
            "Supervisor: Farah Akter Munmun"
        )
        lbl_authors.setStyleSheet("color: #94A3B8; font-size: 10px;")
        cb_layout.addWidget(lbl_authors)
        sb_layout.addWidget(credit_box)

        root_layout.addWidget(sidebar)

        # =====================================================================
        # RIGHT CONTENT AREA (Header Bar + Toast Banner + Stacked Pages)
        # =====================================================================
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Bar
        topbar = QFrame()
        topbar.setProperty("class", "Card")
        topbar.setStyleSheet("border-radius: 0px; border-left: none; border-right: none; border-top: none;")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 10, 24, 10)

        self.lbl_top_user = QLabel("👤 Md. Monirul Hasan (ID: 20255103087)")
        self.lbl_top_user.setStyleSheet("font-weight: 400; font-size: 13px;")

        self.lbl_live_clock = QLabel("🕒 12:00:00 PM")
        self.lbl_live_clock.setStyleSheet(
            "background-color: #312E81; color: #FFFFFF; font-weight: 800; "
            "padding: 5px 12px; border-radius: 8px; font-size: 13px;"
        )

        btn_quick_theme = QPushButton(" Toggle Theme")
        btn_quick_theme.setIcon(get_action_icon("theme"))
        btn_quick_theme.setIconSize(QSize(16, 16))
        btn_quick_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_quick_theme.clicked.connect(self._cycle_theme)

        btn_onboard = QPushButton(" Onboarding")
        btn_onboard.setIcon(get_action_icon("sparkles"))
        btn_onboard.setIconSize(QSize(16, 16))
        btn_onboard.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_onboard.clicked.connect(self.open_onboarding_dialog)

        tb_layout.addWidget(self.lbl_top_user)
        tb_layout.addStretch()
        tb_layout.addWidget(self.lbl_live_clock)
        tb_layout.addWidget(btn_quick_theme)
        tb_layout.addWidget(btn_onboard)
        right_layout.addWidget(topbar)

        # In-App Notification Toast Banner (Hidden until an alert triggers)
        self.toast_banner = QFrame()
        self.toast_banner.setStyleSheet(
            "background-color: #1E1B4B; border-bottom: 2px solid #6366F1; color: #FFFFFF;"
        )
        self.toast_banner.setVisible(False)
        toast_layout = QHBoxLayout(self.toast_banner)
        toast_layout.setContentsMargins(24, 10, 24, 10)
        self.lbl_toast_text = QLabel("")
        self.lbl_toast_text.setStyleSheet("color: #FFFFFF; font-weight: 400;")
        self.lbl_toast_text.setWordWrap(True)
        btn_close_toast = QPushButton("Dismiss ✕")
        btn_close_toast.clicked.connect(lambda: self.toast_banner.setVisible(False))
        toast_layout.addWidget(self.lbl_toast_text, 1)
        toast_layout.addWidget(btn_close_toast)
        right_layout.addWidget(self.toast_banner)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.page_dashboard = DashboardPage(self.db, on_navigate=self.navigate_to)
        self.page_routine = RoutinePage(self.db, on_data_changed=self.refresh_all_pages)
        self.page_exams = ExamsPage(self.db, self.notification_service, on_data_changed=self.refresh_all_pages)
        self.page_faculty = FacultyPage(self.db, on_data_changed=self.refresh_all_pages)
        self.page_learning = LearningHubPage(self.db, self.api_service)
        self.page_settings = SettingsPage(
            self.db,
            self.notification_service,
            on_settings_applied=self.on_settings_updated,
            on_open_onboarding=self.open_onboarding_dialog,
        )

        self.pages_map: Dict[str, QWidget] = {
            "dashboard": self.page_dashboard,
            "routine": self.page_routine,
            "exams": self.page_exams,
            "faculty": self.page_faculty,
            "learning": self.page_learning,
            "settings": self.page_settings,
        }

        for page in self.pages_map.values():
            self.stack.addWidget(page)

        right_layout.addWidget(self.stack, 1)
        root_layout.addWidget(right_area, 1)

        self.navigate_to("dashboard")

    def navigate_to(self, page_key: str) -> None:
        if page_key not in self.pages_map:
            return
        self.stack.setCurrentWidget(self.pages_map[page_key])
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == page_key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh active page
        active_w = self.pages_map[page_key]
        if hasattr(active_w, "refresh_data"):
            active_w.refresh_data()

    def refresh_all_pages(self) -> None:
        user = self.db.get_user()
        self.lbl_top_user.setText(
            f"👤 {user.get('full_name', 'Md. Monirul Hasan')} (ID: {user.get('student_id', '20255103087')})  •  "
            f"Theme: {user.get('theme_preference', 'Dark')}"
        )
        for page in self.pages_map.values():
            if hasattr(page, "refresh_data"):
                page.refresh_data()
        self._update_live_clock()

    def apply_user_theme(self) -> None:
        user = self.db.get_user()
        pref = user.get("theme_preference", "Dark")
        qss = build_stylesheet(pref)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
            app.setFont(get_code_font(), "QPlainTextEdit")
        else:
            self.setStyleSheet(qss)
        self.lbl_top_user.setText(
            f"👤 {user.get('full_name', 'Md. Monirul Hasan')} (ID: {user.get('student_id', '20255103087')})  •  "
            f"Theme: {pref}"
        )

    def on_settings_updated(self) -> None:
        self.apply_user_theme()
        self.refresh_all_pages()

    def _cycle_theme(self) -> None:
        user = self.db.get_user()
        order = ["Dark", "Light", "System"]
        cur = user.get("theme_preference", "Dark")
        next_theme = order[(order.index(cur) + 1) % len(order)] if cur in order else "Dark"
        self.db.update_user(
            full_name=user.get("full_name", "Md. Monirul Hasan"),
            student_id=user.get("student_id", "20255103087"),
            department=user.get("department", "Department of CSE"),
            semester=user.get("semester", "Fall 2026"),
            theme_preference=next_theme,
            clock_format=user.get("clock_format", "12h"),
            week_start_day=user.get("week_start_day", "Saturday"),
            onboarded=1,
        )
        self.on_settings_updated()

    def _update_live_clock(self) -> None:
        user = self.db.get_user()
        fmt = user.get("clock_format", "12h")
        now = datetime.now()
        if fmt == "24h":
            time_str = now.strftime("%H:%M:%S (24h)")
        else:
            time_str = now.strftime("%I:%M:%S %p").lstrip("0")
        self.lbl_live_clock.setText(f"🕒 {time_str}")

    def _show_in_app_toast(self, title: str, message: str, category: str) -> None:
        flat_msg = message.replace("\n", "  |  ")
        self.lbl_toast_text.setText(f"🔔 {title} — {flat_msg}")
        self.toast_banner.setVisible(True)

    def open_onboarding_dialog(self) -> None:
        dlg = OnboardingDialog(self.db, parent=self)
        if dlg.exec():
            self.on_settings_updated()

