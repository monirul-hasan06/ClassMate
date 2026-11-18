"""
Script to generate ultra-high-quality, professional vector (SVG) and raster (PNG, ICO)
logos and icons for ClassMate:
1. ClassMate Main App Logo & App Icon (multi-resolution ICO & PNGs)
2. BUBT (Bangladesh University of Business and Technology) Official-style University Seal/Logo
3. Google Classroom Official-Spec Logo
4. YouTube Official-Spec Logo
5. Navigation Icons (Dashboard, Routine, Exams, Faculty, Learning Hub, Settings)
6. Utility & Action Icons (Clock, Theme Toggle, Sparkles)
"""

import os
import sys
from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QImage, QPainter, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

# Headless Qt App for rendering
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(LOGOS_DIR, exist_ok=True)

# ==============================================================================
# 1. CLASSMATE APPLICATION LOGO (Premium Modern Tech-Academic Icon)
# ==============================================================================
# Designed for maximum clarity from 16px to 512px.
# Features a continuous rounded squircle, multi-layer depth, modern indigo-violet
# glass gradient, luminous academic mortarboard, open book of wisdom, and gold tassel.
CLASSMATE_APP_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Background Primary Gradient -->
    <linearGradient id="cmBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4F46E5"/>
      <stop offset="45%" stop-color="#6366F1"/>
      <stop offset="85%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>

    <!-- Top Highlight Glass Sheen -->
    <linearGradient id="cmSheen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.35"/>
      <stop offset="60%" stop-color="#FFFFFF" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0"/>
    </linearGradient>

    <!-- Mortarboard Diamond Gradient -->
    <linearGradient id="capTopGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="70%" stop-color="#F1F5F9"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </linearGradient>

    <!-- Cap Underside 3D Gradient -->
    <linearGradient id="capUnderGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#CBD5E1"/>
      <stop offset="100%" stop-color="#94A3B8"/>
    </linearGradient>

    <!-- Book Wing Left -->
    <linearGradient id="wingLeftGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#2563EB"/>
    </linearGradient>

    <!-- Book Wing Right -->
    <linearGradient id="wingRightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#A78BFA"/>
      <stop offset="100%" stop-color="#7C3AED"/>
    </linearGradient>

    <!-- Gold Accent Gradient -->
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="60%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>

    <!-- Drop Shadows -->
    <filter id="cardShadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="20" stdDeviation="24" flood-color="#0F172A" flood-opacity="0.45"/>
    </filter>
    <filter id="capShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#020617" flood-opacity="0.32"/>
    </filter>
  </defs>

  <!-- Squircle Base Canvas -->
  <rect x="28" y="28" width="456" height="456" rx="108" fill="url(#cmBg)" filter="url(#cardShadow)"/>

  <!-- Subtle Border Rim -->
  <rect x="30" y="30" width="452" height="452" rx="106" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="4"/>

  <!-- Glossy Sheen Overlay -->
  <path d="M 30 136 C 30 78 78 30 136 30 L 376 30 C 434 30 482 78 482 136 L 482 220 C 340 260 170 240 30 180 Z" 
        fill="url(#cmSheen)"/>

  <!-- Open Book / Wings of Education Base -->
  <g filter="url(#capShadow)">
    <!-- Left Open Book Wing -->
    <path d="M 256 348 C 218 316 156 312 96 332 C 88 335 84 342 84 350 L 84 402 C 84 409 91 415 98 413 C 154 394 212 400 256 428 Z" 
          fill="url(#wingLeftGrad)"/>
    <path d="M 112 348 C 160 334 208 340 242 364" stroke="#BAE6FD" stroke-width="4.5" stroke-linecap="round" fill="none" opacity="0.75"/>
    <path d="M 112 368 C 160 354 208 360 242 384" stroke="#BAE6FD" stroke-width="4.5" stroke-linecap="round" fill="none" opacity="0.45"/>

    <!-- Right Open Book Wing -->
    <path d="M 256 348 C 294 316 356 312 416 332 C 424 335 428 342 428 350 L 428 402 C 428 409 421 415 414 413 C 358 394 300 400 256 428 Z" 
          fill="url(#wingRightGrad)"/>
    <path d="M 400 348 C 352 334 304 340 270 364" stroke="#DDD6FE" stroke-width="4.5" stroke-linecap="round" fill="none" opacity="0.75"/>
    <path d="M 400 368 C 352 354 304 360 270 384" stroke="#DDD6FE" stroke-width="4.5" stroke-linecap="round" fill="none" opacity="0.45"/>

    <!-- Book Center Spine Pin -->
    <line x1="256" y1="346" x2="256" y2="428" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
  </g>

  <!-- Modern Academic Mortarboard Graduation Cap -->
  <g filter="url(#capShadow)">
    <!-- Skull Cap Underside Arch -->
    <path d="M 180 206 C 180 264 214 294 256 294 C 298 294 332 264 332 206 Z" 
          fill="#1E1B4B" opacity="0.75"/>

    <!-- Mortarboard 3D Lower Edge -->
    <polygon points="92,180 256,262 420,180 420,192 256,274 92,192" 
             fill="url(#capUnderGrad)"/>

    <!-- Main Diamond Mortarboard Top -->
    <polygon points="256,96 420,180 256,262 92,180" 
             fill="url(#capTopGrad)"/>

    <!-- Subtle Diamond Inner Rim Highlight -->
    <polygon points="256,104 410,180 256,254 102,180" 
             fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.6"/>

    <!-- Center Golden Button -->
    <ellipse cx="256" cy="178" rx="14" ry="10" fill="url(#goldGrad)"/>

    <!-- Tassel Ribbon Sweeping to Right -->
    <path d="M 256 178 Q 366 190 376 256" 
          fill="none" stroke="url(#goldGrad)" stroke-width="7" stroke-linecap="round"/>

    <!-- Hanging Golden Tassel -->
    <polygon points="368,256 384,256 388,310 364,310" 
             fill="url(#goldGrad)"/>
    <line x1="364" y1="310" x2="388" y2="310" stroke="#B45309" stroke-width="3"/>
  </g>

  <!-- Sparkling Spark of Wisdom (Upper Right) -->
  <g transform="translate(390, 96)">
    <path d="M 0 -22 Q 0 0 22 0 Q 0 0 0 22 Q 0 0 -22 0 Q 0 0 0 -22 Z" fill="#FDE047"/>
    <circle cx="0" cy="0" r="5" fill="#FFFFFF"/>
  </g>

  <!-- Subtle Ambient Sparkle (Upper Left) -->
  <g transform="translate(118, 120) scale(0.65)">
    <path d="M 0 -20 Q 0 0 20 0 Q 0 0 0 20 Q 0 0 -20 0 Q 0 0 0 -20 Z" fill="#BAE6FD"/>
  </g>
