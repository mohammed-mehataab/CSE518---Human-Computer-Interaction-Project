#!/bin/bash
# Virtual Mouse - Automated Setup Script for macOS
# This script automates the installation process

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Virtual Mouse - Automated Setup Script for macOS          ║"
echo "║     Hand Gesture + Voice Control                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Detect OS
echo "🔍 Detecting system..."
if [[ ! "$OSTYPE" == "darwin"* ]]; then
    print_error "This script is for macOS only"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_status "Apple Silicon (M1/M2/M3) detected"
    APPLE_SILICON=true
else
    print_status "Intel Mac detected"
    APPLE_SILICON=false
fi

echo ""
echo "📋 Step 1: Installing Homebrew (if needed)..."

if ! command -v brew &> /dev/null; then
    print_status "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    print_status "Homebrew installed"
else
    print_status "Homebrew already installed"
fi

echo ""
echo "📋 Step 2: Installing system dependencies..."

print_status "Installing portaudio..."
brew install portaudio 2>/dev/null || print_warning "portaudio already installed"

print_status "Installing flac..."
brew install flac 2>/dev/null || print_warning "flac already installed"

print_status "Linking portaudio..."
brew link portaudio 2>/dev/null || print_warning "portaudio already linked"

echo ""
echo "📋 Step 3: Setting up Python environment..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python $PYTHON_VERSION found"

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

echo ""
echo "📋 Step 4: Installing Python dependencies..."

print_status "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

print_status "Installing OpenCV..."
pip install opencv-python > /dev/null 2>&1

print_status "Installing MediaPipe..."
pip install mediapipe > /dev/null 2>&1

print_status "Installing Pillow..."
pip install pillow > /dev/null 2>&1

print_status "Installing PyAutoGUI..."
pip install pyautogui > /dev/null 2>&1

print_status "Installing NumPy..."
pip install numpy > /dev/null 2>&1

print_status "Installing SpeechRecognition..."
pip install SpeechRecognition > /dev/null 2>&1

echo ""
echo "📋 Step 5: Installing PyAudio (may take a moment)..."

if [ "$APPLE_SILICON" = true ]; then
    print_status "Installing PyAudio for Apple Silicon..."
    arch -arm64 pip install --no-cache-dir --global-option='build_ext' \
      --global-option='-I/opt/homebrew/include' \
      --global-option='-L/opt/homebrew/lib' pyaudio==0.2.11
else
    print_status "Installing PyAudio for Intel Mac..."
    pip install pyaudio > /dev/null 2>&1
fi

echo ""
echo "📋 Step 6: Creating directories..."

SCREENSHOTS_DIR="$HOME/Desktop/Screenshots"
if [ ! -d "$SCREENSHOTS_DIR" ]; then
    mkdir -p "$SCREENSHOTS_DIR"
    print_status "Created screenshot directory: $SCREENSHOTS_DIR"
else
    print_status "Screenshot directory already exists"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Grant microphone access:"
echo "     System Preferences > Security & Privacy > Microphone"
echo "     Enable Terminal (or Python)"
echo ""
echo "  3. Run the application:"
echo "     python virtual_mouse.py"
echo ""
echo "📚 For detailed setup instructions, see SETUP_GUIDE.md"
echo "❓ For troubleshooting, see TROUBLESHOOTING.md"
echo ""
echo "🎮 Enjoy your hands-free computing!"
echo ""

# Create a convenience script to activate and run
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python virtual_mouse.py
EOF

chmod +x run.sh
print_status "Created convenience script: ./run.sh"
echo ""
echo "💡 To run in the future, simply:"
echo "   ./run.sh"
echo ""
