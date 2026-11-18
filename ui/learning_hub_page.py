import webbrowser
from datetime import datetime
from typing import Dict
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager
from services.api_service import APIService
from ui.resources import get_app_logo_pixmap


class ClassroomItemDialog(QDialog):
    """Dialog to add a manual or synced Google Classroom Assignment/Announcement."""

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Add Google Classroom Assignment / Announcement")
        self.setMinimumWidth(450)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.course_combo = QComboBox()
        for c in self.db.get_courses(include_archived=False):
            self.course_combo.addItem(f"{c['course_code']} – {c['course_name']}", c["course_code"])

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Assignment", "Announcement", "Lab Task", "Project Milestone"])

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., Assignment 4: SQL Triggers & Views")

        self.due_edit = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.due_edit.setPlaceholderText("YYYY-MM-DD")

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(75)

        form.addRow("Course:", self.course_combo)
        form.addRow("Item Type:", self.type_combo)
        form.addRow("Title:", self.title_edit)
        form.addRow("Due Date:", self.due_edit)
        form.addRow("Description:", self.desc_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Item")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Required", "Please enter a title.")
            return
        course_code = self.course_combo.currentData() or "CSE 208"
        self.db.add_classroom_item(
            course_code=course_code,
            title=title,
            item_type=self.type_combo.currentText(),
            due_date=self.due_edit.text().strip(),
            status="Pending",
            description=self.desc_edit.toPlainText().strip(),
        )
        self.accept()