</svg>
"""

# ==============================================================================
# 2. BUBT OFFICIAL-STYLE UNIVERSITY SEAL (Bangladesh University of Business & Technology)
# ==============================================================================
# Authentic circular university seal with deep royal navy disc, golden filigree borders,
# clear vector typography, torch of wisdom, graduation cap, and open book of knowledge.
BUBT_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Deep Royal Navy Radial Gradient -->
    <radialGradient id="bubtNavyGrad" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#1E3A8A"/>
      <stop offset="60%" stop-color="#172554"/>
      <stop offset="100%" stop-color="#0A0F1D"/>
    </radialGradient>

    <!-- Rich Academic Gold Gradient -->
    <linearGradient id="bubtGoldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FEF08A"/>
      <stop offset="40%" stop-color="#F59E0B"/>
      <stop offset="85%" stop-color="#D97706"/>
      <stop offset="100%" stop-color="#92400E"/>
    </linearGradient>

    <!-- Torch Flame Gradient -->
    <linearGradient id="flameGrad" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#DC2626"/>
      <stop offset="45%" stop-color="#F97316"/>
      <stop offset="100%" stop-color="#FDE047"/>
    </linearGradient>

    <!-- Drop Shadow -->
    <filter id="sealShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#0B132B" flood-opacity="0.48"/>
    </filter>

    <!-- Text Curved Paths -->
    <path id="curveTop" d="M 68 256 A 188 188 0 0 1 444 256" fill="none"/>
    <path id="curveBottom" d="M 444 256 A 188 188 0 0 1 68 256" fill="none"/>
  </defs>

  <!-- Outer Deep Navy Circle Base -->
  <circle cx="256" cy="256" r="236" fill="url(#bubtNavyGrad)" filter="url(#sealShadow)"/>

  <!-- Concentric Gold Filigree Borders -->
  <circle cx="256" cy="256" r="232" fill="none" stroke="url(#bubtGoldGrad)" stroke-width="6"/>
  <circle cx="256" cy="256" r="218" fill="none" stroke="url(#bubtGoldGrad)" stroke-width="2.5" stroke-dasharray="7,5"/>
  <circle cx="256" cy="256" r="148" fill="none" stroke="url(#bubtGoldGrad)" stroke-width="5"/>
  <circle cx="256" cy="256" r="142" fill="none" stroke="#3B82F6" stroke-width="2"/>

  <!-- University Name Along Upper Arc -->
  <text font-family="'Inter', 'Segoe UI', Arial, sans-serif" font-size="21" font-weight="900" fill="#FFFFFF" letter-spacing="3.2">
    <textPath href="#curveTop" startOffset="50%" text-anchor="middle">
      BANGLADESH UNIVERSITY OF BUSINESS &amp; TECH
    </textPath>
  </text>

  <!-- Established & Location Along Lower Arc -->
  <text font-family="'Inter', 'Segoe UI', Arial, sans-serif" font-size="19" font-weight="800" fill="url(#bubtGoldGrad)" letter-spacing="3.8">
    <textPath href="#curveBottom" startOffset="50%" text-anchor="middle">
      ★ ESTD. 2003 • DHAKA ★
    </textPath>
  </text>

  <!-- Inner Center Disc Background -->
  <circle cx="256" cy="256" r="138" fill="#0B1120"/>

  <!-- Torch of Wisdom / Enlightenment (Center Core) -->
  <g transform="translate(256, 175)">
    <!-- Radiant Torch Flame -->
    <path d="M 0 -46 C -24 -16 -6 6 0 24 C 6 6 24 -16 0 -46 Z" fill="url(#flameGrad)"/>
    <path d="M 0 -28 C -10 -8 0 4 0 16 C 0 4 10 -8 0 -28 Z" fill="#FEF08A"/>
    <!-- Torch Holder Base -->
    <path d="M -16 24 L 16 24 L 10 50 L -10 50 Z" fill="url(#bubtGoldGrad)"/>
    <line x1="-14" y1="34" x2="14" y2="34" stroke="#78350F" stroke-width="3"/>
  </g>

  <!-- Academic Graduation Cap (Hovering Above Torch) -->
  <g transform="translate(256, 132) scale(0.82)">
    <polygon points="0,-26 56,0 0,26 -56,0" fill="#F8FAFC"/>
    <path d="M -56 0 L -56 7 L 0 33 L 56 7 L 56 0 L 0 26 Z" fill="#94A3B8"/>
    <ellipse cx="0" cy="0" rx="7" ry="5" fill="url(#bubtGoldGrad)"/>
    <path d="M 0 0 Q 38 8 42 32" fill="none" stroke="url(#bubtGoldGrad)" stroke-width="3.5"/>
  </g>

  <!-- Open Book of Knowledge (Center Base) -->
  <g transform="translate(256, 250)">
    <!-- Book Pages Canvas -->
    <path d="M 0 6 C -28 -16 -70 -14 -102 0 L -102 36 C -70 22 -28 20 0 44 C 28 20 70 22 102 36 L 102 0 C 70 -14 28 -16 0 6 Z" 
          fill="#FFFFFF"/>
    <!-- Page Texture Lines -->
    <path d="M -88 10 C -60 -1 -26 1 -4 21" stroke="#CBD5E1" stroke-width="2.5" fill="none"/>
    <path d="M 88 10 C 60 -1 26 1 4 21" stroke="#CBD5E1" stroke-width="2.5" fill="none"/>
    <path d="M -88 21 C -60 10 -26 12 -4 32" stroke="#CBD5E1" stroke-width="2.5" fill="none"/>
    <path d="M 88 21 C 60 10 26 12 4 32" stroke="#CBD5E1" stroke-width="2.5" fill="none"/>
    <!-- Gold Spine Divider -->
    <line x1="0" y1="6" x2="0" y2="44" stroke="url(#bubtGoldGrad)" stroke-width="4"/>
  </g>

  <!-- Prominent BUBT Bold Monogram -->
  <text x="256" y="340" font-family="'Inter', 'Impact', 'Arial Black', sans-serif" font-size="46" font-weight="900" 
        fill="url(#bubtGoldGrad)" text-anchor="middle" letter-spacing="6">
    BUBT
  </text>
  <text x="256" y="364" font-family="'Inter', 'Segoe UI', sans-serif" font-size="12" font-weight="800" 
        fill="#94A3B8" text-anchor="middle" letter-spacing="2.5">
    IN PURSUIT OF EXCELLENCE
  </text>
</svg>
"""

