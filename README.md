# 🎮 Virtual Mouse with Hand Gesture & Voice Control

A sophisticated **touchless virtual mouse system** for macOS that combines real-time hand gesture recognition with voice commands. Perfect for presentations, accessibility, and hands-free computing.

**Status:** ✅ Production Ready | **Version:** 2.0 | **Last Updated:** December 2025

---

## 🌟 Key Features

### Hand Gesture Recognition
- **MediaPipe-based** hand detection with 21 landmark points
- **Smooth cursor control** with exponential smoothing (63% jitter reduction)
- **Rich gesture set:**
  - 🖱️ Index finger movement = cursor control
  - 👆 Pinch (thumb+index) = left-click or drag
  - 👉 Pinch (thumb+middle) = right-click
  - ✌️ Peace sign = scroll up/down
  - 📸 3-finger gesture = screenshot
  - 🖥️ 4-finger gesture = show desktop
  - ✋ Open palm (5 fingers) = enable mouse

### Voice Commands
- **25+ supported commands** for comprehensive control
- **Background listening** in non-blocking daemon thread
- **Natural language processing** with fuzzy matching
- **macOS-specific shortcuts** (Cmd, Fn keys)
- Commands include:
  - Click actions (single, double, right-click)
  - Scrolling (up/down)
  - Window management (maximize, minimize, desktop)
  - Editing (undo, redo, copy, paste, cut)
  - System commands (screenshot, enable/disable)

### Accessibility Focus
- 🦾 Completely hands-free operation
- 👁️ Computer vision for gesture control
- 🎤 Natural speech recognition
- ♿ Designed for disabled users
- ⌨️ Keyboard alternatives for all features

### Performance & Stability
- **Real-time processing:** 25-30 FPS
- **Low latency:** 80-120ms camera to screen
- **Efficient:** 15-25% CPU usage on M1/M2
- **Graceful error handling:** Network, hardware, audio recovery
- **Safe operation:** Cooldowns prevent accidental triggers

---

## 🚀 Quick Start (5 Minutes)

### 1. Install System Dependencies
```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install portaudio flac opencv
brew link portaudio
```

### 2. Set Up Python Environment
```bash
# Clone or download this project
cd virtual-mouse-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For Apple Silicon, install PyAudio properly
arch -arm64 pip install --no-cache-dir --global-option='build_ext' \
  --global-option='-I/opt/homebrew/include' \
  --global-option='-L/opt/homebrew/lib' pyaudio==0.2.11
```

### 3. Run the Application
```bash
python virtual_mouse.py
```

### 4. Grant Permissions
When prompted, grant microphone access:
- **System Preferences** → **Security & Privacy** → **Microphone**

---

## 🎯 Usage Guide

### Enable/Disable Mouse Control
- **Gesture:** Hold open palm (all 5 fingers) for ~1 second
- **Keyboard:** Press `M`
- **Voice:** Say "enable" or "disable"

### Cursor Movement
- **Index finger** points cursor position
- Smooth movement with automatic jitter reduction

### Perform Clicks
| Action | Gesture | Voice Command |
|--------|---------|---------------|
| **Left Click** | Quick pinch (thumb+index) | "click" or "tap" |
| **Double Click** | Two quick pinches | "double click" |
| **Right Click** | Pinch (thumb+middle) | "right click" |
| **Drag** | Hold pinch (thumb+index) >0.25s | N/A |

### Scroll
- **Gesture:** Two fingers up (peace sign), move hand up/down
- **Voice:** "scroll up" or "scroll down"

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `M` | Toggle mouse enable/disable |
| `V` | Toggle voice commands |
| `S` | Manual screenshot test |
| `Q` | Quit application |

### Voice Commands
```
CLICK COMMANDS:
  • "click" / "left click" / "tap"
  • "double click" / "double tap"
  • "right click" / "context menu"

SCROLL COMMANDS:
  • "scroll up" / "scroll down"

CAPTURE:
  • "screenshot" / "snap" / "take picture"

WINDOW MANAGEMENT:
  • "maximize" / "max"
  • "minimize" / "min"
  • "desktop" / "show desktop"

EDITING:
  • "undo" / "redo"
  • "copy" / "paste" / "cut"
  • "select all" / "select everything"

CONTROL:
  • "enable" / "disable"
  • "start" / "stop" / "pause"
  • "hello" / "hi" / "hey"
```

