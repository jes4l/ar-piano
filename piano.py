import sys
import cv2
import mediapipe as mp
import pygame

from PyQt5.QtGui import QImage, QPixmap, QGuiApplication, QPainter, QPen, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QStatusBar
)
from PyQt5.QtCore import QTimer, QRect, Qt, QPoint


class SkeletonOverlay(QLabel):
    """
    A transparent overlay widget that draws the hand skeleton on top of everything.
    Stores skeleton lines and points from the main ARPiano class and paints them here.
    """
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        # Allow mouse events to pass through to underlying widgets
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.skeleton_data = []  # List of line segments: [((x1,y1),(x2,y2)), ...]
        self.points_data = []    # List of landmark points: [(px, py), ...]

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw skeleton connections as green lines
        pen_line = QPen(QColor(0, 255, 0, 200), 3)  # Semi-transparent green
        painter.setPen(pen_line)
        for line in self.skeleton_data:
            (x1, y1), (x2, y2) = line
            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))

        # Draw landmark points as green circles
        pen_points = QPen(QColor(0, 255, 0, 200), 6)  # Semi-transparent green
        painter.setPen(pen_points)
        for (px, py) in self.points_data:
            painter.drawPoint(QPoint(px, py))


class ARPiano(QMainWindow):
    """
    A PyQt5 window that:
      - Displays a stretched camera feed in the background.
      - Overlays a larger, visually appealing piano keyboard positioned slightly higher.
      - Uses MediaPipe to track specific fingertips and plays notes when they touch keys.
      - Draws the hand skeleton in a transparent overlay above the keys.
    """

    # Fingertip and PIP indices in MediaPipe for index, middle, ring, and pinky fingers
    FINGER_TIPS =  [8, 12, 16, 20]
    FINGER_PIPS =  [6, 10, 14, 18]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AR Piano + Smaller Black Keys + Finger Extension Only")

        # 1) Initialize pygame mixer for audio playback
        pygame.init()
        pygame.mixer.init()

        # 2) Dictionary to hold {note_name: Sound object}
        self.sounds = {}

        # 3) Detect screen size
        screen = QGuiApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.screen_w = rect.width()
        self.screen_h = rect.height()

        # 4) Set window geometry to fill the screen
        self.setGeometry(0, 0, self.screen_w, self.screen_h)

        # 5) Initialize camera capture (webcam)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW on Windows for better performance
        if not self.cap.isOpened():
            print("Warning: Could not open camera.")
        else:
            # Attempt to set camera resolution to match screen size
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.screen_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.screen_h)

        # 6) Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, self.screen_w, self.screen_h)
        self.camera_label.setStyleSheet("background-color: black;")

        # 7) Load .wav sound files into pygame mixer
        self.load_sounds()

        # 8) Create piano keys (white and black), stored for collision detection
        self.keys_info = []
        self.create_white_keys()
        self.create_black_keys()

        # 9) Optional: Add a status bar (can be used for debugging or status messages)
        self.setStatusBar(QStatusBar(self))

        # 10) Initialize MediaPipe Hands for hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS

        # 11) Debounce mechanism: Track active notes to prevent repeated triggering
        self.active_notes = set()

        # 12) Create a SkeletonOverlay to draw hand skeletons above all widgets
        self.overlay_label = SkeletonOverlay(self, self.screen_w, self.screen_h)
        self.overlay_label.show()

        # 13) Set up a QTimer to periodically grab frames from the camera
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)  # Approximately 30 FPS

    def load_sounds(self):
        """
        Load .wav files into pygame.mixer.Sound objects.
        Ensure that the files are located at:
        C:/Users/LLR User/Desktop/music/Sounds/
        """
        base = "C:/Users/LLR User/Desktop/music/Sounds/"

        # List of white and black note filenames (without extension)
        white_notes = ["c4","d4","e4","f4","g4","a4","b4","c5","d5","e5","f5","g5","a5","b5"]
        black_notes = ["c40","d40","f40","g40","a40","c50","d50","f50","g50","a50"]

        # Load white notes
        for note in white_notes:
            try:
                self.sounds[note] = pygame.mixer.Sound(base + f"{note}.wav")
            except pygame.error:
                print(f"Error loading sound file: {base}{note}.wav")

        # Load black notes
        for note in black_notes:
            try:
                self.sounds[note] = pygame.mixer.Sound(base + f"{note}.wav")
            except pygame.error:
                print(f"Error loading sound file: {base}{note}.wav")

    def create_white_keys(self):
        """
        Create a row of larger white keys, positioned slightly higher on the screen.
        """
        white_keys = [
            ("c4", "Q"), ("d4", "W"), ("e4", "E"), ("f4", "R"),
            ("g4", "T"), ("a4", "Y"), ("b4", "U"),
            ("c5", "I"), ("d5", "O"), ("e5", "P"), ("f5", "["),
            ("g5", "]"), ("a5", "\\"), ("b5", "1")
        ]
        num_white = len(white_keys)

        # Define key dimensions (make them larger)
        key_w = self.screen_w / 15.0  # Wider than previous
        key_h = self.screen_h / 3.0   # Taller than previous

        total_w = num_white * key_w
        x_start = (self.screen_w - total_w) / 2

        # Position keys slightly higher from the bottom (20% margin)
        margin_bottom = self.screen_h * 0.20
        y_pos = self.screen_h - key_h - margin_bottom

        for i, (note_name, shortcut) in enumerate(white_keys):
            x = x_start + i * key_w
            btn = QPushButton(note_name.upper(), self)
            btn.setObjectName(note_name)
            btn.setShortcut(shortcut)
            btn.setGeometry(QRect(int(x), int(y_pos), int(key_w), int(key_h)))
            btn.setStyleSheet("""
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid black;
                font-weight: bold;
                font-size: 24px;
            """)
            btn.clicked.connect(self.play_sound)
            self.keys_info.append((btn, note_name))

    def create_black_keys(self):
        """
        Create black keys slightly smaller in height and width, positioned above the white keys.
        """
        black_keys = [
            ("c40", "2"), ("d40", "3"), ("f40", "5"), ("g40", "6"), ("a40", "7"),
            ("c50", "8"), ("d50", "9"), ("f50", "0"), ("g50", "-"), ("a50", "=")
        ]

        white_key_w = self.screen_w / 15.0
        black_key_w = white_key_w * 0.5  # Slightly smaller than before
        black_key_h = self.screen_h / 4.5  # Reduced height

        num_white = 14
        total_white_w = num_white * white_key_w
        x_white_start = (self.screen_w - total_white_w) / 2
        margin_bottom = self.screen_h * 0.20
        y_white_pos = self.screen_h - (self.screen_h / 3.0) - margin_bottom
        y_black_pos = y_white_pos  # Align top with white keys

        # Offsets to position black keys between specific white keys
        offsets = [
            white_key_w*0.7,  white_key_w*1.7,  white_key_w*3.7,
            white_key_w*4.7,  white_key_w*5.7,  white_key_w*7.7,
            white_key_w*8.7,  white_key_w*10.7, white_key_w*11.7,
            white_key_w*12.7,
        ]

        for i, (note_name, shortcut) in enumerate(black_keys):
            x = x_white_start + offsets[i]
            btn = QPushButton(note_name.upper(), self)
            btn.setObjectName(note_name)
            btn.setShortcut(shortcut)
            btn.setGeometry(QRect(int(x), int(y_black_pos), int(black_key_w), int(black_key_h)))
            btn.setStyleSheet("""
                background-color: rgba(0, 0, 0, 220);
                border: 1px solid black;
                color: white;
                font-weight: bold;
                font-size: 20px;
            """)
            btn.clicked.connect(self.play_sound)
            self.keys_info.append((btn, note_name))

    def play_sound(self):
        """
        Play the sound associated with the piano key when clicked or triggered by finger touch.
        """
        note_name = self.sender().objectName()
        if note_name in self.sounds:
            self.sounds[note_name].play()

    def trigger_note_by_name(self, note_name):
        """
        Directly play a note by its name (used for fingertip-triggered notes).
        """
        if note_name in self.sounds:
            self.sounds[note_name].play()

    def update_camera(self):
        """
        Update the camera feed, process hand landmarks, detect finger touches on keys,
        and draw the hand skeleton overlay.
        """
        ret, frame = self.cap.read()
        if not ret:
            return

        # Flip the frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape

        # Process the frame with MediaPipe Hands
        results = self.hands.process(frame_rgb)

        # Initialize lists for skeleton data
        all_lines = []
        all_points = []

        # Set to keep track of currently touched notes
        current_touches = set()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract landmark coordinates
                pts = []
                for lm in hand_landmarks.landmark:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    pts.append((px, py))

                # Draw skeleton lines by connecting landmarks
                for (start_idx, end_idx) in self.HAND_CONNECTIONS:
                    (sx, sy) = pts[start_idx]
                    (ex, ey) = pts[end_idx]
                    all_lines.append([(sx, sy), (ex, ey)])

                # Store landmark points
                all_points.extend(pts)

                # Check each relevant fingertip for extension and collision with keys
                for tip_idx, pip_idx in zip(self.FINGER_TIPS, self.FINGER_PIPS):
                    tip_x, tip_y = pts[tip_idx]
                    pip_x, pip_y = pts[pip_idx]

                    # Determine if the finger is extended
                    if tip_y < pip_y:
                        # Only check for collision if finger is extended
                        for (btn, note_name) in self.keys_info:
                            rect = btn.geometry()
                            if (rect.left() <= tip_x <= rect.right() and
                                rect.top() <= tip_y <= rect.bottom()):
                                current_touches.add(note_name)

        # Debounce: Play notes only when newly touched
        newly_pressed = current_touches - self.active_notes
        for note in newly_pressed:
            self.trigger_note_by_name(note)

        # Update the set of active notes
        self.active_notes = current_touches

        # Update skeleton data in the overlay
        self.overlay_label.skeleton_data = all_lines
        self.overlay_label.points_data = all_points
        self.overlay_label.update()

        # Convert RGB frame back to BGR for display
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Convert to QImage and then to QPixmap
        qt_img = QImage(frame_bgr.data, w, h, w*3, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)

        # Stretch the pixmap to fill the camera_label, ignoring aspect ratio
        pixmap = pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(pixmap)

    def closeEvent(self, event):
        """
        Cleanup resources when the window is closed.
        """
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
        pygame.quit()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = ARPiano()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
