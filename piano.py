import sys
import cv2
import mediapipe as mp
import pygame
import random
import math
import time

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
        self.points_data = []    # list of (x, y)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # For demonstration: draw lines in white, points in red
        pen_line = QPen(QColor(255, 255, 255, 200), 3)
        painter.setPen(pen_line)
        for line in self.skeleton_data:
            (x1, y1), (x2, y2) = line
            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))

        pen_points = QPen(QColor(255, 0, 0, 200), 6)
        painter.setPen(pen_points)
        for (px, py) in self.points_data:
            painter.drawPoint(QPoint(px, py))


class FlyingNote(QLabel):
    """
    A QLabel that displays a random note image and moves in a random direction,
    then destroys itself after 1 second.
    """
    def __init__(self, parent, pixmap, start_x, start_y):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setPixmap(pixmap)
        self.move(start_x, start_y)
        self.show()

        # 1-second lifetime
        self.lifetime_ms = 1000
        self.elapsed_ms = 0

        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 3.0)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start(33)  # ~30 FPS

    def update_position(self):
        self.elapsed_ms += 33
        if self.elapsed_ms >= self.lifetime_ms:
            self.update_timer.stop()
            self.deleteLater()
            return

        # Move
        nx = self.x() + self.vx
        ny = self.y() + self.vy
        self.move(int(nx), int(ny))


class EffectOverlay(QLabel):
    """
    A transparent overlay (above skeleton) to host FlyingNote objects so they appear on top.
    """
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        # Let mouse events pass through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)


class FallingTile(QLabel):
    """
    A simple colored rectangle that falls from the top and aligns with a given piano key.
    Once it intersects the key region, it plays the note, then we remove it.
    """
    def __init__(self, parent, piano, note_name, key_rect, fall_speed):
        super().__init__(parent)
        self.piano = piano
        self.note_name = note_name
        self.key_rect = key_rect
        self.fall_speed = fall_speed
        self.is_finished = False

        # We'll make the tile bigger in height so it holds the note visually
        tile_width = self.key_rect.width()
        tile_height = self.key_rect.height() * 1.5  # 50% taller
        self.resize(tile_width, int(tile_height))

        # Start from top (negative y) so it drops in from "ceiling"
        start_x = self.key_rect.x()
        start_y = -tile_height
        self.move(int(start_x), int(start_y))

        # We'll pick a color for fun
        self.color = QColor(0, 180, 255, 180)  # semi-transparent blue
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.NoPen)
        painter.setPen(pen)
        painter.setBrush(self.color)
        painter.drawRect(self.rect())

    def update_position(self):
        if self.is_finished:
            return
        # Move down
        nx = self.x()
        ny = self.y() + self.fall_speed
        self.move(nx, ny)

        # Check if we intersect the key
        tile_bottom = ny + self.height()
        key_top = self.key_rect.y()

        if tile_bottom >= key_top:
            # Trigger note (once)
            self.piano.trigger_note_by_name(self.note_name)
            self.is_finished = True


class TileOverlay(QLabel):
    """
    Overlay for dropping piano tiles that auto-play notes for a simple 'Happy Birthday' demo.
    """
    def __init__(self, parent, width, height, piano):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.piano = piano  # reference to ARPiano for note triggers, key info
        self.tiles = []

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_tiles)
        self.update_timer.start(33)  # ~30 FPS

    def spawnTile(self, note_name, fall_speed=4):
        # Find the key geometry for this note
        btn_rect = None
        for (btn, nm) in self.piano.keys_info:
            if nm == note_name:
                btn_rect = btn.geometry()
                break
        if not btn_rect:
            return

        tile = FallingTile(self, self.piano, note_name, btn_rect, fall_speed)
        self.tiles.append(tile)

    def update_tiles(self):
        # Move all active tiles
        for tile in self.tiles[:]:
            tile.update_position()
            if tile.is_finished:
                self.tiles.remove(tile)
                tile.deleteLater()