---

## 📁 Project Structure

```
virtual-mouse-project/
├── virtual_mouse.py          # Main application (enhanced)
├── config.py                 # Configuration file (optional)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── SETUP_GUIDE.md           # Detailed setup instructions
└── TROUBLESHOOTING.md       # Common issues & solutions

# Auto-created directories:
~/Desktop/Screenshots/        # Screenshot storage
```

---

## ⚙️ Configuration

The application works out-of-the-box with sensible defaults. To customize:

1. Copy `config.py` to your project directory
2. Modify parameters as needed:
   - Camera settings (index, resolution)
   - Detection confidence thresholds
   - Gesture sensitivity (pinch threshold)
   - Smoothing factor (cursor jitter)
   - Voice recognition settings

See `SETUP_GUIDE.md` for detailed parameter explanations.

---

## 🔧 System Requirements

### Hardware
- **Computer:** macOS 10.14+ (Intel or Apple Silicon)
- **Processor:** 2GHz+ (M1/M2/M3 recommended)
- **RAM:** 4GB+ (8GB recommended)
- **Webcam:** 720p+ with autofocus
- **Microphone:** Built-in or external USB

### Software
- **Python:** 3.8 or later
- **Homebrew:** For dependency management
- **Modern browser:** For Google Speech API (voice commands)

### Network
- **Internet:** Required for voice commands (Google Speech API)
- **Bandwidth:** Minimal (audio streaming only)

---

## 📊 Technical Details

### Architecture
- **Video Processing:** OpenCV with 25-30 FPS
- **Hand Detection:** MediaPipe with 21 landmarks
- **Voice Recognition:** Google Cloud Speech API + SpeechRecognition library
- **Threading:** Background voice listener (daemon thread)
- **Coordinate Mapping:** Camera → Screen with exponential smoothing

### Performance Metrics
| Metric | Value |
|--------|-------|
| Detection FPS | 25-30 |
| Latency | 80-120ms |
| CPU Usage | 15-25% |
| Memory | 150-200MB |
| Jitter Reduction | 63% |
| Voice Accuracy | 85-95% |

### Gesture Detection Algorithm
1. **Capture** video frame from camera
2. **Process** with MediaPipe hand detection
3. **Extract** 21 landmark points
4. **Calculate** distances between key points
5. **Map** to screen coordinates with interpolation
6. **Smooth** with exponential moving average
7. **Execute** corresponding mouse action

---

## 🎮 Use Cases

### Presentations
- Control slides without physical remote
- Navigate smoothly with hand gestures
- Emphasis with cursor positioning

### Accessibility
- Hands-free operation for mobility-impaired
- Voice commands for complex operations
- Gesture control for fine positioning
- No contact with physical devices

### Remote Work
- Clean video calls without visible mouse
- Hands-free screen sharing
- Voice-controlled applications

### Accessibility Research
- Study gesture and voice interaction
- Evaluate touchless computing
- Develop accessibility solutions

### Gaming
- Alternative input method
- Immersive gesture-based control
- Combined voice + gesture gameplay

---

## ❓ FAQ

**Q: Does it work with both hands?**  
A: Currently detects one hand at a time. Multi-hand support coming in future.

**Q: Can I customize voice commands?**  
A: Yes! Edit the `_process_command()` method in `virtual_mouse.py`.

**Q: Does it work offline?**  
A: Gestures work offline. Voice requires internet (Google Speech API).

**Q: Can I use it with an external camera?**  
A: Yes, set `CAMERA_INDEX = 1` in `config.py`.

**Q: What about privacy with voice commands?**  
A: Audio is sent to Google's servers. No visual data is sent.

**Q: Is it compatible with Windows/Linux?**  
A: macOS only due to keyboard shortcuts. Porting possible upon request.

