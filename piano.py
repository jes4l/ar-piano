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
    QApplication, QMainWindow, QLabel, QPushButton, QStatusBar,
    QComboBox, QSlider
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
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.skeleton_data = []
        self.points_data = []

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Skeleton lines in white
        pen_line = QPen(QColor(255, 255, 255, 200), 3)
        painter.setPen(pen_line)
        for line in self.skeleton_data:
            (x1, y1), (x2, y2) = line
            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))

        # Landmarks in red
        pen_points = QPen(QColor(255, 0, 0, 200), 6)
        painter.setPen(pen_points)
        for (px, py) in self.points_data:
            painter.drawPoint(QPoint(px, py))

class FlyingNote(QLabel):
    """
    Displays a random note image that moves for ~1 second, then self-destructs.
    """
    def __init__(self, parent, pixmap, start_x, start_y):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setPixmap(pixmap)
        self.move(start_x, start_y)
        self.show()

        self.lifetime_ms = 1000
        self.elapsed_ms = 0

        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(1.0, 3.0)
        self.vx = speed*math.cos(angle)
        self.vy = speed*math.sin(angle)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start(33)

    def update_position(self):
        self.elapsed_ms += 33
        if self.elapsed_ms >= self.lifetime_ms:
            self.update_timer.stop()
            self.deleteLater()
            return

        nx = self.x() + self.vx
        ny = self.y() + self.vy
        self.move(int(nx), int(ny))

class EffectOverlay(QLabel):
    """
    Transparent overlay above skeleton to hold FlyingNotes.
    """
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

class FallingTile(QLabel):
    """
    A tile that drops near the piano key.
    White note => tile is BLUE, Black note => tile is PINK.
    If Teach OFF => collisions-based scoring (no sound on collision).
    """
    def __init__(self, parent, piano, note_name, key_rect, fall_speed, x_offset=0):
        super().__init__(parent)
        self.piano = piano
        self.note_name = note_name
        self.key_rect = key_rect
        self.fall_speed = fall_speed
        self.is_finished = False

        tile_side = int(key_rect.width() * 0.7)
        self.resize(tile_side, tile_side)

        start_x = key_rect.x() + x_offset + (key_rect.width() - tile_side)//2
        start_y = -tile_side
        self.move(start_x, start_y)

        # Color the tile based on if note_name is white or black
        if note_name in piano.blackNoteNames:
            # pink
            self.fill_color = QColor(255, 105, 180, 180)  # hotpink-ish
        else:
            # blue
            self.fill_color = QColor(0, 128, 255, 180)

        self.border_color = QColor(0, 0, 0, 220)
        self.border_width = 3

        # margin for "close"
        self.margin_close = 50
        self.show()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.border_color, self.border_width)
        painter.setPen(pen)
        painter.setBrush(self.fill_color)
        painter.drawRect(self.rect())

    def update_position(self):
        if self.is_finished:
            return

        nx = self.x()
        ny = self.y() + self.fall_speed
        self.move(nx, ny)

        tile_bottom = ny + self.height()
        key_top = self.key_rect.y()

        # Collisions-based scoring if Teach OFF
        if self.piano.auto_play_muted:
            # Modified to handle list of collisions
            if not any(c['note_name'] == self.note_name for c in self.piano.collisions):
                if tile_bottom >= key_top - self.margin_close:
                    now_ms = int(time.time() * 1000)
                    self.piano.collisions.append({'note_name': self.note_name, 'ctime': now_ms})

        # If tile hits the key
        if tile_bottom >= key_top:
            # If Teach=ON => produce sound
            if not self.piano.auto_play_muted:
                self.piano.trigger_note_by_name(self.note_name, from_tile=True)
            self.is_finished = True

class TileOverlay(QLabel):
    """
    Overlay for auto-spawned tiles.
    """
    def __init__(self, parent, width, height, piano):
        super().__init__(parent)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.piano = piano
        self.tiles = []

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_tiles)
        self.update_timer.start(33)

    def spawnTile(self, note_name, fall_speed=4):
        active_count = sum(1 for t in self.tiles if t.note_name == note_name and not t.is_finished)
        x_offset = active_count * 20

        key_rect = None
        for (btn, nm) in self.piano.keys_info:
            if nm == note_name:
                key_rect = btn.geometry()
                break
        if not key_rect:
            return

        tile = FallingTile(self, self.piano, note_name, key_rect, fall_speed, x_offset)
        self.tiles.append(tile)

    def update_tiles(self):
        for t in self.tiles[:]:
            t.update_position()
            if t.is_finished:
                self.tiles.remove(t)
                t.deleteLater()