# ==============================================================================
# 3. GOOGLE CLASSROOM OFFICIAL-SPEC LOGO
# ==============================================================================
# Pixel-perfect reproduction of Google Classroom's official icon:
# Rounded chalkboard with warm amber/yellow frame border, green board surface,
# white teacher center silhouette, and two translucent student silhouettes.
GOOGLE_CLASSROOM_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Classroom Board Green -->
    <linearGradient id="boardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E8E3E"/>
      <stop offset="100%" stop-color="#137333"/>
    </linearGradient>

    <!-- Outer Frame Gold/Yellow -->
    <linearGradient id="frameGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F9AB00"/>
      <stop offset="100%" stop-color="#E37400"/>
    </linearGradient>

    <!-- Drop Shadow -->
    <filter id="gcShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#062812" flood-opacity="0.40"/>
    </filter>
  </defs>

  <!-- Outer Board Frame -->
  <rect x="36" y="56" width="440" height="400" rx="48" fill="url(#frameGrad)" filter="url(#gcShadow)"/>
  <rect x="42" y="62" width="428" height="388" rx="42" fill="#F29900"/>

  <!-- Inner Chalkboard -->
  <rect x="64" y="84" width="384" height="344" rx="28" fill="url(#boardGrad)"/>

  <!-- White Teacher (Center Figure) -->
  <g fill="#FFFFFF">
    <!-- Teacher Head -->
    <circle cx="256" cy="182" r="38"/>
    <!-- Teacher Torso -->
    <path d="M 188 322 C 188 266 218 244 256 244 C 294 244 324 266 324 322 Z"/>
  </g>

  <!-- Left Student (Translucent Silhouette) -->
  <g fill="#FFFFFF" opacity="0.82">
    <!-- Head -->
    <circle cx="154" cy="216" r="28"/>
    <!-- Torso -->
    <path d="M 106 322 C 106 278 128 262 154 262 C 172 262 188 270 196 286 C 190 296 188 308 188 322 Z"/>
  </g>

  <!-- Right Student (Translucent Silhouette) -->
  <g fill="#FFFFFF" opacity="0.82">
    <!-- Head -->
    <circle cx="358" cy="216" r="28"/>
    <!-- Torso -->
    <path d="M 324 322 C 324 308 322 296 316 286 C 324 270 340 262 358 262 C 384 262 406 278 406 322 Z"/>
  </g>

  <!-- Chalk Tray / Eraser Accent -->
  <rect x="96" y="396" width="68" height="8" rx="4" fill="#FFFFFF" opacity="0.6"/>
  <rect x="180" y="396" width="36" height="8" rx="4" fill="#FDE293" opacity="0.85"/>