class LearningHubPage(QWidget):
    """
    Supplementary API-Driven Features Page (Proposal Section 4.7):
      1. YouTube Learning Assistant (Auto-extracts course keywords to recommend top-ranked playlists)
      2. Google Classroom Integration (Syncs assignment deadlines & course announcements)
    """

    def __init__(self, db: DatabaseManager, api_service: APIService, parent=None):
        super().__init__(parent)
        self.db = db
        self.api_service = api_service
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Page Header
        top_row = QHBoxLayout()
        title_col = QVBoxLayout()
        lbl_title = QLabel("🚀 Smart Learning Hub (YouTube & Google Classroom)")
        lbl_title.setProperty("class", "PageTitle")
        lbl_sub = QLabel(
            "Distraction-free YouTube playlist recommender powered by automatic course keyword extraction & Google Classroom deadline sync"
        )
        lbl_sub.setProperty("class", "MutedText")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        top_row.addLayout(title_col, 1)
        layout.addLayout(top_row)

        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(20, 20))

        # =====================================================================
        # TAB 1: YOUTUBE LEARNING ASSISTANT
        # =====================================================================
        yt_tab = QWidget()
        yt_layout = QVBoxLayout(yt_tab)
        yt_layout.setContentsMargins(14, 14, 14, 14)
        yt_layout.setSpacing(14)

        # Search & Extracted Course Keyword Bar
        search_card = QFrame()
        search_card.setProperty("class", "SubCard")
        sc_layout = QVBoxLayout(search_card)
        sc_layout.setContentsMargins(16, 14, 16, 14)
        sc_layout.setSpacing(10)

        # Brand header for YouTube Learning Assistant
        yt_brand_row = QHBoxLayout()
        yt_brand_row.setSpacing(10)
        yt_logo_badge = QLabel()
        yt_logo_badge.setPixmap(get_app_logo_pixmap(32, 32))
        yt_logo_badge.setFixedSize(32, 32)
        yt_logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        yt_brand_title = QLabel("YouTube Learning Engine • Curated Academic Playlists & Topic Search")
        yt_brand_title.setStyleSheet("font-size: 14px; font-weight: 600;")
        yt_brand_row.addWidget(yt_logo_badge)
        yt_brand_row.addWidget(yt_brand_title, 1)
        sc_layout.addLayout(yt_brand_row)

        search_row = QHBoxLayout()
        self.yt_search_input = QLineEdit()
        self.yt_search_input.setPlaceholderText(
            "🔎 Enter a course topic (e.g., 'SQL Normalization 3NF', 'B+ Tree Indexing', 'Dynamic Programming')..."
        )
        self.yt_search_input.returnPressed.connect(self._on_yt_search)

        btn_search = QPushButton("🎯 Recommend Playlists")
        btn_search.setProperty("class", "PrimaryBtn")
        btn_search.clicked.connect(self._on_yt_search)

        btn_reset_kw = QPushButton("🔄 Auto-Match All Enrolled Courses")
        btn_reset_kw.clicked.connect(self._reset_yt_search)

        search_row.addWidget(self.yt_search_input, 1)
        search_row.addWidget(btn_search)
        search_row.addWidget(btn_reset_kw)
        sc_layout.addLayout(search_row)

        # Auto-extracted keywords chip row
        self.kw_chips_layout = QHBoxLayout()
        self.kw_chips_layout.setSpacing(8)
        sc_layout.addLayout(self.kw_chips_layout)
        yt_layout.addWidget(search_card)

        # Scrollable grid of playlist recommendation cards
        yt_scroll = QScrollArea()
        yt_scroll.setWidgetResizable(True)
        yt_grid_host = QWidget()
        self.yt_cards_grid = QGridLayout(yt_grid_host)
        self.yt_cards_grid.setSpacing(14)
        yt_scroll.setWidget(yt_grid_host)
        yt_layout.addWidget(yt_scroll, 1)

        self.tabs.addTab(yt_tab, QIcon(get_app_logo_pixmap(24, 24)), "YouTube Learning Assistant")

        # =====================================================================
        # TAB 2: GOOGLE CLASSROOM INTEGRATION
        # =====================================================================
        gc_tab = QWidget()
        gc_layout = QVBoxLayout(gc_tab)
        gc_layout.setContentsMargins(14, 14, 14, 14)
        gc_layout.setSpacing(14)

        gc_banner = QFrame()
        gc_banner.setProperty("class", "HeroCard")
        gb_layout = QHBoxLayout(gc_banner)
        gb_layout.setContentsMargins(18, 14, 18, 14)
        gb_layout.setSpacing(14)

        gc_logo_badge = QLabel()
        gc_logo_badge.setPixmap(get_app_logo_pixmap(40, 40))
        gc_logo_badge.setFixedSize(40, 40)
        gc_logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        gb_left = QVBoxLayout()
        gb_left.setSpacing(2)
        self.lbl_gc_status = QLabel("Google Classroom OAuth 2.0 Integration • Connected (BUBT CSE Workspace)")
        self.lbl_gc_status.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.lbl_gc_sub = QLabel(
            "Automatically syncs course assignment deadlines, lab report submissions, and instructor announcements."
        )
        self.lbl_gc_sub.setProperty("class", "MutedText")
        gb_left.addWidget(self.lbl_gc_status)
        gb_left.addWidget(self.lbl_gc_sub)

        btn_sync_now = QPushButton("🔄 Sync Google Classroom Now")
        btn_sync_now.setProperty("class", "PrimaryBtn")
        btn_sync_now.clicked.connect(self._sync_classroom_now)

        btn_add_gc = QPushButton("＋ Add Classroom Task")
        btn_add_gc.clicked.connect(self._open_add_gc_item)

        btn_open_gc = QPushButton("🌐 Open Classroom Web")
        btn_open_gc.clicked.connect(lambda: webbrowser.open("https://classroom.google.com"))

        gb_layout.addWidget(gc_logo_badge)
        gb_layout.addLayout(gb_left, 1)
        gb_layout.addWidget(btn_sync_now)
        gb_layout.addWidget(btn_add_gc)
        gb_layout.addWidget(btn_open_gc)
        gc_layout.addWidget(gc_banner)

        self.tabs.addTab(gc_tab, QIcon(get_app_logo_pixmap(24, 24)), "Google Classroom Integration")

        self.gc_table = QTableWidget()
        self.gc_table.setColumnCount(7)
        self.gc_table.setHorizontalHeaderLabels([
            "Course", "Type", "Assignment / Announcement Title", "Due Date", "Status", "Details", "Actions"
        ])
        self.gc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.gc_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.gc_table.setAlternatingRowColors(True)
        self.gc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        gc_layout.addWidget(self.gc_table, 1)

        self.tabs.addTab(gc_tab, "🎓 Google Classroom Deadlines & Announcements")
        layout.addWidget(self.tabs, 1)

    def refresh_data(self) -> None:
        self._populate_keyword_chips()
        self._populate_youtube_cards(self.yt_search_input.text().strip())
        self._populate_classroom_table()

    def _populate_keyword_chips(self) -> None:
        while self.kw_chips_layout.count():
            item = self.kw_chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lbl = QLabel("✨ Auto-Extracted Course Keywords:")
        lbl.setProperty("class", "MutedText")
        self.kw_chips_layout.addWidget(lbl)

        extracted = self.api_service.extract_course_keywords()
        for course_info in extracted[:6]:
            chip_text = f"{course_info['course_code']}: {course_info['course_name']}"
            btn_chip = QPushButton(chip_text)
            btn_chip.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_chip.setStyleSheet("padding: 4px 10px; font-size: 11px; border-radius: 12px;")
            btn_chip.clicked.connect(lambda _, q=course_info["course_name"]: self._filter_by_chip(q))
            self.kw_chips_layout.addWidget(btn_chip)

        self.kw_chips_layout.addStretch()

    def _filter_by_chip(self, query: str) -> None:
        self.yt_search_input.setText(query)
        self._populate_youtube_cards(query)

    def _on_yt_search(self) -> None:
        self._populate_youtube_cards(self.yt_search_input.text().strip())

    def _reset_yt_search(self) -> None:
        self.yt_search_input.clear()
        self._populate_youtube_cards("")

    def _populate_youtube_cards(self, custom_query: str = "") -> None:
        while self.yt_cards_grid.count():
            item = self.yt_cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        playlists = self.api_service.get_youtube_recommendations(custom_query)
        for idx, pl in enumerate(playlists):
            card = self._create_playlist_card(pl)
            row = idx // 2
            col = idx % 2
            self.yt_cards_grid.addWidget(card, row, col)

    def _create_playlist_card(self, pl: Dict[str, str]) -> QFrame:
        card = QFrame()
        card.setProperty("class", "Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(8)

        top_meta = QHBoxLayout()
        tag = QLabel(pl.get("course_tag", "Course Playlist"))
        tag.setStyleSheet(
            "background-color: #312E81; color: #E0E7FF; font-weight: 700; font-size: 11px; "
            "padding: 3px 10px; border-radius: 10px;"
        )
        rating = QLabel(f"⭐ {pl.get('rating', 'Top Ranked')} • {pl.get('video_count', 'Playlist')}")
        rating.setProperty("class", "MutedText")
        top_meta.addWidget(tag)
        top_meta.addStretch()
        top_meta.addWidget(rating)
        cl.addLayout(top_meta)

        title = QLabel(pl.get("title", "Playlist"))
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        title.setWordWrap(True)
        cl.addWidget(title)

        channel = QLabel(f"📺 Educator / Channel: {pl.get('channel', 'YouTube Education')}")
        channel.setStyleSheet("font-weight: 400; color: #818CF8;")
        cl.addWidget(channel)

        topics = QLabel(f"📖 Key Topics: {pl.get('topics', '')}")
        topics.setProperty("class", "MutedText")
        topics.setWordWrap(True)
        cl.addWidget(topics)

        btn_row = QHBoxLayout()
        btn_watch = QPushButton("▶️ Watch Distraction-Free Playlist on YouTube")
        btn_watch.setProperty("class", "PrimaryBtn")
        btn_watch.setCursor(Qt.CursorShape.PointingHandCursor)
        url = pl.get("url", "https://www.youtube.com")
        btn_watch.clicked.connect(lambda _, u=url: webbrowser.open(u))
        btn_row.addStretch()
        btn_row.addWidget(btn_watch)
        cl.addLayout(btn_row)
        return card

    def _populate_classroom_table(self) -> None:
        items = self.db.get_classroom_items()
        self.gc_table.setRowCount(len(items))

        for r_idx, item in enumerate(items):
            self.gc_table.setItem(r_idx, 0, QTableWidgetItem(item["course_code"]))
            self.gc_table.setItem(r_idx, 1, QTableWidgetItem(item["item_type"]))
            self.gc_table.setItem(r_idx, 2, QTableWidgetItem(item["title"]))
            self.gc_table.setItem(r_idx, 3, QTableWidgetItem(item.get("due_date", "")))
            self.gc_table.setItem(r_idx, 4, QTableWidgetItem(item.get("status", "Pending")))
            self.gc_table.setItem(r_idx, 5, QTableWidgetItem(item.get("description", "")))

            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(6)

            btn_done = QPushButton("✓ Mark Submitted")
            btn_done.setProperty("class", "SuccessBtn")
            btn_done.clicked.connect(lambda _, iid=item["item_id"]: self._mark_gc_submitted(iid))

            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.clicked.connect(lambda _, iid=item["item_id"]: self._delete_gc_item(iid))

            al.addWidget(btn_done)
            al.addWidget(btn_del)
            self.gc_table.setCellWidget(r_idx, 6, act_w)
            self.gc_table.setRowHeight(r_idx, 44)

    def _sync_classroom_now(self) -> None:
        res = self.api_service.sync_google_classroom()
        self._populate_classroom_table()
        self.lbl_gc_sub.setText(
            f"Last synced at {res['synced_at']} • Total Active Classroom Items: {res['total_items']}"
        )
        QMessageBox.information(
            self,
            "Google Classroom Sync Complete",
            f"Synchronized with {res['mode']} at {res['synced_at']}.\n"
            f"New announcements/assignments fetched: {res['added_count']}\n"
            f"Total tracked items: {res['total_items']}",
        )

    def _open_add_gc_item(self) -> None:
        dlg = ClassroomItemDialog(self.db, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._populate_classroom_table()

    def _mark_gc_submitted(self, item_id: int) -> None:
        self.db.update_classroom_item_status(item_id, "Submitted ✓")
        self._populate_classroom_table()

    def _delete_gc_item(self, item_id: int) -> None:
        self.db.delete_classroom_item(item_id)
        self._populate_classroom_table()

