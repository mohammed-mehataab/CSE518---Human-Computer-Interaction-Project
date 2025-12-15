"""
Enhanced Configuration File for Virtual Mouse
==============================================

This file allows you to customize various parameters without modifying
the main application code. Copy this file to the same directory as
virtual_mouse.py and adjust values as needed.

All parameters have sensible defaults - modify only what you need.
"""

# ============================================================================
# CAMERA SETTINGS
# ============================================================================

# Camera index (0 = built-in/default, 1 = external USB camera, etc.)
# To find your camera: python -c "import cv2; cv2.VideoCapture(0).isOpened()"
CAMERA_INDEX = 0

# Camera resolution (width x height)
# Higher = better detection but more CPU usage
# Typical: 640x480, 1280x720
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


# ============================================================================
# MEDIAPIPE DETECTION SETTINGS
# ============================================================================

# Minimum confidence (0.0-1.0) for hand detection
# Higher = stricter, fewer false positives but may miss hands
# Recommended: 0.6-0.8 (0.7 is balanced)
MIN_DETECTION_CONFIDENCE = 0.7

# Minimum confidence for hand tracking between frames
# Higher = smoother tracking but may lose hand more easily
# Recommended: 0.5-0.8
MIN_TRACKING_CONFIDENCE = 0.7


# ============================================================================
# CURSOR MOVEMENT SETTINGS
# ============================================================================

# Smoothing factor for cursor movement (reduces jitter)
# Higher = smoother but less responsive
# Lower = snappier but more jittery
# Range: 3-10 (default: 6)
SMOOTHING_FACTOR = 6

# Frame reduction: pixels to exclude from edges
# Prevents accidental clicks at screen edges
# Range: 40-120 (default: 80)
FRAME_REDUCTION = 80


# ============================================================================
# GESTURE DETECTION THRESHOLDS
# ============================================================================

# Distance in pixels for pinch detection (left-click)
# Lower = easier to trigger, Higher = harder to trigger
# Range: 20-50 (default: 35)
PINCH_THRESHOLD = 35

# Distance for right-click (thumb + middle pinch)
# Usually = PINCH_THRESHOLD + 5 (don't modify unless needed)
RIGHT_CLICK_THRESHOLD = PINCH_THRESHOLD + 5


# ============================================================================
# TIMING THRESHOLDS (all in seconds)
# ============================================================================

# Time to hold pinch for drag (quick pinch = click, long pinch = drag)
DRAG_HOLD_TIME = 0.25

# Minimum time between clicks (prevents accidental double-clicks)
CLICK_COOLDOWN = 0.25

# Time window for recognizing double-click
DOUBLE_CLICK_WINDOW = 0.35

# Scroll sensitivity multiplier
SCROLL_SENSITIVITY = 2.8

# Time to hold open palm (all 5 fingers) to enable mouse
AUTH_HOLD_TIME = 1.0

# Cooldown between shortcut gestures
SHORTCUT_COOLDOWN = 1.8


# ============================================================================
# VOICE RECOGNITION SETTINGS
# ============================================================================

# Energy threshold for microphone (higher = ignore quiet sounds)
# Default: 4000
# Increase if picking up too much background noise
# Decrease if not picking up speech
VOICE_ENERGY_THRESHOLD = 4000

# Ambient noise adjustment duration (seconds)
# Higher = better noise filtering but slower startup
VOICE_NOISE_DURATION = 0.5

# Voice listening timeout (seconds)
VOICE_LISTEN_TIMEOUT = 5.0

# Maximum phrase duration (seconds)
VOICE_PHRASE_TIME_LIMIT = 10