</svg>
"""

# ==============================================================================
# 4. YOUTUBE OFFICIAL-SPEC LOGO
# ==============================================================================
# Precision-crafted YouTube badge conforming to official brand geometry:
# Rounded rectangle with authentic curve profiles and optical center play triangle.
YOUTUBE_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- YouTube Red Gradient -->
    <linearGradient id="ytRedGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FF0000"/>
      <stop offset="100%" stop-color="#E60000"/>
    </linearGradient>

    <!-- Drop Shadow -->
    <filter id="ytShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#4A0000" flood-opacity="0.42"/>
    </filter>
  </defs>

  <!-- Official-Spec Pill Canvas -->
  <path d="M 480 172 C 475 128 440 93 396 88 C 348 80 256 80 256 80 C 256 80 164 80 116 88 C 72 93 37 128 32 172 C 24 218 24 256 24 256 C 24 256 24 294 32 340 C 37 384 72 419 116 424 C 164 432 256 432 256 432 C 256 432 348 432 396 424 C 440 419 475 384 480 340 C 488 294 488 256 488 256 C 488 256 488 218 480 172 Z" 
        fill="url(#ytRedGrad)" filter="url(#ytShadow)"/>

  <!-- Subtle Top Highlight Sheen -->
  <path d="M 480 172 C 475 128 440 93 396 88 C 348 80 256 80 256 80 C 256 80 164 80 116 88 C 72 93 37 128 32 172 C 30 183 28 196 27 210 C 130 190 380 190 485 210 C 484 196 482 183 480 172 Z" 
        fill="#FFFFFF" opacity="0.12"/>

  <!-- Centered White Play Triangle with Soft Rounded Corners -->
  <polygon points="214,178 348,256 214,334" fill="#FFFFFF"/>
</svg>
"""

