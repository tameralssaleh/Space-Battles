import pygame
from projectile import Projectile
import time
import json

class Player(object):
    def __init__(self, x: int, y: int, width: int, height: int, velocity: int, image, screen_size: tuple[int], enemies: list[object], health: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.image = pygame.transform.scale(image, (64, 64))
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.screen_size = screen_size
        self.projectiles = [] # List of all projectile objects currently on screen
        self.projectile_image_src = pygame.image.load("sprites/projectile.png")
        self.projectile_image = pygame.transform.scale(self.projectile_image_src, (16, 16))
        self.projectile_velocity = 10 # Velocity of the projectile
        self.fire_cool_down = 0.25  # Cooldown period in seconds
        self.last_fire_time = 0  # Track the last time a projectile was fired
        self.enemies = enemies
        self.projectile_sound = pygame.mixer.Sound("sounds/projectile.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.death_sound = pygame.mixer.Sound("sounds/death.wav")
        self.score = 0
        self.health = health
        self.damage_image = pygame.image.load("sprites/damage.png")
        self.damage_image = pygame.transform.scale(self.damage_image, (64, 64))
        self.original_image = self.image
        self.last_direction_change_time = time.time()
        self.hit_time = 1
        
        with open("save/data.json", "r") as f:
            self.data = json.load(f)

        self.high_score = self.data["High Score"]
        self.level = self.data["Level"]
        self.unlocked_levels = self.data["Unlocked Levels"]
        self.crystals = self.data["Crystals"]
        
    def draw(self, surface):
        # Revert to the original image after 1/4 second
        if self.hit_time and time.time() - self.hit_time > 0.25:
            self.image = self.original_image
            self.hit_time = 0

        surface.blit(self.image, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(surface)

    def movement(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.velocity
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.velocity

        if self.x < self.width:
            self.x = self.width
        elif self.x > self.screen_size[0] - self.width * 2:
            self.x = self.screen_size[0] - self.width * 2
        
        self.hitbox.x = self.x

    def hit(self):
        self.image = self.damage_image
        self.hit_time = time.time()

    def fire_projectile(self, keys):
        cur_time = time.time()
        if cur_time - self.last_fire_time >= self.fire_cool_down:
            if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
                projectile = Projectile(self.x + self.width // 2 - 4, self.y, 16, 16, self.projectile_velocity, self.projectile_image)
                self.projectiles.append(projectile)
                self.last_fire_time = cur_time  # Update the last fire time
                self.projectile_sound.set_volume(0.5)
                self.projectile_sound.play()

    def check_collision(self):
        for projectile in self.projectiles:
            projectile.move()
            # Check for collision with any enemy
            for enemy in self.enemies:
                if projectile.hitbox.colliderect(enemy.hitbox):
                    enemy.health -= 10
                    self.hit_sound.set_volume(1)
                    self.hit_sound.play()
                    self.projectiles.remove(projectile)
                    enemy.hit()
                    self.score += 10 # Add 10 score for hit
                    self.data["Total Score"] += 10
                    self.data["Hits"] += 1
                    # Ensures level is updated even after collision is detected
                    # This next line prevents that.
                    self.data["Level"] = self.level
                    self.data["Crystals"] = self.crystals 
                    self.data["Unlocked Levels"] = self.unlocked_levels 
                    if self.data["High Score"] < self.score:
                        self.data["High Score"] += 10
                    
                    with open("save/data.json", "w") as f:
                        json.dump(self.data, f, indent=4)
                    if enemy.health <= 0: 
                        self.enemies.remove(enemy)
                        self.death_sound.play()
                        self.score += 100 # Add 100 score for death of enemy
                        with open("save/data.json", "w") as f:
                            self.data["Total Score"] += 100
                            self.data["Kills"] += 1
                            if self.data["High Score"] < self.score:
                                self.data["High Score"] += 100

                            json.dump(self.data, f, indent=4)
                    break

            # Remove projectile if it goes off-screen
            if projectile.y < 0:
                self.projectiles.remove(projectile)


        
