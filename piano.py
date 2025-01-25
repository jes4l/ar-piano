import sys
import cv2
import mediapipe as mp
import pygame
import random
import math

from PyQt5.QtGui import (
    QImage, QPixmap, QGuiApplication, QPainter, QPen, QColor
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QStatusBar
)
from PyQt5.QtCore import QTimer, QRect, Qt, QPoint

class SkeletonOverlay(QLabel):
    """
    A transparent overlay widget that draws the hand skeleton on top of everything (piano + camera).
    """
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        # Let mouse events pass through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.skeleton_data = []  # line segments: [((x1, y1), (x2, y2)), ...]
        self.points_data = []    # landmark points: [(x, y), ...]

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw skeleton connections (white lines)
        pen_line = QPen(QColor(255, 255, 255, 200), 3)
        painter.setPen(pen_line)
        for line in self.skeleton_data:
            (x1, y1), (x2, y2) = line
            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))

        # Draw landmark points (red circles)
        pen_points = QPen(QColor(255, 0, 0, 200), 6)
        painter.setPen(pen_points)
        for (px, py) in self.points_data:
            painter.drawPoint(QPoint(px, py))


class FlyingNote(QLabel):
    """
    A QLabel that displays a random note image and smoothly moves in a random direction,
    then destroys itself after 1 second.
    """
    def __init__(self, parent, pixmap, start_x, start_y):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setPixmap(pixmap)
        self.move(start_x, start_y)
        self.show()

        # Keep track of time
        self.lifetime_ms = 1000  # 1 second
        self.elapsed_ms = 0

        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 3.0)  # pixels per update
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

        # Timer for movement updates (about ~30 fps => 33ms)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start(33)

    def update_position(self):
        self.elapsed_ms += 33
        if self.elapsed_ms >= self.lifetime_ms:
            # Time to destroy
            self.update_timer.stop()
            self.deleteLater()
            return

        # Move by velocity
        x = self.x() + self.vx
        y = self.y() + self.vy
        self.move(int(x), int(y))


class EffectOverlay(QLabel):
    """
    Another transparent overlay widget that sits on top of everything (including skeleton).
    Used to host FlyingNote labels so they appear above all other widgets.
    """
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        # Also pass mouse events through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)


