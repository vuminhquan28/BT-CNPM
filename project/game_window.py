import arcade
import time

from arcade.draw import draw_lrbt_rectangle_filled

from note import Note
from beatmap import Beatmap

import state


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PERFECT_Y = 120


LANE_X = {
    "left": 250,
    "down": 350,
    "up": 450,
    "right": 550
}


volumes = {
    "Perfect": 0.4,
    "Great": 0.5,
    "Good": 0.4,
}


# ================= UI =================

class UI:

    def __init__(self):

        self.score = 0
        self.combo = 0

    def draw(self):

        arcade.draw_text(
            f"Score: {self.score}",
            20,
            560,
            arcade.color.WHITE,
            18,
            bold=True
        )

        arcade.draw_text(
            f"Combo: {self.combo}",
            20,
            530,
            arcade.color.WHITE,
            18,
            bold=True
        )


# ================= HIT EFFECT =================

class HitEffect:

    def __init__(self, x, y, result):

        self.result = result

        self.timer = 0.5

        self.x = x
        self.y = y

        self.scale = 1.0

        colors = {
            "Perfect": arcade.color.GOLD,
            "Great": arcade.color.GREEN,
            "Good": arcade.color.BLUE,
            "Miss": arcade.color.RED
        }

        self.base_color = colors[result]

        self.text = arcade.Text(
            result,
            x,
            y,
            self.base_color,
            20,
            anchor_x="center"
        )

    def update(self, dt):

        self.timer -= dt

        self.y += 80 * dt

        self.scale += dt * 1.5

        alpha = int(255 * max(self.timer / 0.5, 0))

        self.text.color = (*self.base_color[:3], alpha)

        self.text.y = self.y

        self.text.font_size = int(20 * self.scale)

    def draw(self):

        if self.timer > 0:
            self.text.draw()


# ================= GAME =================