# ==============================================================================
# 5. NAVIGATION ICONS (Modern, Clean 24x24 Vector SVGs)
# ==============================================================================
# Professional 24x24 duotone icons styled with 2px stroke, round caps/joins.

NAV_DASHBOARD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect x="3" y="3" width="8" height="9" rx="2.5" fill="#6366F1" fill-opacity="0.2" stroke="#6366F1" stroke-width="2"/>
  <rect x="13" y="3" width="8" height="5" rx="2.5" fill="#818CF8" stroke="#818CF8" stroke-width="2"/>
  <rect x="13" y="10" width="8" height="11" rx="2.5" fill="#6366F1" fill-opacity="0.2" stroke="#6366F1" stroke-width="2"/>
  <rect x="3" y="14" width="8" height="7" rx="2.5" fill="#818CF8" stroke="#818CF8" stroke-width="2"/>
</svg>"""

NAV_ROUTINE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect x="3" y="4" width="18" height="17" rx="3" stroke="#6366F1" stroke-width="2"/>
  <path d="M 3 9 L 21 9" stroke="#6366F1" stroke-width="2"/>
  <line x1="8" y1="2" x2="8" y2="5" stroke="#818CF8" stroke-width="2" stroke-linecap="round"/>
  <line x1="16" y1="2" x2="16" y2="5" stroke="#818CF8" stroke-width="2" stroke-linecap="round"/>
  <circle cx="8" cy="13" r="1.5" fill="#38BDF8"/>
  <circle cx="12" cy="13" r="1.5" fill="#818CF8"/>
  <circle cx="16" cy="13" r="1.5" fill="#818CF8"/>
  <circle cx="8" cy="17" r="1.5" fill="#818CF8"/>
  <circle cx="12" cy="17" r="1.5" fill="#38BDF8"/>
  <circle cx="16" cy="17" r="1.5" fill="#10B981"/>
</svg>"""

NAV_EXAMS_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <rect x="4" y="4" width="16" height="17" rx="3" stroke="#F59E0B" stroke-width="2"/>
  <path d="M 9 2 L 15 2 C 15.6 2 16 2.4 16 3 L 16 5 C 16 5.6 15.6 6 15 6 L 9 6 C 8.4 6 8 5.6 8 5 L 8 3 C 8 2.4 8.4 2 9 2 Z" fill="#F59E0B"/>
  <path d="M 8 11 L 12 11" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
  <path d="M 8 15 L 16 15" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
  <path d="M 8 18 L 14 18" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
  <circle cx="15.5" cy="11" r="1.5" fill="#10B981"/>
