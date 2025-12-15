# Troubleshooting & Advanced Usage Guide

## 🔧 Installation Issues

### Issue: "ModuleNotFoundError: No module named 'cv2'"

**Problem:** OpenCV not installed  
**Solution:**
```bash
pip install opencv-python
```

### Issue: "ModuleNotFoundError: No module named 'mediapipe'"

**Problem:** MediaPipe not installed  
**Solution:**
```bash
pip install mediapipe
```

### Issue: PyAudio installation fails on Apple Silicon

**Problem:** PyAudio can't find PortAudio headers  
**Solution:**
```bash
# Install PortAudio
brew install portaudio

# Link it
brew link portaudio

# Install PyAudio with explicit paths (Apple Silicon)
arch -arm64 pip install --no-cache-dir --global-option='build_ext' \
  --global-option='-I/opt/homebrew/include' \
  --global-option='-L/opt/homebrew/lib' pyaudio==0.2.11

# For Intel Macs, just use:
pip install pyaudio
```

### Issue: "ERROR: Bad CPU type in executable"

**Problem:** FLAC binary incompatibility  
**Solution:**
```bash
# Remove old FLAC
brew uninstall flac

# Reinstall via Homebrew
brew install flac

# Verify installation
which flac
echo $?  # Should output 0 if successful
```

### Issue: "OSError: [Errno 24] Too many open files"

**Problem:** Resource limit exceeded  
**Solution:**
```bash
# Check current limit
ulimit -n

# Increase limit temporarily
ulimit -n 4096

# Make permanent (add to ~/.zshrc or ~/.bash_profile)
echo "ulimit -n 4096" >> ~/.zshrc
source ~/.zshrc
```

---

## 🎤 Voice Recognition Issues

### Issue: Voice commands not recognized

**Cause:** Background noise or quiet speech  
**Solution:**
```python
# In config.py, increase energy threshold:
VOICE_ENERGY_THRESHOLD = 5000  # Was 4000

# Speak more clearly and loudly
# Use quiet environment without background noise
```

### Issue: "No module named 'pyaudio'"

**Problem:** PyAudio not installed or installation failed  
**Solution:**
```bash
# Verify installation
python -c "import pyaudio; print('PyAudio OK')"

# If fails, reinstall with full output
pip install --verbose pyaudio

# Check Homebrew portaudio
brew list portaudio
```

### Issue: Microphone permission denied on macOS

**Problem:** Application doesn't have microphone access  
**Solution:**
1. Open **System Preferences**
2. Go to **Security & Privacy**
3. Click **Microphone** in sidebar
4. Find **Terminal** (or Python) and enable access
5. Restart the application

### Issue: "All backends for transcription are unavailable"

**Problem:** Network issue or Google Speech API unavailable  
**Solution:**
```bash
# Check internet connection
ping -c 1 8.8.8.8

# Restart router if needed
# Google Speech API may be temporarily unavailable
# Try again in a few minutes
```

### Issue: Voice commands execute wrong actions

**Problem:** Speech recognition is inaccurate  
**Solution:**
```python
# Debug by testing specific commands:
from virtual_mouse import VoiceCommandListener, VirtualMouseFinalEnhanced

app = VirtualMouseFinalEnhanced()
listener = app.voice_listener

# Test recognized text directly
listener.test_command("click")
listener.test_command("scroll up")

# Check if microphone is working
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something...")
    audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
    except:
        print("Could not recognize speech")
```

---

## 🎮 Gesture Recognition Issues

### Issue: Hand not detected at all

**Cause:** Poor lighting or camera issues  
**Solution:**
```python
# 1. Check camera works
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"

# 2. Improve lighting (natural light is best)
# 3. Adjust detection confidence (make it more lenient)
# In config.py:
MIN_DETECTION_CONFIDENCE = 0.5  # Was 0.7 (more lenient)

# 4. Check distance from camera (60-90cm optimal)
# 5. Ensure good contrast (plain background)
```

### Issue: Cursor jitters excessively

**Cause:** Hand position noise or low smoothing  
**Solution:**
```python
# In config.py:
SMOOTHING_FACTOR = 10  # Was 6 (higher = smoother)
FRAME_REDUCTION = 120  # Was 80 (exclude more edges)

# Reduce camera resolution
CAMERA_WIDTH = 480  # Was 640
CAMERA_HEIGHT = 360  # Was 480
```

### Issue: Clicks not triggering

**Cause:** Pinch threshold too sensitive  
**Solution:**
```python
# In config.py:
PINCH_THRESHOLD = 45  # Was 35 (harder to trigger)

# Or make it easier:
PINCH_THRESHOLD = 25  # Much easier to trigger
```

### Issue: Can't perform drag operations

**Cause:** Hand position not stable during drag or low frame rate  
**Solution:**
```python
# 1. Hold hand more steadily
# 2. Increase drag hold time
# In config.py:
DRAG_HOLD_TIME = 0.35  # Was 0.25 (hold longer before drag starts)

# 3. Increase smoothing
SMOOTHING_FACTOR = 8  # Was 6
```

### Issue: Wrong camera selected

**Solution:**
```bash
# Find available cameras
python << 'EOF'
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
    else:
        print(f"Camera {i}: Not available")
EOF

# Update config.py with correct camera index
CAMERA_INDEX = 1  # If external USB camera is index 1
```

---

## ⚙️ Advanced Customization

### Custom Voice Commands

To add your own voice commands, modify the `_process_command` method in `virtual_mouse.py`:

```python
# Example: Add "browser" command to open browser
elif "browser" in text_lower:
    pyautogui.hotkey("cmd", "shift", "b")  # macOS Safari shortcut
    self.virtual_mouse.status = "Voice: Browser"
    print("[Voice] ✓ Opened browser")

# Example: Add "email" command
elif "email" in text_lower:
    pyautogui.hotkey("cmd", "1")  # Gmail in browser
    self.virtual_mouse.status = "Voice: Email"
    print("[Voice] ✓ Opened email")
```