class GameWindow(arcade.Window):

    def __init__(self):

        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            "Rhythm Game"
        )

        arcade.set_background_color(arcade.color.BLACK)

        self.state = state.MENU

        self.notes = arcade.SpriteList()

        self.pending_notes = []

        self.effects = []

        self.ui = UI()

        self.start_time = 0

        # ================= SONG LIST =================

        self.songs = [

            {
                "name": "Song 1",
                "file": "assets/sounds/song1.mp3",
                "bg": "assets/images/bg1.png",
                "bpm": 120,
                "duration": 60
            },

            {
                "name": "Song 2",
                "file": "assets/sounds/song2.mp3",
                "bg": "assets/images/bg2.png",
                "bpm": 140,
                "duration": 75
            }
        ]

        self.selected_song_index = 0

        self.background = None

        # ================= SOUND EFFECT =================

        self.hit_sounds = {

            "Perfect": arcade.load_sound("assets/sounds/perfect.mp3"),

            "Great": arcade.load_sound("assets/sounds/great.mp3"),

            "Good": arcade.load_sound("assets/sounds/good.mp3"),

            "Miss": arcade.load_sound("assets/sounds/miss.mp3"),
        }

    # ================= SETUP GAME =================

    def setup_game(self, song):

        self.notes = arcade.SpriteList()

        self.ui.score = 0
        self.ui.combo = 0

        self.bpm = song["bpm"]

        self.beat_interval = 60 / self.bpm

        self.beatmap = Beatmap(
            self.bpm,
            duration=song["duration"]
        )

        self.pending_notes = self.beatmap.get_notes()

        self.start_time = time.time()

        self.last_beat_time = 0

        # ===== LOAD BACKGROUND =====

        self.background = arcade.load_texture(song["bg"])

        # ===== PLAY MUSIC =====

        arcade.play_sound(
            arcade.load_sound(song["file"])
        )

        self.state = state.PLAYING

    # ================= DRAW =================

    def on_draw(self):

        self.clear()

        # ================= MENU =================

        if self.state == state.MENU:

            arcade.draw_text(
                "RHYTHM GAME",
                240,
                350,
                arcade.color.WHITE,
                36,
                bold=True
            )

            arcade.draw_text(
                "Press ENTER",
                300,
                280,
                arcade.color.GRAY,
                22
            )

        # ================= SONG SELECT =================

        elif self.state == state.SONG_SELECT:

            arcade.draw_text(
                "SELECT SONG",
                260,
                450,
                arcade.color.WHITE,
                32,
                bold=True
            )

            for i, song in enumerate(self.songs):

                color = arcade.color.YELLOW if i == self.selected_song_index else arcade.color.WHITE

                arcade.draw_text(
                    song["name"],
                    320,
                    340 - i * 50,
                    color,
                    24
                )

        # ================= PLAYING =================

        elif self.state == state.PLAYING:

            # ===== BACKGROUND =====

            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(
                    0,
                    0,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )
            )

            # ===== DARK OVERLAY =====

            arcade.draw_lrbt_rectangle_filled(
                0,
                SCREEN_WIDTH,
                0,
                SCREEN_HEIGHT,
                (0, 0, 0, 120)
            )

            # ===== LANES =====

            for x in LANE_X.values():
                arcade.draw_lrbt_rectangle_filled(
                    x - 40,
                    x + 40,
                    0,
                    SCREEN_HEIGHT,
                    (255, 255, 255, 40)
                )

                arcade.draw_line(
                    x - 40,
                    0,
                    x - 40,
                    SCREEN_HEIGHT,
                    arcade.color.WHITE,
                    2
                )

                arcade.draw_line(
                    x + 40,
                    0,
                    x + 40,
                    SCREEN_HEIGHT,
                    arcade.color.WHITE,
                    2
                )

            # ===== HIT LINE =====

            draw_lrbt_rectangle_filled(
                200,
                600,
                PERFECT_Y - 8,
                PERFECT_Y + 8,
                arcade.color.YELLOW
            )

            # ===== NOTES =====

            self.notes.draw()

            # ===== UI =====

            self.ui.draw()

            # ===== EFFECT =====

            for e in self.effects:
                e.draw()

    # ================= UPDATE =================

    def on_update(self, delta_time):

        if self.state != state.PLAYING:
            return

        current_time = time.time() - self.start_time

        # ===== SPAWN NOTES =====

        for n in list(self.pending_notes):

            if current_time >= n["time"]:

                note = Note(
                    n["key"],
                    n["time"],
                    LANE_X[n["key"]],
                    SCREEN_HEIGHT
                )

                self.notes.append(note)

                self.pending_notes.remove(n)

        self.notes.update(delta_time)

        # ===== UPDATE EFFECTS =====

        for e in self.effects:
            e.update(delta_time)

        self.effects = [
            e for e in self.effects
            if e.timer > 0
        ]

        # ===== AUTO MISS =====

        for note in self.notes:

            if not note.hit and note.center_y < PERFECT_Y - 40:

                note.hit = True

                note.remove_from_sprite_lists()

                self.ui.combo = 0

                self.effects.append(
                    HitEffect(
                        note.center_x,
                        PERFECT_Y,
                        "Miss"
                    )
                )

                arcade.play_sound(
                    self.hit_sounds["Miss"],
                    volume=0.4
                )

        # ===== END SONG =====

        if (
            current_time > self.beatmap.duration
            and len(self.notes) == 0
        ):
            self.state = state.MENU

    # ================= INPUT =================

    def on_key_press(self, key, modifiers):

        # ===== MENU =====

        if self.state == state.MENU:

            if key == arcade.key.ENTER:
                self.state = state.SONG_SELECT

            return

        # ===== SONG SELECT =====

        if self.state == state.SONG_SELECT:

            if key == arcade.key.UP:

                self.selected_song_index -= 1

                self.selected_song_index %= len(self.songs)

            elif key == arcade.key.DOWN:

                self.selected_song_index += 1

                self.selected_song_index %= len(self.songs)

            elif key == arcade.key.ENTER:

                self.setup_game(
                    self.songs[self.selected_song_index]
                )

            return

        # ===== PLAYING =====

        key_map = {
            arcade.key.LEFT: "left",
            arcade.key.DOWN: "down",
            arcade.key.UP: "up",
            arcade.key.RIGHT: "right"
        }

        if key not in key_map:
            return

        target_note = None

        min_dist = 999

        for note in self.notes:

            if not note.hit:

                dist = abs(note.center_y - PERFECT_Y)

                if dist < min_dist:

                    min_dist = dist

                    target_note = note

        if not target_note:
            return

        # ===== WRONG KEY =====

        if target_note.key != key_map[key]:

            self.ui.combo = 0

            self.effects.append(
                HitEffect(
                    target_note.center_x,
                    PERFECT_Y,
                    "Miss"
                )
            )

            arcade.play_sound(
                self.hit_sounds["Miss"],
                volume=0.4
            )

            return

        dist = abs(target_note.center_y - PERFECT_Y)

        # ===== JUDGEMENT =====

        if dist < 10:

            score = 300
            result = "Perfect"

        elif dist < 30:

            score = 200
            result = "Great"

        elif dist < 60:

            score = 100
            result = "Good"

        else:

            self.ui.combo = 0

            self.effects.append(
                HitEffect(
                    target_note.center_x,
                    PERFECT_Y,
                    "Miss"
                )
            )

            arcade.play_sound(
                self.hit_sounds["Miss"],
                volume=0.4
            )

            return

        target_note.hit = True

        target_note.remove_from_sprite_lists()

        self.ui.score += score

        self.ui.combo += 1

        self.effects.append(
            HitEffect(
                target_note.center_x,
                PERFECT_Y,
                result
            )
        )

        arcade.play_sound(
            self.hit_sounds[result],
            volume=volumes[result]
        )