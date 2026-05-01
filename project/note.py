import arcade

TEXTURES = {
    "up": arcade.load_texture("assets/images/up.png"),
    "down": arcade.load_texture("assets/images/down.png"),
    "left": arcade.load_texture("assets/images/left.png"),
    "right": arcade.load_texture("assets/images/right.png"),
}

class Note(arcade.Sprite):
    def __init__(self, key, time, x, y):
        super().__init__(scale=0.3)

        self.key = key
        self.time = time
        self.center_x = x
        self.center_y = y
        self.hit = False

        self.texture = TEXTURES[key]

    def update(self, delta_time):
        self.center_y -= 250 * delta_time