# Quick Reference Card - Virtual Mouse

## 🚀 Installation (One-liner)
```bash
chmod +x install.sh && ./install.sh
```

## ▶️ Running the App
```bash
source venv/bin/activate
python virtual_mouse.py
# OR simply: ./run.sh
```

---

## 🎮 GESTURE CONTROLS

### Enable Mouse
- **Action:** Hold open palm (all 5 fingers) for ~1 second
- **OR:** Press `M`
- **OR:** Say "enable"

### Cursor Movement
- **Action:** Point index finger
- **Effect:** Cursor follows your finger

### Left Click
- **Gesture:** Quick pinch (thumb + index)
- **Voice:** "click", "left click", "tap"

### Double Click
- **Gesture:** Two quick pinches (within 0.35 seconds)
- **Voice:** "double click", "double tap"

### Right Click
- **Gesture:** Pinch thumb + middle finger
- **Voice:** "right click", "context menu"

### Drag & Drop
- **Gesture:** Pinch thumb + index and hold >0.25s
- **Release:** Open fingers to release
- **Voice:** N/A (gesture only)

### Scroll
- **Gesture:** Peace sign (index + middle up), move hand up/down
- **Voice:** "scroll up", "scroll down"

### Screenshot
- **Gesture:** 3 fingers up (index, middle, ring), thumb + pinky down
- **Voice:** "screenshot", "snap", "take picture"
- **Keyboard:** Press `S`

### Show Desktop
- **Gesture:** 4 fingers up (all but thumb)
- **Voice:** "desktop", "show desktop"

### Maximize Window
- **Gesture:** 5 fingers up (hold while mouse enabled)
- **Voice:** "maximize", "max"

---

## 🎤 VOICE COMMANDS (Quick List)

### Click Commands
| Command | Alternatives |
|---------|--------------|
| click | left click, tap |
| double click | double tap |
| right click | context menu |

### Scroll
| Command | Effect |
|---------|--------|
| scroll up | Scroll page up |
| scroll down | Scroll page down |

### Screenshots
| Command | Alternatives |
|---------|--------------|
| screenshot | snap, take picture |

### Window Management
| Command | macOS Shortcut |
|---------|----------------|
| maximize | cmd+ctrl+f |
| minimize | cmd+m |
| desktop | fn+f11 |

### Editing
| Command | macOS Shortcut |
|---------|----------------|
| undo | cmd+z |
| redo | cmd+shift+z |
| copy | cmd+c |
| paste | cmd+v |
| cut | cmd+x |
| select all | cmd+a |

### Control
| Command | Effect |
|---------|--------|
| enable | Turn mouse on |
| disable | Turn mouse off |

### Greeting
| Command | Response |
|---------|----------|
| hello | Hi! |
| hi | Hi! |
| hey | Hi! |

---

## ⌨️ KEYBOARD SHORTCUTS

| Key | Function |
|-----|----------|
| `M` | Toggle mouse ON/OFF |
| `V` | Toggle voice ON/OFF |
| `S` | Manual screenshot test |
| `Q` | Quit application |

---

## 🔧 CONFIGURATION

### Quick Config Changes

**Make clicks easier:**
```python
# In config.py
PINCH_THRESHOLD = 25  # Was 35
```

**Smoother cursor (less jitter):**
```python
SMOOTHING_FACTOR = 10  # Was 6
```

**Better for poor lighting:**
```python
MIN_DETECTION_CONFIDENCE = 0.5  # Was 0.7
```

**Voice not working?**
```python
VOICE_ENERGY_THRESHOLD = 5000  # Was 4000 (ignore more noise)
```

---

## ❌ TROUBLESHOOTING QUICK FIXES

### Hand not detected
1. Improve lighting ☀️
2. Move hand 60-90cm from camera
3. Lower detection confidence in config.py

### Cursor jitters
1. Increase SMOOTHING_FACTOR to 8-10
2. Better lighting needed
3. Hold hand more steadily

### Clicks not working
1. Increase PINCH_THRESHOLD to 45 (harder to trigger)
2. Move closer to camera
3. Use larger pinching motion

### Voice not working
1. Check System Prefs > Security > Microphone access
2. `brew install flac` (if not done)
3. Speak clearly in quiet room
4. Check internet connection

