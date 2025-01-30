# AR Piano

![AR Piano Demo](ScreenRecording2025-01-26111222-ezgif.com-optimize%20(1)-min.gif)

This is my project that won the 3rd Overall at [PlyHack 25](https://allhackathons.com/hackathon/plymhack/) and here is my [devpost(https://devpost.com/software/ar-piano-teaching-machine).

This Augmented Reality Piano uses real-time hand tracking via MediaPipe to detect finger extension state for both hands, allowing users to interact with virtual keys through gestures. The PyQt5-based interface overlays a piano keyboard (24 keys: 14 white, 10 black) on a live camera feed processed by OpenCV, with Pygame handling audio playback of preloaded WAV samples. A toggle button dynamically shows/hides note labels on the keys.

Falling tiles are colour-coded (blue for white keys, pink for black keys) so you recognise which key to hit.

There are 2 modes, Teaching Mode ON and OFF:

- Teaching Mode ON: Falling tiles auto-play keys to teach melodies such as Happy Birthday and Interstellar using event-driven scheduling.

- Teaching Mode OFF: Falling tiles do not auto-play keys. Users score points +10 for hits, -5 for incorrect key hits and -2 for misses by aligning key presses with falling tiles within a tolerance window.

The tempo slider can be used to adjust the tile speed upon generation between 0.5-2.0 times so you can learn based on your ability.

Flying notes are animated particles emanating from pressed keys which show if your key hit has been successful.