class ARPiano(QMainWindow):
    """
    AR Piano that:
    - Displays a webcam feed in the background.
    - Overlays piano keys near the bottom.
    - Tracks fingertips (index, middle, ring, pinky) with MediaPipe for note triggers.
    - Draws skeleton overlay above the keys.
    - Spawns FlyingNote objects in an EffectOverlay on top (move & vanish after 1s).
    - Auto-plays 'Happy Birthday' via TileOverlay (falling rectangles).
    - Uses "touch-lift" logic to avoid repeated triggers while fingertip remains in same key area.
    """

    FINGER_TIPS =  [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS =  [6, 10, 14, 18]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AR Piano")

        # 1) Initialize Pygame
        pygame.init()
        pygame.mixer.init()

        # 2) Dictionary for {note_name: Sound}
        self.sounds = {}

        # 3) Screen size
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

        # 6) Camera label
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, self.screen_w, self.screen_h)
        self.camera_label.setStyleSheet("background-color: black;")

        # 7) Load sounds & note images
        self.load_sounds()
        self.load_note_images()

        # 8) Create piano keys
        self.keys_info = []
        self.create_white_keys()
        self.create_black_keys()

        # 9) Status bar
        self.setStatusBar(QStatusBar(self))

        # 10) MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS

        # 11) "Touch-lift" tracking:
        # We'll store whether each note is currently "held" (finger remains in bounding box).
        # Once "held", we won't re-trigger until the fingertip leaves (is_held=False).
        self.is_held = {}  # {note_name: bool}
        for (_, nm) in self.keys_info:
            self.is_held[nm] = False

        # 12) Skeleton overlay
        self.skeleton_overlay = SkeletonOverlay(self, self.screen_w, self.screen_h)
        self.skeleton_overlay.show()

        # 13) Effects overlay (FlyingNotes)
        self.effects_overlay = EffectOverlay(self, self.screen_w, self.screen_h)
        self.effects_overlay.raise_()
        self.effects_overlay.show()

        # 14) Tile overlay for auto-play
        self.tile_overlay = TileOverlay(self, self.screen_w, self.screen_h, piano=self)
        self.tile_overlay.raise_()
        self.tile_overlay.show()

        # 15) Timer for camera
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        # 16) Schedule 'Happy Birthday' after 2s
        QTimer.singleShot(2000, self.spawnHappyBirthdayTiles)

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
        """Called when user clicks on a key (mouse or keyboard)."""
        note_name = self.sender().objectName()
        self.trigger_note_by_name(note_name)

    def trigger_note_by_name(self, note_name):
        """
        Actually play the note + spawn flying note effect.
        """
        if note_name in self.sounds:
            self.sounds[note_name].play()

        for (btn, nm) in self.keys_info:
            if nm == note_name:
                self.spawnFlyingNote(btn)
                break

    def spawnFlyingNote(self, btn):
        if not self.notePixmaps:
            return
        pix_original = random.choice(self.notePixmaps)
        scale_factor = random.uniform(0.5, 1.2)
        sw = int(pix_original.width() * scale_factor)
        sh = int(pix_original.height() * scale_factor)
        pix_scaled = pix_original.scaled(sw, sh, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        rect = btn.geometry()
        cx = rect.x() + rect.width()//2
        cy = rect.y() + rect.height()//2
        offx = random.randint(-rect.width()//2, rect.width()//2)
        offy = random.randint(-rect.height()//2, rect.height()//2)
        sx = cx + offx - sw//2
        sy = cy + offy - sh//2

        note_label = FlyingNote(self.effects_overlay, pix_scaled, sx, sy)
        self.effects_overlay.raise_()

    def update_camera(self):
        """
        1) Capture webcam
        2) Flip horizontally
        3) Mediapipe -> find hands
        4) For each fingertip, if extended, see if it's in a bounding box
        5) Use "touch-lift" approach: if note is "held" => skip. If not held => trigger once, mark held.
           Then if finger not in bounding box => mark released => next time can trigger again
        6) Update skeleton overlay, display feed
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

        # We'll track which notes are currently touched THIS FRAME
        touched_now = set()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # convert to pixel coords
                pts = []
                for lm in hand_landmarks.landmark:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    pts.append((px, py))

                # skeleton lines
                for (start_idx, end_idx) in self.HAND_CONNECTIONS:
                    sx, sy = pts[start_idx]
                    ex, ey = pts[end_idx]
                    all_lines.append([(sx, sy), (ex, ey)])
                all_points.extend(pts)

                # check fingertips
                for tip_idx, pip_idx in zip(self.FINGER_TIPS, self.FINGER_PIPS):
                    tip_x, tip_y = pts[tip_idx]
                    pip_x, pip_y = pts[pip_idx]
                    # if finger extended
                    if tip_y < pip_y:
                        # collision with keys
                        for (btn, nm) in self.keys_info:
                            rect = btn.geometry()
                            if (rect.left() <= tip_x <= rect.right() and
                                rect.top() <= tip_y <= rect.bottom()):
                                touched_now.add(nm)

        # "Touch-lift" approach:
        # For every note that is touched_now, if is_held[note] == False, we trigger and set is_held[note] = True
        # For every note that is not touched_now but was is_held[note] == True, we set is_held[note] = False
        for (btn, nm) in self.keys_info:
            if nm in touched_now:
                # being touched
                if not self.is_held[nm]:
                    # wasn't held => trigger once
                    self.trigger_note_by_name(nm)
                    self.is_held[nm] = True
            else:
                # not being touched
                if self.is_held[nm]:
                    # release
                    self.is_held[nm] = False

        # Skeleton overlay
        self.skeleton_overlay.skeleton_data = all_lines
        self.skeleton_overlay.points_data = all_points
        self.skeleton_overlay.update()

        # show camera
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        qt_img = QImage(frame_bgr.data, w, h, w*3, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)
        pixmap = pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(pixmap)

    def spawnHappyBirthdayTiles(self):
        """
        Spawns a simple sequence of tiles for 'Happy Birthday'.
        """
        # Basic 'Happy Birthday' melody in c-majorish
        melody = [
            ('g4', 0),    ('g4', 800),  ('a4', 800), ('g4', 800), ('c5', 800), ('b4', 1000),
            ('g4', 800),  ('g4', 800),  ('a4', 800), ('g4', 800), ('d5', 800), ('c5', 1000),
            ('g4', 800),  ('g4', 800),  ('g5', 800), ('e5', 800), ('c5', 800), ('b4', 800), ('a4', 1200),
            ('f5', 800),  ('f5', 800),  ('e5', 800), ('c5', 800), ('d5', 800), ('c5', 1000)
        ]
        current_time = 0
        for (note_name, delta) in melody:
            current_time += delta
            QTimer.singleShot(current_time, lambda n=note_name: self.tile_overlay.spawnTile(n, fall_speed=4))

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
