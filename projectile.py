import pygame

# Class for Projectile object

class Projectile(object):
    def __init__(self, x, y, width, height, velocity, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.image = pygame.transform.scale(image, (width, height))
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, surface):
        surface.blit(self.image, (self.x - 4, self.y))

    def move(self, downward=False):
        if downward:
            self.y += self.velocity
        else:
            self.y -= self.velocity
        self.hitbox.y = self.y
