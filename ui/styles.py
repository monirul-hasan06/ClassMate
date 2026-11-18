import sys
from typing import Dict


def detect_windows_dark_mode() -> bool:
    """Detect whether Windows 10/11 is currently using Dark App Mode."""
    if sys.platform == "win32":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return True
    return True


def resolve_theme(theme_preference: str) -> str:
    """Resolve 'Light', 'Dark', or 'System' into 'Dark' or 'Light'."""
    pref = (theme_preference or "Dark").strip().capitalize()
    if pref == "System":
        return "Dark" if detect_windows_dark_mode() else "Light"
    if pref not in ("Dark", "Light"):
        return "Dark"
    return pref


def get_theme_palette(theme_preference: str = "Dark") -> Dict[str, str]:
    mode = resolve_theme(theme_preference)
    if mode == "Dark":
        return {
            "mode": "Dark",
            "bg_main": "#0F172A",
            "bg_sidebar": "#0B1120",
            "bg_card": "#1E293B",
            "bg_card_alt": "#263449",
            "bg_input": "#0F172A",
            "border": "#334155",
            "border_focus": "#6366F1",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "accent": "#6366F1",
            "accent_hover": "#4F46E5",
            "accent_soft": "#1E1B4B",
            "success": "#10B981",
            "success_hover": "#059669",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "warning": "#F59E0B",
            "info": "#3B82F6",
            "hero_grad_start": "#1E1B4B",
            "hero_grad_end": "#1E293B",
            "hero_border": "#4F46E5",
        }
    else:
        return {
            "mode": "Light",
            "bg_main": "#F1F5F9",
            "bg_sidebar": "#0F172A",
            "bg_card": "#FFFFFF",
            "bg_card_alt": "#F8FAFC",
            "bg_input": "#FFFFFF",
            "border": "#CBD5E1",
            "border_focus": "#4F46E5",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "text_muted": "#64748B",
            "accent": "#4F46E5",
            "accent_hover": "#4338CA",
            "accent_soft": "#EEF2FF",
            "success": "#059669",
            "success_hover": "#047857",
            "danger": "#DC2626",
            "danger_hover": "#B91C1C",
            "warning": "#D97706",
            "info": "#2563EB",
            "hero_grad_start": "#EEF2FF",
            "hero_grad_end": "#E0E7FF",
            "hero_border": "#6366F1",
        }


def build_stylesheet(theme_preference: str = "Dark") -> str:
    p = get_theme_palette(theme_preference)
    return f"""
        QMainWindow, QDialog {{
            background-color: {p['bg_main']};
            color: {p['text_primary']};
            font-family: 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            font-weight: 400;
        }}
        QWidget {{
            color: {p['text_primary']};
            font-family: 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            font-weight: 400;
        }}
        QPlainTextEdit {{
            font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            font-weight: 400;
        }}
        QFrame#Sidebar {{
            background-color: {p['bg_sidebar']};
            border-right: 1px solid #1E293B;
        }}
        QLabel#BrandTitle {{
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        QLabel#BrandSubtitle {{
            color: #94A3B8;
            font-size: 11px;
            font-weight: 400;
        }}
        QPushButton.NavButton {{
            background-color: transparent;
            color: #CBD5E1;
            border: none;
            border-radius: 8px;
            padding: 11px 14px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton.NavButton:hover {{
            background-color: #1E293B;
            color: #FFFFFF;
        }}
        QPushButton.NavButton[active="true"] {{
            background-color: {p['accent']};
            color: #FFFFFF;
        }}
        QFrame.Card {{
            background-color: {p['bg_card']};
            border: 1px solid {p['border']};
            border-radius: 12px;
        }}
        QFrame.HeroCard {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {p['hero_grad_start']}, stop:1 {p['hero_grad_end']});
            border: 2px solid {p['hero_border']};
            border-radius: 14px;
        }}
        QFrame.SubCard {{
            background-color: {p['bg_card_alt']};
            border: 1px solid {p['border']};
            border-radius: 10px;
        }}
        QLabel.PageTitle {{
            font-size: 22px;
            font-weight: 600;
            color: {p['text_primary']};
        }}
        QLabel.SectionTitle {{
            font-size: 15px;
            font-weight: 600;
            color: {p['text_primary']};
        }}
        QLabel.MutedText {{
            color: {p['text_secondary']};
            font-size: 13px;
        }}
        QPushButton {{
            background-color: {p['bg_card_alt']};
            color: {p['text_primary']};
            border: 1px solid {p['border']};
            border-radius: 8px;
            padding: 8px 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            border-color: {p['accent']};
        }}
        QPushButton.PrimaryBtn {{
            background-color: {p['accent']};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton.PrimaryBtn:hover {{
            background-color: {p['accent_hover']};
        }}
        QPushButton.SuccessBtn {{
            background-color: {p['success']};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton.SuccessBtn:hover {{
            background-color: {p['success_hover']};
        }}
        QPushButton.DangerBtn {{
            background-color: {p['danger']};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton.DangerBtn:hover {{
            background-color: {p['danger_hover']};
        }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit, QTextEdit {{
            background-color: {p['bg_input']};
            color: {p['text_primary']};
            border: 1px solid {p['border']};
            border-radius: 8px;
            padding: 7px 10px;
            selection-background-color: {p['accent']};
        }}
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
            border: 1.5px solid {p['border_focus']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {p['bg_card']};
            color: {p['text_primary']};
            selection-background-color: {p['accent']};
            selection-color: #FFFFFF;
            border: 1px solid {p['border']};
        }}
        QTabWidget::pane {{
            border: 1px solid {p['border']};
            border-radius: 10px;
            background-color: {p['bg_card']};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {p['bg_card_alt']};
            color: {p['text_secondary']};
            border: 1px solid {p['border']};
            padding: 8px 16px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background-color: {p['accent']};
            color: #FFFFFF;
            border-color: {p['accent']};
        }}
        QTableWidget {{
            background-color: {p['bg_card']};
            alternate-background-color: {p['bg_card_alt']};
            color: {p['text_primary']};
            border: 1px solid {p['border']};
            border-radius: 10px;
            gridline-color: {p['border']};
            selection-background-color: {p['accent']};
            selection-color: #FFFFFF;
        }}
        QHeaderView::section {{
            background-color: {p['bg_card_alt']};
            color: {p['text_primary']};
            font-weight: 600;
            padding: 8px 10px;
            border: none;
            border-bottom: 1px solid {p['border']};
            border-right: 1px solid {p['border']};
        }}
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QProgressBar {{
            border: 1px solid {p['border']};
            border-radius: 6px;
            background-color: {p['bg_input']};
            text-align: center;
            color: {p['text_primary']};
            font-weight: 400;
            min-height: 16px;
            max-height: 16px;
        }}
        QProgressBar::chunk {{
            background-color: {p['success']};
            border-radius: 5px;
        }}
        QCheckBox {{
            spacing: 8px;
            font-weight: 600;
        }}
    """