</svg>"""

NAV_FACULTY_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <circle cx="12" cy="8" r="4" stroke="#10B981" stroke-width="2"/>
  <path d="M 4 20 C 4 16 7.5 13.5 12 13.5 C 16.5 13.5 20 16 20 20" stroke="#10B981" stroke-width="2" stroke-linecap="round"/>
  <!-- Academic Mortarboard Tiny Cap -->
  <path d="M 12 2 L 18 5 L 12 8 L 6 5 Z" fill="#34D399"/>
</svg>"""

NAV_LEARNING_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <!-- Glowing Bulb / Idea Rocket -->
  <path d="M 12 2 C 15.5 5 19 8.5 19 14 C 19 18 16 21 12 22 C 8 21 5 18 5 14 C 5 8.5 8.5 5 12 2 Z" 
        fill="#EC4899" fill-opacity="0.18" stroke="#EC4899" stroke-width="2"/>
  <circle cx="12" cy="11" r="2.5" fill="#F43F5E"/>
  <path d="M 9 17 C 10.5 16 13.5 16 15 17" stroke="#FDA4AF" stroke-width="2" stroke-linecap="round"/>
</svg>"""

NAV_SETTINGS_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <circle cx="12" cy="12" r="3.2" stroke="#94A3B8" stroke-width="2"/>
  <path d="M 12 2 L 12 4.5 M 12 19.5 L 12 22 M 2 12 L 4.5 12 M 19.5 12 L 22 12 M 4.9 4.9 L 6.7 6.7 M 17.3 17.3 L 19.1 19.1 M 4.9 19.1 L 6.7 17.3 M 17.3 6.7 L 19.1 4.9" 
        stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
</svg>"""

# ==============================================================================
# 6. ACTION & STATUS ICONS
# ==============================================================================
CLOCK_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <circle cx="12" cy="12" r="9" stroke="#818CF8" stroke-width="2"/>
  <path d="M 12 7 L 12 12 L 15.5 14" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
</svg>"""

THEME_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <circle cx="12" cy="12" r="9" stroke="#FBBF24" stroke-width="2"/>
  <path d="M 12 3 A 9 9 0 0 1 12 21 Z" fill="#FBBF24"/>
</svg>"""

SPARKLES_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <path d="M 12 2 L 14 8 L 20 10 L 14 12 L 12 18 L 10 12 L 4 10 L 10 8 Z" fill="#38BDF8"/>
  <circle cx="18" cy="18" r="2" fill="#F472B6"/>
