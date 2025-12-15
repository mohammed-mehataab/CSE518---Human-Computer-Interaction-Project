"""
Virtual Mouse with Hand Gesture Recognition & Voice Commands
============================================================

A touchless virtual mouse for macOS that combines:
- MediaPipe hand gesture recognition for cursor control
- Speech recognition for voice commands
- Real-time processing with OpenCV
- Accessibility features for disabled users

Author: AI Assistant
Date: December 2025
Version: 2.0

Features:
- Hand gesture detection with 21 landmark points
- Pinch detection for clicks and dragging
- Scroll detection with peace sign (2 fingers)
- Voice commands (25+ commands supported)
- Background voice listening (non-blocking)
- macOS-specific shortcuts
- Configurable thresholds
- Error handling for microphone/camera loss

Dependencies:
- opencv-python
- mediapipe
- numpy
- pyautogui
- speech_recognition
- pyaudio
- pillow
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import os
import math
from datetime import datetime
import threading
import speech_recognition as sr
import sys
import warnings
import subprocess
from PIL import ImageGrab


# ============================================================================
# SUPPRESS WARNINGS
# ============================================================================
warnings.filterwarnings("ignore")


# ============================================================================
# FLAC SETUP FOR MACOS (CRITICAL FOR APPLE SILICON)
# ============================================================================
def setup_flac_for_macos():
    """
    Set up FLAC binary for macOS speech recognition.
    
    FLAC is required by speech_recognition to encode audio for Google API.
    This function locates the system FLAC installation via Homebrew.
    
    Returns:
        bool: True if FLAC setup successful, False otherwise
    """
    try:
        # Get the system FLAC binary installed via Homebrew
        flac_path = subprocess.check_output(["which", "flac"]).decode().strip()
        
        # Override the speech_recognition FLAC converter
        import speech_recognition.audio as sr_audio
        original_get_flac = sr_audio.get_flac_converter
        sr_audio.get_flac_converter = lambda: flac_path
        
        print(f"✓ [Voice] FLAC binary found: {flac_path}")
        return True
        
    except subprocess.CalledProcessError:
        print("⚠ [Voice] WARNING: 'flac' not found in PATH")
        print("  Install with: brew install flac")
        print("  Or use: arch -arm64 brew install flac (Apple Silicon)")
        print("  Voice commands may not work without FLAC binary")
        return False
        
    except Exception as e:
        print(f"⚠ [Voice] Warning setting up FLAC: {e}")
        return False


# Call FLAC setup
FLAC_AVAILABLE = setup_flac_for_macos()


# ============================================================================
# CONFIGURATION
# ============================================================================
try:
    from config import (  # type: ignore
        CAMERA_INDEX,
        CAMERA_WIDTH,
        CAMERA_HEIGHT,
        MIN_DETECTION_CONFIDENCE,
        MIN_TRACKING_CONFIDENCE,
        SMOOTHING_FACTOR,
        FRAME_REDUCTION,
        PINCH_THRESHOLD,
    )
    print("✓ [Config] Loaded custom configuration from config.py")
except ImportError:
    # Default configuration
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.7
    SMOOTHING_FACTOR = 6
    FRAME_REDUCTION = 80
    PINCH_THRESHOLD = 35
    print("✓ [Config] Using default configuration")


# ============================================================================
# PYAUTOGUI SAFETY SETTINGS
# ============================================================================
pyautogui.FAILSAFE = False      # No fail-safe (we handle it ourselves)
pyautogui.PAUSE = 0.05          # Small pause between actions


# ============================================================================
# VOICE COMMAND LISTENER CLASS
# ============================================================================
class VoiceCommandListener:
    """
    Listens for voice commands in a background thread.
    
    This class implements a non-blocking voice recognition system that:
    - Runs in a separate daemon thread
    - Continuously listens for voice commands
    - Validates against a whitelist of 25+ supported commands
    - Handles network errors gracefully
    - Executes macOS-specific keyboard shortcuts
    
    Attributes:
        virtual_mouse (VirtualMouseFinalEnhanced): Reference to main app
        recognizer (sr.Recognizer): Speech recognition engine
        microphone (sr.Microphone): Microphone input source
        listening (bool): Whether actively listening
        thread (threading.Thread): Background listening thread
        voice_available (bool): Whether microphone is available
    """
    
    # Define valid command keywords for filtering
    VALID_KEYWORDS = {
        # Click commands
        "click", "left click", "tap", "double click", "double tap",
        "right click", "context menu",
        # Scroll commands
        "scroll up", "scroll down",
        # Capture commands
        "screenshot", "snap", "take picture",
        # Window management
        "maximize", "max", "minimize", "min", "desktop", "show desktop",
        # Edit commands
        "undo", "redo", "copy", "paste", "cut", "select", "select all",
        # Control commands
        "enable", "disable", "hello", "hi", "hey", "activate", "start",
        "pause", "stop",
    }


    def __init__(self, virtual_mouse):
        """
        Initialize voice command listener.
        
        Args:
            virtual_mouse (VirtualMouseFinalEnhanced): Reference to main app
        """
        self.virtual_mouse = virtual_mouse
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.listening = False
        self.thread = None
        self.voice_available = False

        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            self.voice_available = True
            print("✓ [Voice] Microphone initialized successfully")
        except Exception as e:
            print(f"⚠ [Voice] Could not initialize microphone: {e}")
            print("  Voice commands will be disabled. Gesture controls still work.")


    def start(self):
        """Start listening for voice commands in background thread."""
        if not self.voice_available:
            return

        if not self.listening:
            self.listening = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("[Voice] Listener started")


    def stop(self):
        """Stop listening for voice commands."""
        self.listening = False
        print("[Voice] Listener stopped")


    def _listen_loop(self):
        """
        Background loop that continuously listens for voice commands.
        
        This loop:
        - Adjusts for ambient noise
        - Listens with timeout
        - Recognizes speech via Google Cloud API
        - Handles various error conditions gracefully
        - Validates against command whitelist
        """
        print("[Voice] Listening loop started")
        
        while self.listening:
            try:
                with self.microphone as source:
                    # Adjust noise threshold
                    try:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        # Higher energy threshold = ignore quiet sounds
                        self.recognizer.energy_threshold = 4000
                    except Exception:
                        pass

                    try:
                        # Listen with timeout
                        audio = self.recognizer.listen(
                            source, timeout=5.0, phrase_time_limit=10
                        )

                        # Try to recognize speech
                        try:
                            text = (
                                self.recognizer.recognize_google(audio)
                                .lower()
                                .strip()
                            )
                            
                            if text:  # Only process non-empty results
                                print(f"[Voice] Recognized: '{text}'")
                                self._process_command(text)
                                
                        except OSError as e:
                            # FLAC binary issue - skip this audio
                            if "Bad CPU type" in str(e) or "flac" in str(e).lower():
                                pass
                            else:
                                raise
                        except sr.UnknownValueError:
                            # Speech couldn't be understood - silently ignore
                            pass
                        except sr.RequestError as e:
                            # Network error or API issue - continue listening
                            pass
                    except sr.RequestError:
                        # Timeout waiting for speech - continue
                        pass

            except AssertionError:
                # Microphone context issue - reset
                time.sleep(0.1)
            except Exception:
                # Other errors - silently ignore
                time.sleep(0.1)


    def test_command(self, text):
        """
        Test a voice command manually (for debugging).
        
        Args:
            text (str): Command text to process
        """
        print(f"[Voice] Testing command: '{text}'")
        self._process_command(text.lower().strip())


    def _process_command(self, text):
        """
        Process recognized voice command.
        
        Flow:
        1. Validate against whitelist of valid keywords
        2. Check for specific command patterns
        3. Execute corresponding mouse action
        4. Update status display
        
        Args:
            text (str): Recognized text from speech API
        """
        text_lower = text.lower().strip()
        
        # Check if any valid keyword is in the text
        has_valid_command = any(keyword in text_lower for keyword in self.VALID_KEYWORDS)

        if not has_valid_command:
            print(f"[Voice] Ignored: '{text}' (no matching command)")
            return

        # Add small delay to ensure window focus
        time.sleep(0.1)

        print(f"[Voice] Processing: '{text}'")

        # ================================================================
        # CLICK COMMANDS (check specific patterns first to avoid conflicts)
        # ================================================================
        
        # Right click (check BEFORE "click" to avoid matching "click" in "right click")
        if "right click" in text_lower or "context menu" in text_lower:
            pyautogui.rightClick()
            self.virtual_mouse.status = "Voice: Right click"
            print("[Voice] ✓ Right click")

        # Double click (check BEFORE "click")
        elif "double click" in text_lower or "double tap" in text_lower:
            pyautogui.doubleClick()
            self.virtual_mouse.status = "Voice: Double click"
            print("[Voice] ✓ Double click")

        # Left click (check LAST)
        elif any(k in text_lower for k in ["click", "left click", "tap"]):
            pyautogui.click()
            self.virtual_mouse.status = "Voice: Left click"
            print("[Voice] ✓ Left click")

        # ================================================================
        # SCROLL COMMANDS
        # ================================================================
        
        elif "scroll up" in text_lower:
            pyautogui.scroll(5)
            self.virtual_mouse.status = "Voice: Scroll up"
            print("[Voice] ✓ Scroll up")

        elif "scroll down" in text_lower:
            pyautogui.scroll(-5)
            self.virtual_mouse.status = "Voice: Scroll down"
            print("[Voice] ✓ Scroll down")

        # ================================================================
        # SCREENSHOT COMMAND
        # ================================================================
        
        elif any(k in text_lower for k in ["screenshot", "snap", "take picture"]):
            try:
                filename = os.path.join(
                    self.virtual_mouse.screenshot_dir,
                    f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                )
                screenshot = ImageGrab.grab()
                screenshot.save(filename)
                
                if os.path.exists(filename):
                    self.virtual_mouse.status = "Voice: Screenshot saved"
                    print(f"[Voice] ✓ Screenshot saved to {filename}")
                else:
                    self.virtual_mouse.status = "Voice: Screenshot failed"
                    print("[Voice] ✗ Screenshot failed: File not saved")
            except Exception as e:
                self.virtual_mouse.status = "Voice: Screenshot failed"
                print(f"[Voice] ✗ Screenshot error: {e}")

        # ================================================================
        # ENABLE/DISABLE COMMANDS
        # ================================================================
        
        elif any(k in text_lower for k in ["enable", "start", "activate"]):
            self.virtual_mouse.mouse_enabled = True
            self.virtual_mouse.status = "Voice: Mouse enabled"
            print("[Voice] ✓ Mouse enabled")

        elif any(k in text_lower for k in ["disable", "stop", "pause"]):
            self.virtual_mouse.mouse_enabled = False
            self.virtual_mouse.status = "Voice: Mouse disabled"
            print("[Voice] ✓ Mouse disabled")

        # ================================================================
        # WINDOW MANAGEMENT COMMANDS
        # ================================================================
        
        elif "maximize" in text_lower or "max" in text_lower:
            pyautogui.hotkey("cmd", "ctrl", "f")
            self.virtual_mouse.status = "Voice: Maximize window"
            print("[Voice] ✓ Maximize window")

        elif "minimize" in text_lower or "min" in text_lower:
            pyautogui.hotkey("cmd", "m")
            self.virtual_mouse.status = "Voice: Minimize window"
            print("[Voice] ✓ Minimize window")

        elif "desktop" in text_lower or "show desktop" in text_lower:
            try:
                pyautogui.hotkey("fn", "f11")
            except:
                pyautogui.hotkey("fn", "f3")
            self.virtual_mouse.status = "Voice: Show desktop"
            print("[Voice] ✓ Show desktop")

        # ================================================================
        # EDIT COMMANDS (macOS uses Cmd, not Ctrl)
        # ================================================================
        
        elif "undo" in text_lower:
            pyautogui.hotkey("cmd", "z")
            self.virtual_mouse.status = "Voice: Undo"
            print("[Voice] ✓ Undo")

        elif "redo" in text_lower:
            pyautogui.hotkey("cmd", "shift", "z")
            self.virtual_mouse.status = "Voice: Redo"
            print("[Voice] ✓ Redo")

        elif "copy" in text_lower:
            pyautogui.hotkey("cmd", "c")
            self.virtual_mouse.status = "Voice: Copy"
            print("[Voice] ✓ Copy")

        elif "paste" in text_lower:
            pyautogui.hotkey("cmd", "v")
            self.virtual_mouse.status = "Voice: Paste"
            print("[Voice] ✓ Paste")

        elif "cut" in text_lower:
            pyautogui.hotkey("cmd", "x")
            self.virtual_mouse.status = "Voice: Cut"
            print("[Voice] ✓ Cut")

        elif "select all" in text_lower or "select everything" in text_lower:
            pyautogui.hotkey("cmd", "a")
            self.virtual_mouse.status = "Voice: Select all"
            print("[Voice] ✓ Select all")

        # ================================================================
        # GREETING COMMANDS
        # ================================================================
        
        elif any(k in text_lower for k in ["hello", "hi", "hey"]):
            self.virtual_mouse.status = "Voice: Hello!"
            print("[Voice] ✓ Greeting acknowledged")


# ============================================================================
# VIRTUAL MOUSE MAIN CLASS
# ============================================================================
class VirtualMouseFinalEnhanced:
    """
    Enhanced virtual mouse with hand gesture recognition and voice control.
    
    This class implements:
    - Real-time hand detection using MediaPipe
    - 25-landmark hand pose estimation
    - Gesture recognition (pinch, scroll, palm)
    - Cursor mapping with smoothing
    - Voice command processing
    - macOS keyboard shortcuts
    
    Attributes:
        screen_w, screen_h: Screen resolution
        cam_w, cam_h: Camera resolution
        smoothing: Cursor smoothing factor
        frame_reduction: Pixel margin from edges
        pinch_threshold: Distance threshold for click detection
        mouse_enabled: Global on/off toggle
        mp_hands: MediaPipe hand detection model
        hands: Hand detection instance
        voice_listener: Voice command listener
        status: Current status message
    """

    def __init__(self):
        """Initialize virtual mouse with all components."""
        # Screen and camera dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        self.cam_w, self.cam_h = CAMERA_WIDTH, CAMERA_HEIGHT

        # Control parameters
        self.smoothing = SMOOTHING_FACTOR
        self.frame_reduction = FRAME_REDUCTION
        self.pinch_threshold = PINCH_THRESHOLD
        self.right_click_threshold = PINCH_THRESHOLD + 5
        
        # Timing thresholds (seconds)
        self.drag_hold_time = 0.25
        self.click_cooldown = 0.25
        self.double_click_window = 0.35
        self.scroll_sensitivity = 2.8
        self.auth_hold_time = 1.0
        self.shortcut_cooldown = 1.8

        # State tracking
        self.mouse_enabled = False
        self.palm_started = None
        self.pinching = False
        self.dragging = False
        self.pinch_start = 0.0
        self.last_left_click = 0.0
        self.last_click_time = 0.0
        self.last_right_click = 0.0
        self.prev_scroll_y = None
        self.last_shortcut = 0.0
        
        # Cursor tracking
        self.prev_x = self.screen_w // 2
        self.prev_y = self.screen_h // 2
        self.status = "Show an open palm to enable"

        # Initialize MediaPipe hand detection
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        # Create screenshot directory
        self.screenshot_dir = os.path.expanduser("~/Desktop/Screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Verify directory is writable
        try:
            with open(os.path.join(self.screenshot_dir, ".write_test"), "w") as f:
                f.write(f"write ok {datetime.now().isoformat()}\n")
            print(f"✓ [App] Screenshots will save to: {self.screenshot_dir}")
        except Exception as e:
            print(f"⚠ [App] Warning: Cannot write to screenshot dir: {e}")

        # Initialize voice command listener
        self.voice_listener = VoiceCommandListener(self)
        self.voice_listener.start()
        print("✓ [App] Voice listener initialized")


    @staticmethod
    def dist(p1, p2):
        """
        Calculate Euclidean distance between two points.
        
        Args:
            p1: Tuple of (x, y) coordinates
            p2: Tuple of (x, y) coordinates
            
        Returns:
            float: Distance between points
        """
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


    @staticmethod
    def finger_up(landmarks, tip, pip):
        """
        Check if a finger is up (extended).
        
        Compares tip position (landmark) with PIP joint position.
        Finger is considered "up" if tip is above PIP.
        
        Args:
            landmarks: Hand landmarks from MediaPipe
            tip: Landmark index for finger tip
            pip: Landmark index for PIP joint
            
        Returns:
            bool: True if finger is up, False if down
        """
        return (landmarks[tip].y - landmarks[pip].y) < -0.02


    def map_to_screen(self, x, y, frame_w, frame_h):
        """
        Map camera coordinates to screen coordinates with smoothing.
        
        Steps:
        1. Interpolate camera coords to screen space
        2. Apply exponential smoothing
        3. Move cursor to smoothed position
        
        Args:
            x (float): Camera x coordinate
            y (float): Camera y coordinate
            frame_w (int): Camera frame width
            frame_h (int): Camera frame height
        """
        # Interpolate from camera space to screen space
        screen_x = np.interp(
            x,
            [self.frame_reduction, frame_w - self.frame_reduction],
            [0, self.screen_w],
        )
        screen_y = np.interp(
            y,
            [self.frame_reduction, frame_h - self.frame_reduction],
            [0, self.screen_h],
        )
        
        # Apply exponential smoothing to reduce jitter
        curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothing
        curr_y = self.prev_y + (screen_y - self.prev_y) / self.smoothing
        
        # Update position
        self.prev_x, self.prev_y = curr_x, curr_y
        pyautogui.moveTo(curr_x, curr_y)


    def handle_auth(self, fingers_up, now):
        """
        Handle authentication (palm hold for enable).
        
        Requires all 5 fingers up for AUTH_HOLD_TIME seconds.
        
        Args:
            fingers_up (dict): Finger up/down states
            now (float): Current time
        """
        if all(fingers_up.values()):
            if self.palm_started is None:
                self.palm_started = now
            elif (
                not self.mouse_enabled
                and (now - self.palm_started) >= self.auth_hold_time
            ):
                self.mouse_enabled = True
                self.status = "✓ Mouse enabled (palm hold)"
        else:
            self.palm_started = None


    def handle_scroll(self, fingers_up, middle_tip):
        """
        Handle scroll gesture (peace sign with hand motion).
        
        Peace sign = index + middle up, ring + pinky down.
        Motion = move hand up/down to scroll.
        
        Args:
            fingers_up (dict): Finger up/down states
            middle_tip (tuple): Middle finger tip position
        """
        if (
            fingers_up["index"]
            and fingers_up["middle"]
            and not fingers_up["ring"]
            and not fingers_up["pinky"]
        ):
            if self.prev_scroll_y is not None:
                delta = self.prev_scroll_y - middle_tip[1]
                if abs(delta) > 1:
                    pyautogui.scroll(int(delta * self.scroll_sensitivity))
                    self.status = "Scrolling"
            self.prev_scroll_y = middle_tip[1]
        else:
            self.prev_scroll_y = None


    def handle_clicks(self, thumb_tip, index_tip, middle_tip, now):
        """
        Handle click and drag gestures.
        
        Actions:
        - Thumb + index pinch: Left click (quick) or drag (hold)
        - Thumb + middle pinch: Right click
        
        Args:
            thumb_tip (tuple): Thumb tip position
            index_tip (tuple): Index tip position
            middle_tip (tuple): Middle tip position
            now (float): Current time
        """
        thumb_index = self.dist(thumb_tip, index_tip)
        thumb_middle = self.dist(thumb_tip, middle_tip)

        # Right click: Thumb + middle pinch
        if (
            thumb_middle < self.right_click_threshold
            and (now - self.last_right_click) > self.click_cooldown
        ):
            pyautogui.rightClick()
            self.last_right_click = now
            self.status = "Right click"
            return

        # Left click / Drag: Thumb + index pinch
        if thumb_index < self.pinch_threshold:
            if not self.pinching:
                self.pinching = True
                self.pinch_start = now
                
            # Hold pinch for DRAG_HOLD_TIME to start dragging
            if (
                self.pinching
                and not self.dragging
                and (now - self.pinch_start) >= self.drag_hold_time
            ):
                pyautogui.mouseDown()
                self.dragging = True
                self.status = "Dragging"
        else:
            # Pinch released
            if self.pinching:
                held = now - self.pinch_start
                
                if self.dragging:
                    # Release drag
                    pyautogui.mouseUp()
                    self.status = "Drag released"
                elif (
                    held < self.drag_hold_time
                    and (now - self.last_left_click) > self.click_cooldown
                ):
                    # Quick pinch = click
                    if (now - self.last_click_time) <= self.double_click_window:
                        # Double click
                        pyautogui.doubleClick()
                        self.status = "Double click"
                        self.last_click_time = 0.0
                    else:
                        # Single click
                        pyautogui.click()
                        self.status = "Left click"
                        self.last_click_time = now
                    self.last_left_click = now
                    
                self.pinching = False
                self.dragging = False


    def handle_shortcuts(self, fingers_up, thumb_up, now):
        """
        Handle special gesture shortcuts.
        
        Shortcuts:
        - 3 fingers up (index, middle, ring), thumb + pinky down: Screenshot
        - 4 fingers up (all but thumb): Show desktop
        - 5 fingers up while enabled: Maximize
        
        Args:
            fingers_up (dict): Finger up/down states
            thumb_up (bool): Thumb state
            now (float): Current time
        """
        if (now - self.last_shortcut) < self.shortcut_cooldown:
            return

        # Screenshot: index + middle + ring up, pinky down, thumb down
        if (
            fingers_up["index"]
            and fingers_up["middle"]
            and fingers_up["ring"]
            and not fingers_up["pinky"]
            and not thumb_up
        ):
            try:
                filename = os.path.join(
                    self.screenshot_dir,
                    f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                )
                screenshot = ImageGrab.grab()
                screenshot.save(filename)
                
                if os.path.exists(filename):
                    print(f"✓ [Gesture] Screenshot: {filename}")
                    self.status = "Screenshot saved"
                else:
                    self.status = "Screenshot failed"
            except Exception as e:
                print(f"✗ [Gesture] Screenshot error: {e}")
                self.status = "Screenshot failed"
            self.last_shortcut = now
            return

        # Show desktop: four fingers up, thumb down
        if (
            fingers_up["index"]
            and fingers_up["middle"]
            and fingers_up["ring"]
            and fingers_up["pinky"]
            and not thumb_up
        ):
            pyautogui.hotkey("fn", "f11")
            self.status = "Show desktop"
            self.last_shortcut = now
            return

        # Maximize: all five up while enabled
        if all(fingers_up.values()) and self.mouse_enabled:
            pyautogui.hotkey("cmd", "ctrl", "f")
            self.status = "Maximize window"
            self.last_shortcut = now


    def reset_on_loss(self):
        """Reset state when hand is lost from view."""
        if self.dragging:
            pyautogui.mouseUp()
        self.pinching = False
        self.dragging = False
        self.prev_scroll_y = None
        self.status = "Show your hand to the camera"


    def draw_overlay(self, frame):
        """
        Draw status overlay on video frame.
        
        Shows:
        - Key bindings
        - Mouse on/off status
        - Voice on/off status
        - Current action status
        
        Args:
            frame (np.ndarray): OpenCV frame to draw on
        """
        # Instructions
        cv2.putText(
            frame,
            "Palm to enable | M toggle | V voice | Q quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        
        # Mouse status
        color = (0, 200, 0) if self.mouse_enabled else (0, 0, 200)
        cv2.putText(
            frame,
            f"Mouse: {'ON' if self.mouse_enabled else 'OFF'}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )
        
        # Voice status
        voice_color = (0, 200, 0) if self.voice_listener.listening else (0, 0, 200)
        cv2.putText(
            frame,
            f"Voice: {'ON' if self.voice_listener.listening else 'OFF'}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            voice_color,
            2,
        )
        
        # Action status
        cv2.putText(
            frame,
            f"Status: {self.status}",
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (220, 220, 220),
            2,
        )


    def run(self):
        """
        Main application loop.
        
        Steps:
        1. Capture video frame from camera
        2. Detect hand landmarks with MediaPipe
        3. Extract finger positions
        4. Process gestures and execute actions
        5. Handle keyboard input
        6. Draw overlay and display
        """
        # Initialize camera
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)

        # Print instructions
        print("=" * 70)
        print("Virtual Mouse - Enhanced Natural Gestures + Voice Commands")
        print("=" * 70)
        print("\n📌 GESTURE CONTROLS:")
        print("  • Index finger = Move cursor")
        print("  • Pinch (thumb+index) = Click/Double/Drag")
        print("  • Pinch (thumb+middle) = Right-click")
        print("  • Peace sign (2 fingers) = Scroll up/down")
        print("  • 3 fingers up = Screenshot")
        print("  • 4 fingers up = Show desktop")
        print("  • 5 fingers up (hold 1s) = Enable/Maximize")
        print("\n🎤 VOICE COMMANDS:")
        print("  • 'click', 'right click', 'scroll up/down'")
        print("  • 'screenshot', 'maximize', 'minimize'")
        print("  • 'copy', 'paste', 'undo', 'redo'")
        print("  • 'enable'/'disable' mouse control")
        print("\n⌨️  KEYBOARD SHORTCUTS:")
        print("  • M = Toggle mouse enable/disable")
        print("  • V = Toggle voice commands")
        print("  • S = Manual screenshot test")
        print("  • Q = Quit application")
        print("=" * 70 + "\n")

        # Main loop
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Camera not available")
                break

            # Flip frame horizontally for selfie view
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            now = time.time()

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)
                lm = hand.landmark
                h, w, _ = frame.shape

                # Extract finger tip positions
                tips = {
                    "thumb": (int(lm[4].x * w), int(lm[4].y * h)),
                    "index": (int(lm[8].x * w), int(lm[8].y * h)),
                    "middle": (int(lm[12].x * w), int(lm[12].y * h)),
                }

                # Determine which fingers are up/down
                fingers_up = {
                    "thumb": self.finger_up(lm, 4, 3),
                    "index": self.finger_up(lm, 8, 6),
                    "middle": self.finger_up(lm, 12, 10),
                    "ring": self.finger_up(lm, 16, 14),
                    "pinky": self.finger_up(lm, 20, 18),
                }

                # Check for enable/disable (palm hold)
                self.handle_auth(fingers_up, now)

                # Process actions if mouse is enabled
                if self.mouse_enabled:
                    # Move cursor
                    self.map_to_screen(tips["index"][0], tips["index"][1], w, h)
                    
                    # Handle scroll
                    self.handle_scroll(fingers_up, tips["middle"])
                    
                    # Handle clicks if not scrolling
                    if self.prev_scroll_y is None:
                        self.handle_clicks(
                            tips["thumb"], tips["index"], tips["middle"], now
                        )
                    
                    # Handle shortcut gestures
                    self.handle_shortcuts(fingers_up, fingers_up["thumb"], now)
                else:
                    self.status = "Mouse paused - show palm or press M"
                    self.pinching = False
                    self.dragging = False
                    self.prev_scroll_y = None
            else:
                # Hand lost from view
                self.reset_on_loss()

            # Draw overlay
            self.draw_overlay(frame)
            
            # Display frame
            cv2.imshow("Virtual Mouse - Enhanced", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("q"):
                # Quit
                if self.dragging:
                    pyautogui.mouseUp()
                self.voice_listener.stop()
                print("\n✓ Application closed by user")
                break
                
            if key == ord("m"):
                # Toggle mouse enable/disable
                self.mouse_enabled = not self.mouse_enabled
                self.status = "✓ Mouse enabled" if self.mouse_enabled else "Mouse paused"
                self.pinching = False
                self.dragging = False
                self.prev_scroll_y = None
                print(f"[Input] Mouse: {self.status}")
                
            if key == ord("v"):
                # Toggle voice commands
                if not self.voice_listener.voice_available:
                    self.status = "Voice not available - install PyAudio"
                elif self.voice_listener.listening:
                    self.voice_listener.stop()
                    self.status = "Voice commands disabled"
                    print("[Input] Voice disabled")
                else:
                    self.voice_listener.start()
                    self.status = "Voice commands enabled"
                    print("[Input] Voice enabled")
                    
            if key == ord("s"):
                # Manual screenshot test
                fname = os.path.join(
                    self.screenshot_dir,
                    f"screenshot_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                )
                try:
                    img = ImageGrab.grab()
                    img.save(fname)
                    print(f"✓ [Input] Screenshot saved: {fname}")
                except Exception as e:
                    print(f"✗ [Input] Screenshot failed: {e}")

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        try:
            self.hands.close()
        except Exception:
            pass


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        print("\n" + "=" * 70)
        print("VIRTUAL MOUSE - Starting Application")
        print("=" * 70)
        VirtualMouseFinalEnhanced().run()
    except KeyboardInterrupt:
        print("\n✓ Application closed by user (Ctrl+C)")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure proper cleanup
        try:
            import atexit
            atexit._run_exitfuncs()
        except Exception:
            pass
        print("\nGoodbye!\n")