class ARPiano(QMainWindow):
    """
    AR Piano that:
    - Shows webcam feed in the background.
    - Overlays piano keys near the bottom.
    - Tracks fingertips (index, middle, ring, pinky) with MediaPipe for note triggers.
    - Draws skeleton with a SkeletonOverlay.
    - Spawns FlyingNote objects in an EffectOverlay on top, which move & vanish after 1s.
    """

    # Fingertips & PIPs
    FINGER_TIPS =  [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS =  [6, 10, 14, 18]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AR Piano + Flying Notes")

        # 1) Initialize Pygame mixer
        pygame.init()
        pygame.mixer.init()

        # 2) Dict for {note_name: Sound}
        self.sounds = {}

        # 3) Detect screen size
        screen = QGuiApplication.primaryScreen()
        geometry = screen.availableGeometry()
        self.screen_w = geometry.width()
        self.screen_h = geometry.height()

        # 4) Fill window
        self.setGeometry(0, 0, self.screen_w, self.screen_h)

        # 5) Camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Warning: Could not open camera.")
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.screen_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.screen_h)

        # 6) Label for camera
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, self.screen_w, self.screen_h)
        self.camera_label.setStyleSheet("background-color: black;")

        # 7) Load sounds & note images
        self.load_sounds()
        self.load_note_images()

        # 8) Piano keys
        self.keys_info = []
        self.create_white_keys()
        self.create_black_keys()

        # 9) Status bar
        self.setStatusBar(QStatusBar(self))

        # 10) MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS

        # 11) Debounce set
        self.active_notes = set()

        # 12) Skeleton overlay
        self.skeleton_overlay = SkeletonOverlay(self, self.screen_w, self.screen_h)
        self.skeleton_overlay.show()

        # 13) Effects overlay (on top of skeleton)
        self.effects_overlay = EffectOverlay(self, self.screen_w, self.screen_h)
        self.effects_overlay.raise_()  # ensure it's on top
        self.effects_overlay.show()

        # 14) Timer for camera updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

    def load_sounds(self):
        base = "C:/Users/LLR User/Desktop/music/Sounds/"
        white_notes = ["c4","d4","e4","f4","g4","a4","b4","c5","d5","e5","f5","g5","a5","b5"]
        black_notes = ["c40","d40","f40","g40","a40","c50","d50","f50","g50","a50"]

        for note in white_notes + black_notes:
            try:
                self.sounds[note] = pygame.mixer.Sound(base + f"{note}.wav")
            except pygame.error:
                print(f"Could not load sound: {note}.wav")

    def load_note_images(self):
        """
        Load Assets/note1.png..note5.png into a list.
        """
        self.notePixmaps = []
        for i in range(1, 6):
            path = f"Assets/note{i}.png"
            pix = QPixmap(path)
            if not pix.isNull():
                self.notePixmaps.append(pix)
            else:
                print(f"Warning: Could not load {path}")

    def create_white_keys(self):
        white_keys = [
            ("c4", "Q"), ("d4", "W"), ("e4", "E"), ("f4", "R"),
            ("g4", "T"), ("a4", "Y"), ("b4", "U"),
            ("c5", "I"), ("d5", "O"), ("e5", "P"), ("f5", "["),
            ("g5", "]"), ("a5", "\\"), ("b5", "1")
        ]
        num_white = len(white_keys)
        key_w = self.screen_w / 15.0
        key_h = self.screen_h / 3.0
        total_w = num_white * key_w
        x_start = (self.screen_w - total_w) / 2

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
        black_keys = [
            ("c40", "2"), ("d40", "3"), ("f40", "5"), ("g40", "6"), ("a40", "7"),
            ("c50", "8"), ("d50", "9"), ("f50", "0"), ("g50", "-"), ("a50", "=")
        ]
        white_key_w = self.screen_w / 15.0
        black_key_w = white_key_w * 0.5
        black_key_h = self.screen_h / 4.5

        num_white = 14
        total_white_w = num_white * white_key_w
        x_white_start = (self.screen_w - total_white_w) / 2
        margin_bottom = self.screen_h * 0.20
        y_white_pos = self.screen_h - (self.screen_h / 3.0) - margin_bottom
        y_black_pos = y_white_pos

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
        # Called when key is clicked
        note_name = self.sender().objectName()
        self.trigger_note_by_name(note_name)

    def trigger_note_by_name(self, note_name):
        # Plays note & spawns flying note
        if note_name in self.sounds:
            self.sounds[note_name].play()

        # Find button geometry
        for (btn, name) in self.keys_info:
            if name == note_name:
                self.spawnFlyingNote(btn)
                break

    def spawnFlyingNote(self, btn):
        """
        Creates a random note image, scaled randomly, and places a FlyingNote
        in the effects_overlay. The note label moves in a random direction, then vanishes.
        """
        if not self.notePixmaps:
            return
        pix_original = random.choice(self.notePixmaps)

        # random scale
        scale_factor = random.uniform(0.5, 1.2)
        scaled_w = int(pix_original.width() * scale_factor)
        scaled_h = int(pix_original.height() * scale_factor)
        pix_scaled = pix_original.scaled(scaled_w, scaled_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # position near the button center
        rect = btn.geometry()
        center_x = rect.x() + rect.width()//2
        center_y = rect.y() + rect.height()//2

        # random offset
        off_x = random.randint(-rect.width()//2, rect.width()//2)
        off_y = random.randint(-rect.height()//2, rect.height()//2)
        start_x = center_x + off_x - scaled_w//2
        start_y = center_y + off_y - scaled_h//2

        # Create a flying note label inside the effects_overlay
        note_label = FlyingNote(self.effects_overlay, pix_scaled, start_x, start_y)
        # The note_label raises itself automatically, but let's ensure overlay is on top
        self.effects_overlay.raise_()

    def update_camera(self):
        """
        Grab frame, flip horizontally, process with MediaPipe, do skeleton + fingertip collision.
        Update skeleton overlay. Show feed in camera_label.
        """
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape

        results = self.hands.process(frame_rgb)

        all_lines = []
        all_points = []
        current_touches = set()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Convert landmarks to pixel coords
                pts = []
                for lm in hand_landmarks.landmark:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    pts.append((px, py))

                # Build skeleton lines
                for (start_idx, end_idx) in self.HAND_CONNECTIONS:
                    sx, sy = pts[start_idx]
                    ex, ey = pts[end_idx]
                    all_lines.append([(sx, sy), (ex, ey)])
                all_points.extend(pts)

                # Fingertip collision if extended
                for tip_idx, pip_idx in zip(self.FINGER_TIPS, self.FINGER_PIPS):
                    tip_x, tip_y = pts[tip_idx]
                    pip_x, pip_y = pts[pip_idx]
                    if tip_y < pip_y:  # extended
                        # Collision check
                        for (btn, note_name) in self.keys_info:
                            rect = btn.geometry()
                            if (rect.left() <= tip_x <= rect.right() and
                                rect.top() <= tip_y <= rect.bottom()):
                                current_touches.add(note_name)

        # Debounce
        newly_pressed = current_touches - self.active_notes
        for note in newly_pressed:
            self.trigger_note_by_name(note)

        self.active_notes = current_touches

        # Update skeleton overlay
        self.skeleton_overlay.skeleton_data = all_lines
        self.skeleton_overlay.points_data = all_points
        self.skeleton_overlay.update()

        # Show camera feed
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        qt_img = QImage(frame_bgr.data, w, h, w*3, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)
        pixmap = pixmap.scaled(self.camera_label.width(),
                               self.camera_label.height(),
                               Qt.IgnoreAspectRatio,
                               Qt.SmoothTransformation)
        self.camera_label.setPixmap(pixmap)

    def closeEvent(self, event):
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