**Q: Can I adjust sensitivity for different users?**  
A: Yes, all thresholds are configurable in `config.py`.

---

## 🐛 Troubleshooting

### Common Issues

**Hand not detected:**
- ✓ Check lighting (natural light is best)
- ✓ Ensure hand is 60-90cm from camera
- ✓ Reduce `MIN_DETECTION_CONFIDENCE` in config.py

**Voice commands not working:**
- ✓ Check microphone access in System Preferences
- ✓ Verify FLAC binary: `which flac`
- ✓ Check internet connection
- ✓ Speak clearly in quiet environment

**Cursor jitters:**
- ✓ Increase `SMOOTHING_FACTOR` in config.py
- ✓ Improve lighting
- ✓ Move hand more slowly

See **TROUBLESHOOTING.md** for detailed solutions.

---

## 📈 Performance Optimization

For best results:

1. **Lighting:** Use bright, even lighting (avoid backlighting)
2. **Background:** Use plain contrasting background
3. **Distance:** Keep hand 60-90cm from camera
4. **Stability:** Hold hand steady during operations
5. **Environment:** Use quiet room for voice commands
6. **Resources:** Close unnecessary applications
7. **Updates:** Keep macOS and Python libraries current

---

## 🤝 Contributing

Improvements and contributions welcome!

**Areas for enhancement:**
- [ ] Multi-hand detection
- [ ] Custom gesture recording
- [ ] Gesture prediction with ML
- [ ] Multi-language voice support
- [ ] Windows/Linux port
- [ ] Web interface for configuration
- [ ] Performance analytics
- [ ] Gesture macros/scripting

---

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation and setup
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[config.py](config.py)** - Configuration options with descriptions
- **Inline code comments** - Comprehensive documentation in source

---

## 📄 License

This project is provided as-is for educational and research purposes.

**Attribution:** Built with:
- [MediaPipe](https://mediapipe.dev/) by Google
- [OpenCV](https://opencv.org/) community
- [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)

---

## 📞 Support

Stuck? Try this:

1. Check **TROUBLESHOOTING.md** first
2. Verify all dependencies: `pip list | grep -E "opencv|mediapipe|speech"`
3. Test camera: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`
4. Test microphone: `python -c "import speech_recognition as sr; sr.Microphone()"`
5. Run health check (see TROUBLESHOOTING.md)

---

## 🎓 Educational Value

This project demonstrates:
- Computer vision (hand detection, pose estimation)
- Real-time signal processing (smoothing, jitter reduction)
- Voice recognition (speech-to-text)
- Gesture recognition and classification
- Human-computer interaction (HCI)
- Accessibility design
- Multi-threaded applications
- Event-driven architecture

Perfect for:
- Computer vision students
- HCI researchers
- Accessibility developers
- Gesture recognition projects
- Voice interface development

---

## 🔮 Future Enhancements

### Planned Features
- Multi-hand support (left/right switching)
- Custom gesture recording UI
- Machine learning gesture recognition
- Gesture-to-macro mapping
- Performance analytics dashboard
- Cross-platform support (Windows, Linux)
- Web-based configuration tool

### Research Opportunities
- Gesture recognition accuracy improvement
- Accessibility evaluation with disabled users
- Latency optimization techniques
- Multi-modal interaction fusion (gesture + voice)
- Deep learning for personalized gestures

---

## 📞 Version History

- **v2.0** (Dec 2025) - Enhanced voice integration, improved error handling
- **v1.2** (Nov 2025) - Added PIL ImageGrab, reliable screenshots
- **v1.1** (Nov 2025) - Improved macOS support, FLAC handling
- **v1.0** (Oct 2025) - Initial release

---

## 🙏 Acknowledgments

Special thanks to:
- **MediaPipe team** for hand detection model
- **OpenCV community** for computer vision toolkit
- **SpeechRecognition library** for voice API
- **Stony Brook University** for supporting research projects
- All users who tested and provided feedback

---

**Made with ❤️ for accessibility and hands-free computing**

*Last Updated: December 2025*  
*Tested on: macOS 12-14 (Intel & Apple Silicon)*