class ARPiano(QMainWindow):
    """
    AR Piano with:
     - Teach Toggle => collisions-based or auto-play
     - Real-time tempo slider (green->orange->red)
     - White note => tile is blue, black => tile is pink
     - Pressed key => highlight in yellow, revert to original color on release
     - Show Notes starts OFF, Teach starts ON, Tempo starts at 1.25
    """

    # We'll define the note sets for quick reference
    whiteNoteNames = {
        "c4","d4","e4","f4","g4","a4","b4",
        "c5","d5","e5","f5","g5","a5","b5"
    }
    blackNoteNames = {
        "c40","d40","f40","g40","a40","c50","d50","f50","g50","a50"
    }

    FINGER_TIPS = [8,12,16,20]
    FINGER_PIPS = [6,10,14,18]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AR Piano Teaching Machine")

        pygame.init()
        pygame.mixer.init()

        # *** MODIFICATION START ***
        # Initialize collisions as a list to handle multiple simultaneous collisions
        self.collisions = []  # List of dicts with 'note_name' and 'ctime'
        # *** MODIFICATION END ***

        self.tile_score_window_ms = 500

        # tempo factor start at 1.25 => medium
        self.tempoFactor = 1.25

        # We'll keep original style references for each key
        self.keyStyles = {}

        screen = QGuiApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.screen_w = rect.width()
        self.screen_h = rect.height()
        self.setGeometry(0,0,self.screen_w,self.screen_h)

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Warning: Could not open camera.")
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.screen_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.screen_h)

        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0,0,self.screen_w,self.screen_h)
        self.camera_label.setStyleSheet("background-color:black;")

        self.keys_info = []
        self.load_sounds()
        self.load_note_images()

        # Create keys
        self.create_white_keys()
        self.create_black_keys()

        self.setStatusBar(QStatusBar(self))

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS

        self.is_held = {}
        for (_, nm) in self.keys_info:
            self.is_held[nm] = False

        # overlays
        self.skeleton_overlay = SkeletonOverlay(self,self.screen_w,self.screen_h)
        self.skeleton_overlay.show()

        self.effects_overlay = EffectOverlay(self,self.screen_w,self.screen_h)
        self.effects_overlay.raise_()
        self.effects_overlay.show()

        self.tile_overlay = TileOverlay(self,self.screen_w,self.screen_h,piano=self)
        self.tile_overlay.raise_()
        self.tile_overlay.show()

        # camera update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        # toggles
        self.auto_play_muted = False  # Teach ON => normal auto-play
        self.createTeachToggleButton()

        self.show_notes = False  # start with no note labels
        self.createShowNotesToggleButton()

        # scoring
        self.score = 0
        self.scoreLabel = QLabel("Score: 0", self)
        self.scoreLabel.setStyleSheet("color:white;font-size:20px;")
        self.scoreLabel.setGeometry(20,10,200,40)
        self.scoreLabel.show()

        # tempo slider
        self.createTempoSlider()

        # music selection
        self.createMusicSelection()

    def load_sounds(self):
        base = "C:/Users/LLR User/Desktop/music/Sounds/"
        white_notes = [
            "c4","d4","e4","f4","g4","a4","b4",
            "c5","d5","e5","f5","g5","a5","b5"
        ]
        black_notes = [
            "c40","d40","f40","g40","a40",
            "c50","d50","f50","g50","a50"
        ]
        self.sounds = {}
        for note in white_notes + black_notes:
            try:
                self.sounds[note] = pygame.mixer.Sound(base + f"{note}.wav")
            except pygame.error:
                print(f"Could not load sound: {note}.wav")

    def load_note_images(self):
        self.notePixmaps = []
        for i in range(1,6):
            path = f"Assets/note{i}.png"
            pix = QPixmap(path)
            if not pix.isNull():
                self.notePixmaps.append(pix)
            else:
                print(f"Warning: Could not load {path}")

    def create_white_keys(self):
        white_keys = [
            ("c4","Q"), ("d4","W"), ("e4","E"), ("f4","R"),
            ("g4","T"), ("a4","Y"), ("b4","U"),
            ("c5","I"), ("d5","O"), ("e5","P"), ("f5","["),
            ("g5","]"), ("a5","\\"), ("b5","1")
        ]
        num_white = len(white_keys)
        key_w = self.screen_w/15.0
        key_h = self.screen_h/3.0
        total_w = num_white*key_w
        x_start = (self.screen_w - total_w)/2

        self.piano_x_start = x_start
        self.piano_total_w = total_w

        margin_bottom = self.screen_h*0.20
        y_pos = self.screen_h - key_h - margin_bottom

        base_white_style = """
            background-color: rgba(255, 255, 255, 220);
            border: 1px solid black;
            font-weight: bold;
            font-size: 24px;
        """
        for i, (note_name, shortcut) in enumerate(white_keys):
            x = x_start + i*key_w
            btn = QPushButton(note_name.upper(), self)
            btn.setObjectName(note_name)
            btn.setShortcut(shortcut)
            btn.setGeometry(QRect(int(x), int(y_pos), int(key_w), int(key_h)))
            btn.setStyleSheet(base_white_style)
            btn.clicked.connect(self.play_sound)
            self.keys_info.append((btn, note_name))

            # store original style
            self.keyStyles[note_name] = base_white_style

    def create_black_keys(self):
        black_keys = [
            ("c40","2"), ("d40","3"), ("f40","5"), ("g40","6"), ("a40","7"),
            ("c50","8"), ("d50","9"), ("f50","0"), ("g50","-"), ("a50","=")
        ]
        white_key_w = self.screen_w/15.0
        black_key_w = white_key_w*0.5
        black_key_h = self.screen_h/4.5

        num_white = 14
        total_white_w = num_white*white_key_w
        x_white_start = (self.screen_w - total_white_w)/2
        margin_bottom = self.screen_h*0.20
        y_white_pos = self.screen_h - (self.screen_h / 3.0) - margin_bottom

        base_black_style = """
            background-color: rgba(0, 0, 0, 220);
            border: 1px solid black;
            color: white;
            font-weight: bold;
            font-size: 20px;
        """
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
            btn.setGeometry(QRect(int(x), int(y_white_pos), int(black_key_w), int(black_key_h)))
            btn.setStyleSheet(base_black_style)
            btn.clicked.connect(self.play_sound)
            self.keys_info.append((btn, note_name))

            self.keyStyles[note_name] = base_black_style

    def createTeachToggleButton(self):
        """
        Teach Toggle:
        Teach ON => auto-play, tile collisions produce sound
        Teach OFF => collisions => no sound from collisions, user can press keys to produce sound
        """
        btn_w, btn_h = 200, 30
        padding_right = 20
        shift_right = 10
        x_pos = self.piano_x_start + self.piano_total_w - btn_w - padding_right + shift_right
        y_buttons = int(0.82 * self.screen_h)

        self.teachButton = QPushButton("Teach You To Play: ON", self)
        self.teachButton.setGeometry(int(x_pos), int(y_buttons), btn_w, btn_h)
        self.teachButton.setStyleSheet("""
            background-color: rgba(200, 200, 200, 200);
            font-size: 14px;
            font-weight: bold;
        """)
        self.teachButton.clicked.connect(self.toggleTeach)
        self.auto_play_muted = False  # Teach ON => normal auto-play

    def createShowNotesToggleButton(self):
        btn_w, btn_h = 200, 30
        padding_right = 20
        shift_right = 10
        x_pos = self.piano_x_start + self.piano_total_w - btn_w - padding_right + shift_right
        y_buttons = int(0.82 * self.screen_h) + 50

        self.showNotesButton = QPushButton("Show Notes: OFF", self)
        self.showNotesButton.setGeometry(int(x_pos), int(y_buttons), btn_w, btn_h)
        self.showNotesButton.setStyleSheet("""
            background-color: rgba(200, 200, 200, 200);
            font-size: 14px;
            font-weight: bold;
        """)
        self.showNotesButton.clicked.connect(self.toggleShowNotes)
        self.show_notes = False

        # Hide note labels on startup
        for (btn, nm) in self.keys_info:
            btn.setText("")

    def toggleTeach(self):
        self.auto_play_muted = not self.auto_play_muted
        if self.auto_play_muted:
            self.teachButton.setText("Teach You To Play: OFF")
        else:
            self.teachButton.setText("Teach You To Play: ON")

    def toggleShowNotes(self):
        self.show_notes = not self.show_notes
        if self.show_notes:
            self.showNotesButton.setText("Show Notes: ON")
        else:
            self.showNotesButton.setText("Show Notes: OFF")
        for (btn, nm) in self.keys_info:
            if self.show_notes:
                btn.setText(nm.upper())
            else:
                btn.setText("")

    def createTempoSlider(self):
        """
        Horizontal slider, range=50..200 => factor=0.5..2.0
        Starting at 125 => factor=1.25 => "medium"
        Green->orange->red sub-page color
        """
        self.tempoSlider = QSlider(Qt.Horizontal, self)
        self.tempoSlider.setRange(50, 200)
        self.tempoSlider.setValue(125)  # factor=1.25
        self.tempoSlider.setGeometry(80, self.screen_h - 120, 300, 30)
        self.tempoSlider.valueChanged.connect(self.onTempoSliderChanged)

        self.updateTempoSliderStyle(125)

    def onTempoSliderChanged(self, value):
        self.tempoFactor = value / 100.0
        self.updateTempoSliderStyle(value)

    def updateTempoSliderStyle(self, sliderVal):
        frac = (sliderVal - 50)/150.0
        green = (0,255,0)
        orange = (255,165,0)
        red = (255,0,0)

        def color_interpolate(c1,c2,t):
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            return (r,g,b)

        if frac < 0.5:
            subFrac = frac * 2.0
            c = color_interpolate(green, orange, subFrac)
        else:
            subFrac = (frac - 0.5) * 2.0
            c = color_interpolate(orange, red, subFrac)

        def rgb_to_hex(c):
            return "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])

        color_hex = rgb_to_hex(c)

        style = f"""
            QSlider::groove:horizontal {{
                border: 1px solid #bbb;
                background: #eee;
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66e, stop:1 #bbf
                );
                border: 1px solid #777;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::add-page:horizontal {{
                background: #fff;
            }}
            QSlider::sub-page:horizontal {{
                background: {color_hex};
                border-radius: 4px;
            }}
        """
        self.tempoSlider.setStyleSheet(style)

    def createMusicSelection(self):
        self.musicBox = QComboBox(self)
        self.musicBox.addItems(["Happy Birthday (basic)", "Interstellar (basic)"])
        box_w, box_h = 200, 30
        play_btn_w, play_btn_h = 200, 30
        total_width = box_w + 10 + play_btn_w
        x_box = (self.screen_w - total_width)/2
        y_buttons = int(0.82*self.screen_h)

        self.musicBox.setGeometry(int(x_box), int(y_buttons), box_w, box_h)
        self.playMusicButton = QPushButton("Play Selected Music", self)
        self.playMusicButton.setGeometry(int(x_box+box_w+10), int(y_buttons), play_btn_w, play_btn_h)
        self.playMusicButton.setStyleSheet("""
            background-color: rgba(200, 200, 200, 200);
            font-size: 14px;
            font-weight: bold;
        """)
        self.playMusicButton.clicked.connect(self.onPlayMusicClicked)

    def onPlayMusicClicked(self):
        s = self.musicBox.currentText()
        if "Happy Birthday" in s:
            melody = [
                ('g4',0),('g4',800),('a4',800),('g4',800),('c5',800),('b4',1000),
                ('g4',800),('g4',800),('a4',800),('g4',800),('d5',800),('c5',1000),
                ('g4',800),('g4',800),('g5',800),('e5',800),('c5',800),('b4',800),('a4',1200),
                ('f5',800),('f5',800),('e5',800),('c5',800),('d5',800),('c5',1000)
            ]
            self.playMelodyIteratively(melody)
        elif "Interstellar" in s:
            melody = [
                ('c4',0), ('g4',800), ('g4',800), ('a4',1000),
                ('g4',800), ('f4',800), ('e4',1200), ('e4',800),
                ('g4',800), ('g4',1000)
            ]
            self.playMelodyIteratively(melody)

    def playMelodyIteratively(self, melody):
        """
        Iterative scheduling => real-time tempo changes affect next note.
        """
        self.currentMelody = melody
        self.currentMelodyIndex = 0
        self.scheduleNextNote()

    def scheduleNextNote(self):
        if self.currentMelodyIndex >= len(self.currentMelody):
            return
        note_name, delta = self.currentMelody[self.currentMelodyIndex]
        self.currentMelodyIndex += 1

        # spawn tile for this note
        self.tile_overlay.spawnTile(note_name, 4)

        if self.currentMelodyIndex < len(self.currentMelody):
            next_delta = self.currentMelody[self.currentMelodyIndex][1]
            QTimer.singleShot(int(next_delta / self.tempoFactor), self.scheduleNextNote)

    def play_sound(self):
        note_name = self.sender().objectName()
        self.trigger_note_by_name(note_name)

    def trigger_note_by_name(self, note_name, from_tile=False):
        """
        Handles playing sounds and scoring logic based on teach mode.
        """

        current_ms = int(time.time() * 1000)

        # 1) If the note is triggered by a falling tile and Teach is ON
        if from_tile and not self.auto_play_muted:
            if note_name in self.sounds:
                self.sounds[note_name].play()
            return

        # 2) If the user presses a key and Teach is OFF (manual scoring)
        if not from_tile and self.auto_play_muted:
            # Always play the sound when pressing a key
            if note_name in self.sounds:
                self.sounds[note_name].play()

            if not self.collisions:
                # No notes in proximity, penalize
                self.addScore(-5)
            else:
                matched_collision = None
                for collision in self.collisions:
                    if collision['note_name'] == note_name:
                        if current_ms - collision['ctime'] <= self.tile_score_window_ms:
                            matched_collision = collision
                            break

                if matched_collision:
                    self.addScore(10)
                    self.collisions.remove(matched_collision)
                else:
                    # Wrong key pressed while a note is in proximity
                    self.addScore(-5)

            # Always spawn a flying note for visual feedback
            self.spawnFlyingNoteOnKey(note_name)
            return

        # 3) If the user presses a key and Teach is ON
        if not from_tile and not self.auto_play_muted:
            if note_name in self.sounds:
                self.sounds[note_name].play()
            self.spawnFlyingNoteOnKey(note_name)
            return

    def spawnFlyingNoteOnKey(self, note_name):
        # find button
        for (btn, nm) in self.keys_info:
            if nm == note_name:
                self.spawnFlyingNote(btn)
                break

    def addScore(self, points):
        self.score += points
        if self.score < 0:
            self.score = 0
        self.scoreLabel.setText(f"Score: {self.score}")

    def spawnFlyingNote(self, btn):
        if not self.notePixmaps:
            return
        pix_original = random.choice(self.notePixmaps)
        sf = random.uniform(0.5,1.2)
        sw = int(pix_original.width()*sf)
        sh = int(pix_original.height()*sf)
        pix_scaled = pix_original.scaled(sw, sh, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        r = btn.geometry()
        cx = r.x() + r.width()//2
        cy = r.y() + r.height()//2
        offx = random.randint(-r.width()//2, r.width()//2)
        offy = random.randint(-r.height()//2, r.height()//2)
        sx = cx+offx - sw//2
        sy = cy+offy - sh//2

        note_label = FlyingNote(self.effects_overlay, pix_scaled, sx, sy)
        self.effects_overlay.raise_()

    def update_camera(self):
        # Capture
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame,1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h,w,_ = frame_rgb.shape

        results = self.hands.process(frame_rgb)

        all_lines = []
        all_points = []
        touched_now = set()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                pts = []
                for lm in hand_landmarks.landmark:
                    px=int(lm.x*w)
                    py=int(lm.y*h)
                    pts.append((px,py))

                # skeleton
                for (start_idx,end_idx) in self.HAND_CONNECTIONS:
                    sx,sy=pts[start_idx]
                    ex,ey=pts[end_idx]
                    all_lines.append([(sx,sy),(ex,ey)])
                all_points.extend(pts)

                # check fingertip extended
                for tip_idx,pip_idx in zip(self.FINGER_TIPS,self.FINGER_PIPS):
                    tip_x,tip_y=pts[tip_idx]
                    pip_x,pip_y=pts[pip_idx]
                    if tip_y < pip_y:
                        # fingertip extended => see if on a key
                        for (btn,nm) in self.keys_info:
                            r=btn.geometry()
                            if (r.left()<=tip_x<=r.right() and
                                r.top()<=tip_y<=r.bottom()):
                                touched_now.add(nm)

        # highlight pressed keys in YELLOW, revert others
        for (btn,nm) in self.keys_info:
            if nm in touched_now:
                if not self.is_held[nm]:
                    # trigger note
                    self.trigger_note_by_name(nm)
                    self.is_held[nm]=True
                # set style => pressed
                btn.setStyleSheet("background-color: yellow; border: 2px solid black; font-weight: bold;")
            else:
                if self.is_held[nm]:
                    # key was released
                    self.is_held[nm]=False
                # revert style to original
                btn.setStyleSheet(self.keyStyles[nm])

        # Handle missed notes
        if self.auto_play_muted:
            current_ms=int(time.time()*1000)
            to_remove = []
            for collision in self.collisions:
                if current_ms - collision['ctime'] > self.tile_score_window_ms:
                    self.addScore(-2)
                    to_remove.append(collision)
            for collision in to_remove:
                self.collisions.remove(collision)

        self.skeleton_overlay.skeleton_data = all_lines
        self.skeleton_overlay.points_data = all_points
        self.skeleton_overlay.update()

        # show camera
        frame_bgr=cv2.cvtColor(frame_rgb,cv2.COLOR_RGB2BGR)
        qt_img=QImage(frame_bgr.data,w,h,w*3,QImage.Format_BGR888)
        pixmap=QPixmap.fromImage(qt_img)
        pixmap=pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
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

if __name__=="__main__":
    main()