### Custom Gesture Mappings

To add new gestures, add methods to the `VirtualMouseFinalEnhanced` class:

```python
def handle_custom_gesture(self, fingers_up, now):
    """
    Example: Three-finger swipe for app switcher
    """
    if (fingers_up["index"] and fingers_up["middle"] and fingers_up["ring"] 
        and not fingers_up["pinky"] and fingers_up["thumb"]):
        # Perform action
        pyautogui.hotkey("cmd", "tab")  # macOS app switcher
        self.status = "App switcher"

# Then call in main loop:
# self.handle_custom_gesture(fingers_up, now)
```

### Performance Tuning

**For slower computers:**
```python
# In config.py:
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 360
MIN_DETECTION_CONFIDENCE = 0.8  # Skip faint detections
MIN_TRACKING_CONFIDENCE = 0.8
SMOOTHING_FACTOR = 3  # Less smoothing = less CPU
```

**For better accuracy:**
```python
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
MIN_DETECTION_CONFIDENCE = 0.5
SMOOTHING_FACTOR = 10
```

---

## 📊 Performance Monitoring

### Check CPU and Memory Usage

```bash
# Monitor in real-time (press Ctrl+C to stop)
top -p $(pgrep -f "python.*virtual_mouse")

# Get detailed stats
ps aux | grep virtual_mouse
```

### Frame Rate Analysis

Add this to the main loop in `virtual_mouse.py`:

```python
import time

frame_times = []
start_time = time.time()

# In main loop, after cv2.waitKey(1):
current_time = time.time()
frame_times.append(current_time - start_time)

# Print FPS every 100 frames
if len(frame_times) >= 100:
    avg_time = sum(frame_times) / len(frame_times)
    fps = 1 / avg_time if avg_time > 0 else 0
    print(f"Average FPS: {fps:.1f}")
    frame_times = []
    
start_time = current_time
```

---

## 🔄 Reset to Defaults

If configuration becomes corrupted, reset to defaults:

```bash
# Remove custom config
rm config.py

# Application will use hardcoded defaults
python virtual_mouse.py
```

---

## 📱 Testing Individual Components

### Test Camera Only
```python
import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break
    
    cv2.imshow("Camera Test", cv2.flip(frame, 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Test Hand Detection Only
```python
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    if results.multi_hand_landmarks:
        print(f"Hand detected! {len(results.multi_hand_landmarks)} hand(s)")
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
    
    cv2.imshow("Hand Detection Test", cv2.flip(frame, 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Test Microphone Only
```python
import speech_recognition as sr

recognizer = sr.Recognizer()

try:
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 🚀 Performance Optimization Tips

1. **Close other applications** - Reduces system load
2. **Use good lighting** - Improves hand detection speed
3. **Keep hand steady** - Reduces jitter compensation
4. **Reduce resolution** - Faster processing if FPS is low
5. **Disable voice** when not needed - Saves CPU and network
6. **Use wired USB camera** - More stable than wireless
7. **Update drivers** - Ensures optimal camera performance
8. **Use external microphone** - Better audio for voice commands

---

## 📞 Getting More Help

**Enable debug mode:**
```python
# Uncomment in virtual_mouse.py to see detailed logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Collect diagnostic information:**
```bash
# Create a diagnostic report
python << 'EOF'
import cv2, mediapipe, speech_recognition, pyaudio, numpy, pyautogui
import platform

print("=== System Info ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {platform.python_version()}")

print("\n=== Installed Packages ===")
packages = ["cv2", "mediapipe", "speech_recognition", "pyaudio", "numpy", "pyautogui"]
for pkg in packages:
    try:
        mod = __import__(pkg)
        print(f"✓ {pkg}: {mod.__version__ if hasattr(mod, '__version__') else 'installed'}")
    except:
        print(f"✗ {pkg}: NOT INSTALLED")

print("\n=== Hardware ===")
cap = cv2.VideoCapture(0)
print(f"Camera: {'✓ Available' if cap.isOpened() else '✗ Not found'}")
cap.release()

mic = speech_recognition.Microphone()
print(f"Microphone: {'✓ Available' if mic else '✗ Not found'}")

print(f"Screen: {pyautogui.size()}")
EOF
```

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
python << 'EOF'
print("=" * 50)
print("Virtual Mouse Health Check")
print("=" * 50)

# Check imports
try:
    import cv2
    print("✓ OpenCV")
except:
    print("✗ OpenCV - pip install opencv-python")

try:
    import mediapipe
    print("✓ MediaPipe")
except:
    print("✗ MediaPipe - pip install mediapipe")

try:
    import speech_recognition
    print("✓ SpeechRecognition")
except:
    print("✗ SpeechRecognition - pip install SpeechRecognition")

try:
    import pyaudio
    print("✓ PyAudio")
except:
    print("✗ PyAudio - pip install pyaudio")

try:
    import pyautogui
    print("✓ PyAutoGUI")
except:
    print("✗ PyAutoGUI - pip install pyautogui")

try:
    import PIL
    print("✓ Pillow")
except:
    print("✗ Pillow - pip install pillow")

# Check hardware
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✓ Camera detected")
        cap.release()
    else:
        print("✗ Camera not found")
except:
    print("✗ Camera check failed")

try:
    import speech_recognition as sr
    sr.Microphone()
    print("✓ Microphone detected")
except:
    print("✗ Microphone not found")

print("\n✓ Ready to run: python virtual_mouse.py")
EOF
```

---

**Last Updated:** December 2025  
**Tested on:** macOS 12-14 (Intel & Apple Silicon)
