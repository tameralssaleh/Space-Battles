import pygame
import random
import time
import json
from projectile import Projectile

class Enemy(object):
    def __init__(self, x, y, width, height, velocity, image, screen_size, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.image = pygame.transform.scale(image, (64, 64))
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.screen_size = screen_size
        self.health = health
        self.damage_image = pygame.image.load("sprites/damage.png")
        self.damage_image = pygame.transform.scale(self.damage_image, (64, 64))
        self.damage_image = pygame.transform.flip(self.damage_image, flip_x=False, flip_y=True)
        self.original_image = self.image
        self.last_direction_change_time = time.time()
        self.direction = random.choice([-1, 0, 1])  # Initial direction (-1: left, 0: no movement, 1: right)
        self.hit_time = 1
        self.projectiles = []
        self.projectile_image = pygame.image.load("sprites/projectile.png")
        self.projectile_image = pygame.transform.scale(self.projectile_image, (16, 16))
        self.projectile_image = pygame.transform.flip(self.projectile_image, flip_x=False, flip_y=True)
        self.projectile_sound = pygame.mixer.Sound("sounds/projectile.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.death_sound = pygame.mixer.Sound("sounds/death.wav")
        self.projectile_velocity = 5  # Speed of the enemy's projectile
        self.fire_cooldown = random.uniform(1.0, 3.0)  # Random cooldown between shots
        self.last_fire_time = time.time()
        self.kills_player = False

        with open("save/data.json", "r") as f:
            self.data = json.load(f)

    def hit(self):
        self.image = self.damage_image
        self.hit_time = time.time()

    def fire_projectile(self):
        current_time = time.time()
        if current_time - self.last_fire_time >= self.fire_cooldown:
            # Fire a projectile
            projectile = Projectile(self.x + self.width // 2 - 4, self.y + self.height, 16, 16, self.projectile_velocity, self.projectile_image)
            self.projectiles.append(projectile)
            self.last_fire_time = current_time
            self.projectile_sound.play()

    def check_collision(self, player):
        for projectile in self.projectiles:
            projectile.move(downward=True)
            if projectile.hitbox.colliderect(player.hitbox):
                player.hit()
                self.hit_sound.play()
                player.health -= 10
                self.projectiles.remove(projectile)
                if player.health <= 0:
                    self.death_sound.play()
                    self.kills_player = True

                    with open("save/data.json", "w") as f:
                        self.data["Deaths"] += 1
                        json.dump(self.data, f, indent=4)

            # Remove projectile if it goes off-screen
            if projectile.y > self.screen_size[1]:
                self.projectiles.remove(projectile)

    def draw(self, surface):
        # Revert to the original image after 1/4 second
        if self.hit_time and time.time() - self.hit_time > 0.25:
            self.image = self.original_image
            self.hit_time = 0

        surface.blit(self.image, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(surface)

    def movement(self):
        current_time = time.time()
        if current_time - self.last_direction_change_time >= random.uniform(0.0, 1.5): # Randomly change direction
            self.direction = random.choice([-1, 0, 1])
            self.last_direction_change_time = current_time

        self.x += self.velocity * self.direction

        # Keep the enemy within screen bounds
        if self.x < 0:
            self.x = 0
            self.direction = 1
        elif self.x > self.screen_size[0] - self.width:
            self.x = self.screen_size[0] - self.width
            self.direction = -1

        self.hitbox.x = self.x

class Boss(object):
    def __init__(self, x, y, width, height, velocity, image, screen_size, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.image = pygame.transform.scale(image, (128, 128))
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.screen_size = screen_size
        self.health = health
        self.damage_image = pygame.image.load("sprites/damage.png")
        self.damage_image = pygame.transform.scale(self.damage_image, (128, 128))
        self.damage_image = pygame.transform.flip(self.damage_image, flip_x=False, flip_y=True)
        self.original_image = self.image
        self.last_direction_change_time = time.time()
        self.direction = random.choice([-1, 0, 1])  # Initial direction (-1: left, 0: no movement, 1: right)
        self.hit_time = 1
        self.projectiles = []
        self.projectile_image = pygame.image.load("sprites/projectile.png")
        self.projectile_image = pygame.transform.scale(self.projectile_image, (32, 32))
        self.projectile_image = pygame.transform.flip(self.projectile_image, flip_x=False, flip_y=True)
        self.projectile_sound = pygame.mixer.Sound("sounds/projectile.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.death_sound = pygame.mixer.Sound("sounds/death.wav")
        self.projectile_velocity = 5  # Speed of the enemy's projectile
        self.fire_cooldown = random.uniform(1.0, 3.0)  # Random cooldown between shots
        self.last_fire_time = time.time()
        self.kills_player = False

        with open("save/data.json", "r") as f:
            self.data = json.load(f)

    def hit(self):
        self.image = self.damage_image
        self.hit_time = time.time()

    def fire_projectile(self):
        current_time = time.time()
        if current_time - self.last_fire_time >= self.fire_cooldown:
            # Fire a projectile
            projectile = Projectile(self.x + self.width // 2 - 4, self.y + self.height, 32, 32, self.projectile_velocity, self.projectile_image)
            self.projectiles.append(projectile)
            self.last_fire_time = current_time
            self.projectile_sound.play()

    def check_collision(self, player):
        for projectile in self.projectiles:
            projectile.move(downward=True)
            if projectile.hitbox.colliderect(player.hitbox):
                player.hit()
                self.hit_sound.play()
                player.health -= 50
                self.projectiles.remove(projectile)
                if player.health <= 0:
                    self.death_sound.play()
                    self.kills_player = True

                    with open("save/data.json", "w") as f:
                        self.data["Deaths"] += 1
                        json.dump(self.data, f, indent=4)

            # Remove projectile if it goes off-screen
            if projectile.y > self.screen_size[1]:
                self.projectiles.remove(projectile)

    def draw(self, surface):
        # Revert to the original image after 1/4 second
        if self.hit_time and time.time() - self.hit_time > 0.25:
            self.image = self.original_image
            self.hit_time = 0

        surface.blit(self.image, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(surface)

    def movement(self):
        current_time = time.time()
        if current_time - self.last_direction_change_time >= random.uniform(0.0, 1.5): # Randomly change direction
            self.direction = random.choice([-1, 0, 1])
            self.last_direction_change_time = current_time

        self.x += self.velocity * self.direction

        # Keep the enemy within screen bounds
        if self.x < 0:
            self.x = 0
            self.direction = 1
        elif self.x > self.screen_size[0] - self.width:
            self.x = self.screen_size[0] - self.width
            self.direction = -1

        self.hitbox.x = self.x