import webbrowser
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager


class FacultyDialog(QDialog):
    """Dialog to Add or Edit a Faculty Member in the `faculty` table."""

    def __init__(self, db: DatabaseManager, faculty_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.faculty_data = faculty_data
        self.setWindowTitle("Edit Faculty Record" if faculty_data else "Add Faculty Member")
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.name_edit = QLineEdit(self.faculty_data.get("name", "") if self.faculty_data else "")
        self.name_edit.setPlaceholderText("e.g., Farah Akter Munmun")

        self.short_edit = QLineEdit(self.faculty_data.get("short_name", "") if self.faculty_data else "")
        self.short_edit.setPlaceholderText("e.g., FAM")

        self.desig_edit = QLineEdit(
            self.faculty_data.get("designation", "Assistant Professor") if self.faculty_data else "Assistant Professor"
        )
        self.dept_edit = QLineEdit(
            self.faculty_data.get("department", "Department of CSE") if self.faculty_data else "Department of CSE"
        )
        self.email_edit = QLineEdit(self.faculty_data.get("email", "") if self.faculty_data else "")
        self.email_edit.setPlaceholderText("e.g., farha.akhter@bubt.edu.bd")

        self.phone_edit = QLineEdit(self.faculty_data.get("phone", "") if self.faculty_data else "")
        self.phone_edit.setPlaceholderText("e.g., +880 1711-000101")

        self.hours_edit = QLineEdit(self.faculty_data.get("consulting_hours", "") if self.faculty_data else "")
        self.hours_edit.setPlaceholderText("e.g., Sun & Tue: 11:30 AM - 01:30 PM")

        self.room_edit = QLineEdit(
            self.faculty_data.get("office_room", "Building 2, Room 504") if self.faculty_data else "Building 2, Room 504"
        )

        form.addRow("Full Name:", self.name_edit)
        form.addRow("Short Name / Initials:", self.short_edit)
        form.addRow("Designation:", self.desig_edit)
        form.addRow("Department:", self.dept_edit)
        form.addRow("Email Address:", self.email_edit)
        form.addRow("Contact Number:", self.phone_edit)
        form.addRow("Consulting Hours:", self.hours_edit)
        form.addRow("Office Room:", self.room_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Faculty")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        name = self.name_edit.text().strip()
        short = self.short_edit.text().strip()
        if not name or not short:
            QMessageBox.warning(self, "Validation Error", "Full Name and Short Name (Initials) are required.")
            return
        if self.faculty_data:
            self.db.update_faculty(
                faculty_id=self.faculty_data["faculty_id"],
                name=name,
                short_name=short,
                designation=self.desig_edit.text().strip(),
                department=self.dept_edit.text().strip(),
                email=self.email_edit.text().strip(),
                phone=self.phone_edit.text().strip(),
                consulting_hours=self.hours_edit.text().strip(),
                office_room=self.room_edit.text().strip(),
            )
        else:
            self.db.add_faculty(
                name=name,
                short_name=short,
                designation=self.desig_edit.text().strip(),
                department=self.dept_edit.text().strip(),
                email=self.email_edit.text().strip(),
                phone=self.phone_edit.text().strip(),
                consulting_hours=self.hours_edit.text().strip(),
                office_room=self.room_edit.text().strip(),
            )
        self.accept()


class FacultyPage(QWidget):
    """
    Faculty Directory Page (Proposal Section 4.4).
    Stores and searches Full Name, Short Name, Designation, Department,
    Email Address, Contact Number, and Office/Consulting Hours.
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

        # Header
        top_row = QHBoxLayout()
        title_col = QVBoxLayout()
        lbl_title = QLabel("👩‍🏫 Faculty Directory & Consultation Hours")
        lbl_title.setProperty("class", "PageTitle")
        lbl_sub = QLabel(
            "Centralized directory of BUBT faculty contact details, designations, emails, and consulting hours"
        )
        lbl_sub.setProperty("class", "MutedText")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        top_row.addLayout(title_col, 1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, initials [FAM], department, or email...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.refresh_data)

        btn_add = QPushButton("＋ Add Faculty Member")
        btn_add.setProperty("class", "PrimaryBtn")
        btn_add.clicked.connect(self._open_add_faculty)

        top_row.addWidget(self.search_input)
        top_row.addWidget(btn_add)
        layout.addLayout(top_row)

        # Highlighted Course Supervisor / Instructor Card (Farah Akter Munmun [FAM])
        self.supervisor_card = QFrame()
        self.supervisor_card.setProperty("class", "HeroCard")
        sup_layout = QHBoxLayout(self.supervisor_card)
        sup_layout.setContentsMargins(18, 14, 18, 14)

        sup_info = QVBoxLayout()
        lbl_badge = QLabel("⭐ COURSE INSTRUCTOR & PROJECT SUPERVISOR (DBMS)")
        lbl_badge.setStyleSheet("font-size: 11px; font-weight: 800; color: #818CF8;")
        self.lbl_sup_name = QLabel("Farah Akter Munmun [FAM] — Assistant Professor, Department of CSE, BUBT")
        self.lbl_sup_name.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.lbl_sup_meta = QLabel(
            "📧 Email: farha.akhter@bubt.edu.bd  |  🕒 Consulting Hours: Sun, Tue: 11:30 AM - 01:30 PM  |  🏢 Building 2, Room 504"
        )
        self.lbl_sup_meta.setProperty("class", "MutedText")
        sup_info.addWidget(lbl_badge)
        sup_info.addWidget(self.lbl_sup_name)
        sup_info.addWidget(self.lbl_sup_meta)

        btn_copy_sup = QPushButton("📋 Copy Email")
        btn_copy_sup.clicked.connect(lambda: self._copy_email("farha.akhter@bubt.edu.bd"))
        btn_mail_sup = QPushButton("✉️ Send Email")
        btn_mail_sup.setProperty("class", "PrimaryBtn")
        btn_mail_sup.clicked.connect(lambda: webbrowser.open("mailto:farha.akhter@bubt.edu.bd"))

        sup_layout.addLayout(sup_info, 1)
        sup_layout.addWidget(btn_copy_sup)
        sup_layout.addWidget(btn_mail_sup)
        layout.addWidget(self.supervisor_card)

        # Faculty Directory Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Full Name", "Short Name", "Designation", "Department", "Email Address", "Phone", "Consulting Hours & Room", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

    def refresh_data(self) -> None:
        query = self.search_input.text().strip() if hasattr(self, "search_input") else ""
        faculty_list = self.db.get_all_faculty(query)
        self.table.setRowCount(len(faculty_list))

        for r_idx, f in enumerate(faculty_list):
            self.table.setItem(r_idx, 0, QTableWidgetItem(f["name"]))
            self.table.setItem(r_idx, 1, QTableWidgetItem(f["short_name"]))
            self.table.setItem(r_idx, 2, QTableWidgetItem(f.get("designation", "")))
            self.table.setItem(r_idx, 3, QTableWidgetItem(f.get("department", "")))
            self.table.setItem(r_idx, 4, QTableWidgetItem(f.get("email", "")))
            self.table.setItem(r_idx, 5, QTableWidgetItem(f.get("phone", "")))
            room_and_hours = f"{f.get('consulting_hours', '')} ({f.get('office_room', '')})"
            self.table.setItem(r_idx, 6, QTableWidgetItem(room_and_hours))

            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(6)

            btn_copy = QPushButton("Copy Email")
            btn_copy.clicked.connect(lambda _, em=f.get("email", ""): self._copy_email(em))

            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda _, item=f: self._edit_faculty(item))

            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.clicked.connect(lambda _, fid=f["faculty_id"]: self._delete_faculty(fid))

            al.addWidget(btn_copy)
            al.addWidget(btn_edit)
            al.addWidget(btn_del)
            self.table.setCellWidget(r_idx, 7, act_w)
            self.table.setRowHeight(r_idx, 44)

    def _copy_email(self, email: str) -> None:
        if email:
            QApplication.clipboard().setText(email)
            QMessageBox.information(self, "Copied", f"Email address '{email}' copied to clipboard!")

    def _open_add_faculty(self) -> None:
        dlg = FacultyDialog(self.db, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()

    def _edit_faculty(self, faculty_data: Dict[str, Any]) -> None:
        dlg = FacultyDialog(self.db, faculty_data=faculty_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()

    def _delete_faculty(self, faculty_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Faculty Record",
            "Are you sure you want to remove this faculty record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_faculty(faculty_id)
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()

