import random

class Beatmap:
    def __init__(self, bpm=120, duration=20):
        self.bpm = bpm
        self.beat_time = 60 / bpm
        self.duration = duration

    def get_notes(self):
        notes = []
        t = 1.0

        keys = ["left", "down", "up", "right"]

        while t < self.duration:
            notes.append({
                "time": t,
                "key": random.choice(keys)
            })
            t += self.beat_time

        return notes