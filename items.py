
# Items that the player can obtain to help them in levels.

class Heart:
    def __init__(self, x, y, image, screen_size):
        self.x = x
        self.y = y
        self.image = image
        self.hitbox = self.image.get_rect(topleft=(x, y))
        self.screen_size = screen_size
        self.active = True

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, (self.x, self.y))

    def update(self):
        self.y += 2  # Move the heart downwards
        self.hitbox.y = self.y
        if self.y > self.screen_size[1]:
            self.active = False  # Deactivate if it goes off-screen

class Crystal:
    def __init__(self, x, y, image, screen_size):
        self.x = x
        self.y = y
        self.image = image
        self.hitbox = self.image.get_rect(topleft=(x, y))
        self.screen_size = screen_size
        self.active = True

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, (self.x, self.y))

    def update(self):
        self.y += 2  # Move the heart downwards
        self.hitbox.y = self.y
        if self.y > self.screen_size[1]:
            self.active = False  # Deactivate if it goes off-screen