</svg>"""


def render_svg_to_image(svg_content: str, width: int, height: int) -> QImage:
    """Renders an SVG string to a high-DPI QImage with full antialiasing."""
    renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter)
    painter.end()
    return image


def save_multi_size_ico(svg_content: str, ico_path: str):
    """Saves a multi-resolution Windows ICO file (256x256 high-res)."""
    img256 = render_svg_to_image(svg_content, 256, 256)
    img256.save(ico_path, "ICO")
    print(f"Generated multi-res icon: {ico_path}")


def main():
    print("Beginning high-resolution vector and raster asset generation...")

    # Dictionary of all SVG files to write
    svg_map = {
        # Core logos
        os.path.join(LOGOS_DIR, "classmate_logo.svg"): CLASSMATE_APP_LOGO_SVG,
        os.path.join(LOGOS_DIR, "bubt_logo.svg"): BUBT_LOGO_SVG,
        os.path.join(LOGOS_DIR, "google_classroom_logo.svg"): GOOGLE_CLASSROOM_LOGO_SVG,
        os.path.join(LOGOS_DIR, "youtube_logo.svg"): YOUTUBE_LOGO_SVG,
        # Navigation icons
        os.path.join(ICONS_DIR, "nav_dashboard.svg"): NAV_DASHBOARD_SVG,
        os.path.join(ICONS_DIR, "nav_routine.svg"): NAV_ROUTINE_SVG,
        os.path.join(ICONS_DIR, "nav_exams.svg"): NAV_EXAMS_SVG,
        os.path.join(ICONS_DIR, "nav_faculty.svg"): NAV_FACULTY_SVG,
        os.path.join(ICONS_DIR, "nav_learning.svg"): NAV_LEARNING_SVG,
        os.path.join(ICONS_DIR, "nav_settings.svg"): NAV_SETTINGS_SVG,
        # Utility icons
        os.path.join(ICONS_DIR, "icon_clock.svg"): CLOCK_ICON_SVG,
        os.path.join(ICONS_DIR, "icon_theme.svg"): THEME_ICON_SVG,
        os.path.join(ICONS_DIR, "icon_sparkles.svg"): SPARKLES_ICON_SVG,
    }

    # Write SVGs
    for path, content in svg_map.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Wrote SVG: {path}")

    # Render PNGs and ICOs
    # 1. ClassMate Main App Logo
    app_img_512 = render_svg_to_image(CLASSMATE_APP_LOGO_SVG, 512, 512)
    app_img_512.save(os.path.join(LOGOS_DIR, "classmate_logo.png"), "PNG")
    app_img_256 = render_svg_to_image(CLASSMATE_APP_LOGO_SVG, 256, 256)
    app_img_256.save(os.path.join(ICONS_DIR, "app_icon_256.png"), "PNG")
    app_img_128 = render_svg_to_image(CLASSMATE_APP_LOGO_SVG, 128, 128)
    app_img_128.save(os.path.join(ICONS_DIR, "app_icon_128.png"), "PNG")
    app_img_64 = render_svg_to_image(CLASSMATE_APP_LOGO_SVG, 64, 64)
    app_img_64.save(os.path.join(ICONS_DIR, "app_icon_64.png"), "PNG")
    app_img_32 = render_svg_to_image(CLASSMATE_APP_LOGO_SVG, 32, 32)
    app_img_32.save(os.path.join(ICONS_DIR, "app_icon_32.png"), "PNG")
    save_multi_size_ico(CLASSMATE_APP_LOGO_SVG, os.path.join(ICONS_DIR, "app_icon.ico"))

    # 2. BUBT Logo PNGs
    bubt_img_512 = render_svg_to_image(BUBT_LOGO_SVG, 512, 512)
    bubt_img_512.save(os.path.join(LOGOS_DIR, "bubt_logo.png"), "PNG")
    bubt_img_128 = render_svg_to_image(BUBT_LOGO_SVG, 128, 128)
    bubt_img_128.save(os.path.join(LOGOS_DIR, "bubt_logo_128.png"), "PNG")

    # 3. Google Classroom Logo PNGs
    gc_img_512 = render_svg_to_image(GOOGLE_CLASSROOM_LOGO_SVG, 512, 512)
    gc_img_512.save(os.path.join(LOGOS_DIR, "google_classroom_logo.png"), "PNG")
    gc_img_64 = render_svg_to_image(GOOGLE_CLASSROOM_LOGO_SVG, 64, 64)
    gc_img_64.save(os.path.join(LOGOS_DIR, "google_classroom_logo_64.png"), "PNG")

    # 4. YouTube Logo PNGs
    yt_img_512 = render_svg_to_image(YOUTUBE_LOGO_SVG, 512, 512)
    yt_img_512.save(os.path.join(LOGOS_DIR, "youtube_logo.png"), "PNG")
    yt_img_64 = render_svg_to_image(YOUTUBE_LOGO_SVG, 64, 64)
    yt_img_64.save(os.path.join(LOGOS_DIR, "youtube_logo_64.png"), "PNG")

    # 5. Nav Icons PNGs (48x48 for crisp high-DPI scaling)
    nav_icons = {
        "nav_dashboard": NAV_DASHBOARD_SVG,
        "nav_routine": NAV_ROUTINE_SVG,
        "nav_exams": NAV_EXAMS_SVG,
        "nav_faculty": NAV_FACULTY_SVG,
        "nav_learning": NAV_LEARNING_SVG,
        "nav_settings": NAV_SETTINGS_SVG,
        "icon_clock": CLOCK_ICON_SVG,
        "icon_theme": THEME_ICON_SVG,
        "icon_sparkles": SPARKLES_ICON_SVG,
    }
    for name, svg_code in nav_icons.items():
        img = render_svg_to_image(svg_code, 48, 48)
        img.save(os.path.join(ICONS_DIR, f"{name}.png"), "PNG")

    print("All vector and raster assets successfully generated!")


if __name__ == "__main__":
    main()
