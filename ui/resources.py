import os
from functools import lru_cache
from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QFont, QGuiApplication, QIcon, QImage, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")
BRAND_LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
BRAND_LOGO_DARK_PATH = os.path.join(ASSETS_DIR, "logo-dark.png")


def get_code_font() -> QFont:
    font = QFont("Cascadia Code")
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSizeF(10.5)
    for feature in ("liga", "calt"):
        font.setFeature(QFont.Tag.fromString(feature), 1)
    return font


def _device_pixel_ratio() -> float:
    app = QGuiApplication.instance()
    screen = app.primaryScreen() if app else None
    return screen.devicePixelRatio() if screen else 1.0


@lru_cache(maxsize=32)
def get_app_icon() -> QIcon:
    """Returns the current ClassMate brand mark as the application icon."""
    return QIcon(get_app_logo_pixmap(256, 256))


def render_svg_to_pixmap(svg_path: str, width: int, height: int) -> QPixmap:
    """Renders an SVG file directly into a crisp, high-DPI QPixmap with antialiasing."""
    if not os.path.exists(svg_path):
        return QPixmap()
    renderer = QSvgRenderer(svg_path)
    device_pixel_ratio = _device_pixel_ratio()
    pixel_width = max(1, round(width * device_pixel_ratio))
    pixel_height = max(1, round(height * device_pixel_ratio))
    image = QImage(pixel_width, pixel_height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    source_size = renderer.defaultSize()
    if source_size.isEmpty():
        source_size = renderer.viewBox().size().toSize()
    if source_size.isEmpty():
        painter.end()
        return QPixmap()
    target_size = source_size.scaled(
        QSize(pixel_width, pixel_height), Qt.AspectRatioMode.KeepAspectRatio
    )
    target = QRectF(
        (pixel_width - target_size.width()) / 2,
        (pixel_height - target_size.height()) / 2,
        target_size.width(),
        target_size.height(),
    )
    renderer.render(painter, target)
    painter.end()
    pixmap = QPixmap.fromImage(image)
    pixmap.setDevicePixelRatio(device_pixel_ratio)
    return pixmap


@lru_cache(maxsize=32)
def get_app_logo_pixmap(
    width: int = 48, height: int = 48, dark: bool = False
) -> QPixmap:
    """Returns the current ClassMate brand logo, preserving its aspect ratio."""
    logo_path = (
        BRAND_LOGO_DARK_PATH
        if dark and os.path.exists(BRAND_LOGO_DARK_PATH)
        else BRAND_LOGO_PATH
    )
    if not os.path.exists(logo_path):
        logo_path = os.path.join(LOGOS_DIR, "classmate_logo.svg")
    if os.path.exists(logo_path):
        if logo_path.lower().endswith(".svg"):
            return render_svg_to_pixmap(logo_path, width, height)
        pixmap = QPixmap(logo_path)
        device_pixel_ratio = _device_pixel_ratio()
        pixmap = pixmap.scaled(
            max(1, round(width * device_pixel_ratio)),
            max(1, round(height * device_pixel_ratio)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        return pixmap

    # Keep the UI usable until the new root-level asset is supplied.
    fallback_png = os.path.join(LOGOS_DIR, "classmate_logo.png")
    if os.path.exists(fallback_png):
        pixmap = QPixmap(fallback_png)
        device_pixel_ratio = _device_pixel_ratio()
        pixmap = pixmap.scaled(
            max(1, round(width * device_pixel_ratio)),
            max(1, round(height * device_pixel_ratio)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        return pixmap
    return QPixmap()


@lru_cache(maxsize=16)
def get_nav_icon(key: str) -> QIcon:
    """Returns a high-resolution vector QIcon for a sidebar navigation item."""
    svg_name = f"nav_{key}.svg"
    svg_p = os.path.join(ICONS_DIR, svg_name)
    if os.path.exists(svg_p):
        icon = QIcon()
        for sz in (20, 24, 32, 48):
            pm = render_svg_to_pixmap(svg_p, sz, sz)
            icon.addPixmap(pm)
        return icon
    png_p = os.path.join(ICONS_DIR, f"nav_{key}.png")
    if os.path.exists(png_p):
        return QIcon(png_p)
    return QIcon()


@lru_cache(maxsize=16)
def get_action_icon(key: str) -> QIcon:
    """Returns an action/status icon (e.g. 'clock', 'theme', 'sparkles')."""
    svg_name = f"icon_{key}.svg"
    svg_p = os.path.join(ICONS_DIR, svg_name)
    if os.path.exists(svg_p):
        icon = QIcon()
        for sz in (18, 24, 32):
            pm = render_svg_to_pixmap(svg_p, sz, sz)
            icon.addPixmap(pm)
        return icon
    png_p = os.path.join(ICONS_DIR, f"icon_{key}.png")
    if os.path.exists(png_p):
        return QIcon(png_p)
    return QIcon()