### Camera not found
1. Test: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`
2. Try different camera: `CAMERA_INDEX = 1` in config.py
3. Check USB connection (external camera)

---

## 📊 PERFORMANCE TIPS

### For Slow Computers
```python
CAMERA_WIDTH = 480   # Was 640
CAMERA_HEIGHT = 360  # Was 480
SMOOTHING_FACTOR = 3 # Less smoothing
```

### For Best Accuracy
```python
CAMERA_WIDTH = 1280  # Larger
CAMERA_HEIGHT = 720
SMOOTHING_FACTOR = 10
```

### Disable voice if not needed
- Press `V` to turn off voice
- Saves CPU and network bandwidth

---

## 🧪 QUICK TESTS

### Test Camera
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Test Microphone
```bash
python -c "import speech_recognition as sr; sr.Microphone(); print('OK')"
```

### Test Hand Detection
```python
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands.Hands()
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
results = mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
print("Hand detected!" if results.multi_hand_landmarks else "No hand")
```

### Full Health Check
```bash
python << 'EOF'
try:
    import cv2, mediapipe, speech_recognition, pyaudio, numpy, pyautogui
    print("✓ All packages installed")
except: print("✗ Missing packages")

import cv2
cap = cv2.VideoCapture(0)
print("✓ Camera OK" if cap.isOpened() else "✗ Camera missing")
cap.release()

try:
    speech_recognition.Microphone()
    print("✓ Microphone OK")
except: print("✗ Microphone missing")
EOF
```

---

## 📚 DOCUMENTATION FILES

| File | Purpose |
|------|---------|
| README.md | Project overview & features |
| SETUP_GUIDE.md | Detailed installation |
| TROUBLESHOOTING.md | Problem solving |
| config.py | Configuration options |
| virtual_mouse.py | Main application |
| requirements.txt | Dependencies |
| install.sh | Automated setup |

---

## 🎯 COMMON TASKS

### Change camera
```python
# In config.py
CAMERA_INDEX = 1  # Try 0, 1, 2, etc.
```

### Add custom voice command
```python
# In virtual_mouse.py, in _process_command()
elif "mycommand" in text_lower:
    pyautogui.hotkey("cmd", "x")  # Your action
    self.virtual_mouse.status = "Custom command"
```

### Add custom gesture
```python
# In virtual_mouse.py, add method to VirtualMouseFinalEnhanced class
def handle_my_gesture(self, fingers_up, now):
    if fingers_up["index"] and fingers_up["thumb"]:
        # Do something
        pass

# Call in main loop:
self.handle_my_gesture(fingers_up, now)
```

### Disable voice completely
```python
# Don't call voice_listener.start() in __init__
# Or press V to toggle
```

---

## 💡 PRO TIPS

1. **Improve accuracy:** Better lighting = better hand detection
2. **Smoother scrolling:** Increase SCROLL_SENSITIVITY to 3.5
3. **Faster clicks:** Reduce CLICK_COOLDOWN to 0.15
4. **Better voice:** Use quiet room + speak clearly
5. **Save battery:** Disable voice when not needed
6. **Multiple users:** Create separate config.py per user
7. **Calibrate:** Test thresholds with your hand size
8. **Record gestures:** Can add gesture recording feature

---

## 📞 SUPPORT

**Quick Help:**
- Check TROUBLESHOOTING.md
- Run health check (see above)
- Test individual components
- Check configuration

**Detailed Help:**
- Read SETUP_GUIDE.md
- See code comments in virtual_mouse.py
- Check README.md FAQ section

**Still stuck?**
- Verify internet (for voice)
- Check system permissions
- Ensure all packages installed
- Try different Python version (3.8+)

---

## 🎓 QUICK LEARNING

### Hand Gesture Landmarks (21 points)
- 0: Wrist
- 1-4: Thumb (base to tip)
- 5-8: Index (base to tip)
- 9-12: Middle (base to tip)
- 13-16: Ring (base to tip)
- 17-20: Pinky (base to tip)

### Key Calculations
- **Pinch:** Distance between thumb tip (4) and index tip (8)
- **Scroll:** Track middle tip (12) vertical movement
- **Cursor:** Use index tip (8) for positioning

---

## ✅ SETUP CHECKLIST

- [ ] Run install.sh
- [ ] Grant microphone access (System Prefs)
- [ ] Test camera: `python -c "import cv2; ..."`
- [ ] Test microphone: `python -c "import speech_recognition; ..."`
- [ ] Run app: `python virtual_mouse.py`
- [ ] Test open palm to enable
- [ ] Test a gesture
- [ ] Test a voice command
- [ ] Read README.md

---

**Quick Start:** `chmod +x install.sh && ./install.sh && ./run.sh`

**Documentation:** See README.md, SETUP_GUIDE.md, TROUBLESHOOTING.md

**Version:** 2.0 | **Last Updated:** December 2025
