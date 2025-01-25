import sys
import cv2
import pygame
from PyQt5.QtGui import QImage, QPixmap, QGuiApplication
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QStatusBar
)
from PyQt5.QtCore import QTimer, QRect, Qt

class ARPiano(QMainWindow):
    """
    A PyQt5 window that:
      - Detects screen size and uses it for the window.
      - Attempts to set the camera to the same resolution.
      - Overlays proportionally scaled piano keys near the bottom, centered.
      - Stretches the camera feed to fill the entire window (no black bars).
      - Plays notes via pygame mixer when keys are clicked or shortcuts are pressed.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AR Piano Demo - Full Screen Matching")

        # 1) Initialize pygame mixer for audio
        pygame.init()
        pygame.mixer.init()

        # 2) Dictionary to hold {note_name: Sound object}
        self.sounds = {}

        # 3) Detect the screen size
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.screen_w = screen_geometry.width()
        self.screen_h = screen_geometry.height()

        # 4) Resize this window to fill that available screen area
        #    Or you can do self.showFullScreen() for *true* fullscreen.
        self.setGeometry(0, 0, self.screen_w, self.screen_h)

        # 5) Set up the camera capture
        #    Attempt to match the screen size for the camera resolution
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # On Windows, CAP_DSHOW sometimes helps
        if not self.cap.isOpened():
            print("Warning: Could not open camera.")
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.screen_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.screen_h)

        # 6) Create a label to show the camera feed
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, self.screen_w, self.screen_h)
        self.camera_label.setStyleSheet("background-color: black;")

        # 7) Load your .wav files
        self.load_sounds()

        # 8) Create the piano keys, sized/positioned proportionally
        self.create_white_keys()
        self.create_black_keys()

        # 9) Optional status bar
        self.setStatusBar(QStatusBar(self))

        # 10) QTimer to grab camera frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)  # ~30 FPS

    def load_sounds(self):
        """
        Load .wav files into pygame.mixer.Sound.
        Make sure these files exist at C:/Users/LLR User/Desktop/music/Sounds/.
        """
        base = "C:/Users/LLR User/Desktop/music/Sounds/"

        # A subset of notes—adjust as you have .wav files
        white_notes = ["c4","d4","e4","f4","g4","a4","b4","c5","d5","e5","f5","g5","a5","b5"]
        black_notes = ["c40","d40","f40","g40","a40","c50","d50","f50","g50","a50"]

        for note in white_notes + black_notes:
            self.sounds[note] = pygame.mixer.Sound(base + f"{note}.wav")

    def create_white_keys(self):
        """
        Create a row of white keys, sized and positioned proportionally to screen size.
        We'll place them near the bottom, centered horizontally.
        """
        white_keys = [
            ("c4", "Q"), ("d4", "W"), ("e4", "E"), ("f4", "R"),
            ("g4", "T"), ("a4", "Y"), ("b4", "U"),
            ("c5", "I"), ("d5", "O"), ("e5", "P"), ("f5", "["),
            ("g5", "]"), ("a5", "\\"), ("b5", "1")
        ]

        num_white = len(white_keys)
        # We'll define a fraction of screen width for each key
        key_w = self.screen_w / 20.0  # adjust as you like
        key_h = self.screen_h / 4.0   # e.g. 25% of screen height
        total_width = num_white * key_w

        # Center them horizontally
        x_start = (self.screen_w - total_width) / 2
        # Place them near the bottom with a 5% margin
        margin_bottom = self.screen_h * 0.05
        y_pos = self.screen_h - key_h - margin_bottom

        for i, (note_name, shortcut) in enumerate(white_keys):
            x = x_start + i * key_w
            btn = QPushButton(note_name.upper(), self)
            btn.setObjectName(note_name)
            btn.setShortcut(shortcut)
            btn.setGeometry(QRect(int(x), int(y_pos), int(key_w), int(key_h)))
            btn.setStyleSheet("""
                background-color: rgba(255, 255, 255, 200);
                font-weight: bold;
                font-size: 18px;
            """)
            btn.clicked.connect(self.play_sound)

    def create_black_keys(self):
        """
        Create black keys in between the white keys, proportionally.
        For 10 black keys: c40, d40, f40, g40, a40, c50, d50, f50, g50, a50
        We'll approximate positions similarly.
        """
        black_keys = [
            ("c40", "2"), ("d40", "3"), ("f40", "5"), ("g40", "6"), ("a40", "7"),
            ("c50", "8"), ("d50", "9"), ("f50", "0"), ("g50", "-"), ("a50", "=")
        ]

        # We'll base black key widths on ~60% of white key width
        white_key_w = self.screen_w / 20.0
        black_key_w = white_key_w * 0.6
        black_key_h = self.screen_h / 5.0  # a bit shorter

        # We need the same x_start from create_white_keys
        # Let's just recalc quickly:
        num_white = 14
        total_white_w = num_white * white_key_w
        x_white_start = (self.screen_w - total_white_w) / 2
        margin_bottom = self.screen_h * 0.05
        y_white_pos = self.screen_h - (self.screen_h / 4.0) - margin_bottom
        # black keys will be placed slightly above that
        y_black_pos = y_white_pos

        # Approx offsets for black keys between white keys
        # Adjust these to visually place black keys in correct spots
        black_offsets = [
            white_key_w * 0.7,   # c40
            white_key_w * 1.7,   # d40
            white_key_w * 3.7,   # f40
            white_key_w * 4.7,   # g40
            white_key_w * 5.7,   # a40
            white_key_w * 7.7,   # c50
            white_key_w * 8.7,   # d50
            white_key_w * 10.7,  # f50
            white_key_w * 11.7,  # g50
            white_key_w * 12.7,  # a50
        ]

        for i, (note_name, shortcut) in enumerate(black_keys):
            x = x_white_start + black_offsets[i]
            btn = QPushButton(note_name.upper(), self)
            btn.setObjectName(note_name)
            btn.setShortcut(shortcut)
            btn.setGeometry(QRect(int(x), int(y_black_pos), int(black_key_w), int(black_key_h)))
            btn.setStyleSheet("""
                background-color: rgba(0, 0, 0, 220);
                color: white;
                font-weight: bold;
                font-size: 16px;
            """)
            btn.clicked.connect(self.play_sound)

    def play_sound(self):
        """Called when a piano key is clicked or its shortcut pressed."""
        note_name = self.sender().objectName()
        if note_name in self.sounds:
            self.sounds[note_name].play()

    def update_camera(self):
        """
        Grabs a frame from the webcam, converts it to QPixmap,
        and STRETCHES it to fill the entire window.
        """
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w

        # Convert to QImage -> QPixmap
        qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # SCALE to fill the entire camera_label area, ignoring aspect ratio
        pixmap = pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.IgnoreAspectRatio,        # <--- Fill exactly, no letterbox
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(pixmap)

    def closeEvent(self, event):
        """
        Cleanup camera and quit pygame on close.
        """
        if self.cap.isOpened():
            self.cap.release()
        pygame.quit()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = ARPiano()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
