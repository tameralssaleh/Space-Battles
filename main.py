import pygame
import sys
import os
import random
import json
import time
import shutil
from datetime import datetime
from player import Player
from enemy import Enemy, Boss
from gui import Button, LevelButton
from items import Heart, Crystal
from levels import levels


pygame.init()

SCREENSIZE: tuple[int] = (800, 600)
PLAYER_SPAWN: tuple[int] = ((SCREENSIZE[0] - 64) / 2, SCREENSIZE[1] - 64 * 2)

title_bg = pygame.image.load("backgrounds/bg1.png")
title_bg = pygame.transform.scale(title_bg, SCREENSIZE)

window = pygame.display.set_mode(SCREENSIZE)
pygame.display.set_caption("Space Battles")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

backgrounds = os.listdir("backgrounds")
random_bg = pygame.image.load(f"backgrounds/{random.choice(backgrounds)}")
background = pygame.transform.scale(random_bg, SCREENSIZE)

player_img = pygame.image.load("sprites/player.png")
player_img_icon = pygame.transform.scale(player_img, (32, 32))
enemy_img = pygame.transform.flip(player_img, flip_x=False, flip_y=True)
boss_img_src = pygame.image.load("sprites/boss.png")
boss_enemy_img = pygame.transform.flip(boss_img_src, flip_x=False, flip_y=True)

heart_img = pygame.image.load("sprites/health.png")
heart_img = pygame.transform.scale(heart_img, (32, 32))

crystal_img = pygame.image.load("sprites/crystal.png")
crystal_img = pygame.transform.scale(crystal_img, (32, 32)) 

clock = pygame.time.Clock()

large_font = pygame.font.Font(None, 48)
medium_font = pygame.font.Font(None, 36) 
small_font = pygame.font.Font(None, 24)

game_over_sound = pygame.mixer.Sound("sounds/gameover.wav")
win_sound = pygame.mixer.Sound("sounds/win.wav")
grab_sound = pygame.mixer.Sound("sounds/grab.wav")
heal_sound = pygame.mixer.Sound("sounds/heal.wav")

enemies = []

player = Player(PLAYER_SPAWN[0], PLAYER_SPAWN[1], 64, 64, 5, player_img, SCREENSIZE, enemies, 100)
enemy = Enemy(random.randint(64, SCREENSIZE[0] - 64), 64, 64, 64, random.randint(3,10), enemy_img, SCREENSIZE, 100)

heart_drop_attempt_cooldown = 1
heart_drop_attempt_time = time.time()
heart_drop_rate = [False] * 98 + [True] * 2 # 2% chance heart will spawn every second

crystal_drop_attempt_cooldown = 3
crystal_drop_attempt_time = time.time()
crystal_drop_rate = [False] * 9 + [True] # 10% chance crystal will spawn every 10 seconds

heart_drops = []  # List to manage multiple hearts
crystal_drops = [] # List to manage multiple crystals

def start_game(level):
    global game_over_flag, win_game_flag, enemies, player, heart
    # Reset player score and health
    player.score = 0
    player.health = 100

    enemies.clear() # Ensure enemies are cleared before creating new ones.
    level_str = str(level) # Ensure level is string
    level_int = int(level) # Level_int will be used to check which level the player is.

    enemy_count = levels.get(level_str, 1)  # Resets to 1 enemy if player level is passed max level (will add more levels soon)
    for _ in range(enemy_count):
        enemy = Enemy(random.randint(64, SCREENSIZE[0] - 64), 64, 64, 64, random.randint(3, 10), enemy_img, SCREENSIZE, 100)
        if 10 > level_int > 5:
            enemy.health = 120
        elif 20 > level_int > 10:
            enemy.health = 150
            player.fire_cool_down = 0.20 # Fire cool down is 0.25 second(s) before level 10.
        enemies.append(enemy)

    if level_int % 10 == 0:
        boss_enemy = Boss(random.randint(64, SCREENSIZE[0] - 64), 64, 128, 128, random.randint(3, 10), boss_enemy_img, SCREENSIZE, 500)
        enemies.append(boss_enemy)

    # Reset game flags
    game_over_flag = False
    win_game_flag = False

def game_over(surface, final_score, high_score):
    global game_over_flag, play_again_btn, quit_btn

    game_over_flag = True
    surface.fill((0, 0, 0))
    game_over_sound.play()

    enemies.clear()

    # Draw game over texts
    game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
    surface.blit(game_over_text, (SCREENSIZE[0] // 2 - 115, SCREENSIZE[1] // 2 - 50))

    high_text = medium_font.render(f"High Score: {high_score}", True, (255, 255, 255))
    surface.blit(high_text, (SCREENSIZE[0] // 2 - 100, SCREENSIZE[1] // 1.95))

    final_text = medium_font.render(f"Final Score: {final_score}", True, (255, 255, 255))
    surface.blit(final_text, (SCREENSIZE[0] // 2 - 100, SCREENSIZE[1] // 2.10))

    play_again_btn = Button(text="Play Again", x=SCREENSIZE[0] // 2 - 160, y=SCREENSIZE[1] // 1.70, width=150, height=50, font=pygame.font.Font(None, 36), color=(50, 168, 100), hover_color=(85, 201, 134))
    play_again_btn.draw(surface)
    quit_btn = Button(text="Quit Game", x=SCREENSIZE[0] // 2 + 5, y=SCREENSIZE[1] // 1.70, width=150, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))
    quit_btn.draw(surface)

def win_screen(surface, final_score, high_score):
    global win_game_flag, enemies, player, next_level_btn, play_again_btn, quit_btn, selected_level

    with open("text/splashes.txt", "r") as f:
        random_text = random.choice(f.readlines())

    win_game_flag = True
    surface.fill((0, 0, 0))

    player.score = 0
    player.health = 100
    
    enemies.clear()

    win_text = large_font.render("Level Complete!", True, (0, 255, 0))
    surface.blit(win_text, (SCREENSIZE[0] // 2 - 130, SCREENSIZE[1] // 2 - 50))

    high_text = medium_font.render(f"High Score: {high_score}", True, (255, 255, 255))
    surface.blit(high_text, (SCREENSIZE[0] // 2 - 100, SCREENSIZE[1] // 1.95))

    final_text = medium_font.render(f"Final Score: {final_score}", True, (255, 255, 255))
    surface.blit(final_text, (SCREENSIZE[0] // 2 - 100, SCREENSIZE[1] // 2.10))

    play_again_btn = Button(text="Play Again", x=SCREENSIZE[0] // 2 - 250, y=SCREENSIZE[1] // 1.70, width=150, height=50, font=pygame.font.Font(None, 36), color=(50, 168, 100), hover_color=(85, 201, 134))
    play_again_btn.draw(surface)
    next_level_btn = Button(text="Next level", x=SCREENSIZE[0] // 2 - 75, y=SCREENSIZE[1] // 1.70, width=150, height=50, font=pygame.font.Font(None, 36), color=(50, 168, 100), hover_color=(85, 201, 134))
    next_level_btn.draw(surface)
    quit_btn = Button(text="Quit Game", x=SCREENSIZE[0] // 2 + 100, y=SCREENSIZE[1] // 1.70, width=150, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))
    quit_btn.draw(surface)

    tip_text = small_font.render(random_text, True, (255, 255, 255))
    surface.blit(tip_text, tip_text.get_rect(center=(SCREENSIZE[0] // 2, SCREENSIZE[1] // 1.20)))    

def select_level():
    time.sleep(0.1) # Prevents more than one click to be registered
    with open("save/data.json", "r") as f:
        data = json.load(f)
        
    select_lvl_font = pygame.font.Font(None, 64)
    select_lvl_title = select_lvl_font.render("Select Level", True, (255, 255, 255))
    back_btn = Button(text="Back", x=SCREENSIZE[0] // 2 - 350, y=525, width=150, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))

    level_buttons = []
    button_size = 50
    padding = 20
    levels_per_row = 10
    level_count = len(levels)

    for i in range(level_count):
        row = i // levels_per_row
        col = i % levels_per_row
        x = SCREENSIZE[0] // 2 - ((levels_per_row * (button_size + padding)) // 2) + col * (button_size + padding)
        y = SCREENSIZE[1] // 2 - 100 + row * (button_size + padding)
        level_button = LevelButton(id=i + 1, x=x, y=y, width=button_size, height=button_size, font=pygame.font.Font(None, 24), color=(50, 168, 100), hover_color=(85, 201, 134))

        # Color each boss level button a gold color.
        if level_button.id % 10 == 0:
            level_button.color = (171, 125, 0)
            level_button.hover_color = (212, 156, 6)
        # Disable button if the player hasn't reached that level yet
        if level_button.id > data["Unlocked Levels"]:
            level_button.color = (99, 99, 99)
            level_button.hover_color = (99, 99, 99)
            level_button.enabled = False
        
        level_buttons.append(level_button)

    while True:
        window.blit(title_bg, (0, 0))
        window.blit(select_lvl_title, (SCREENSIZE[0] // 2 - select_lvl_title.get_width() // 2, SCREENSIZE[1] // 4 - 100))
        back_btn.draw(window)

        for level_button in level_buttons:
            level_button.draw(window)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pressed[0]:
            if back_btn.is_clicked(mouse_x, mouse_y):
                title_screen()  # End loop & return to title screen.
                break

            for level_button in level_buttons:
                if level_button.enabled:
                    if level_button.is_clicked(mouse_x, mouse_y):
                        selected_level = level_button.id
                        time.sleep(0.1)
                        start_game(str(selected_level))
                        player.level = selected_level
                        data["Level"] = player.level
                        with open("save/data.json", "w") as f:
                            json.dump(data, f, indent=4)
                        f.close()
                        return
                else:
                    pass
    f.close()

def options_screen():
    options_font = pygame.font.Font(None, 64)
    options_title = options_font.render("Options", True, (255, 255, 255))
    back_btn = Button(text="Back", x=SCREENSIZE[0] // 2 - 350, y=525, width=150, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))
    while True:
        clear_crash_btn = Button(text=f"Clear Crash Data ({len(os.listdir('crashdata')) if os.path.exists('crashdata') else 0})", x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 - 150, width=300, height=50, font=pygame.font.Font(None, 36), color=(99, 99, 99), hover_color=(145, 145, 145))
        window.blit(title_bg, (0, 0))
        window.blit(options_title, (SCREENSIZE[0] // 2 - options_title.get_width() // 2, SCREENSIZE[1] // 4 - 100))
        back_btn.draw(window)
        clear_crash_btn.draw(window)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pressed[0]:
            if back_btn.is_clicked(mouse_x, mouse_y):
                title_screen()  # End loop & return to title screen.
                break
            if clear_crash_btn.is_clicked(mouse_x, mouse_y):
                if os.path.exists("crashdata"):
                    shutil.rmtree("crashdata")
                    clear_crash_btn.text = "Crash Data Cleared"

def show_stats():
    with open("save/data.json", "r") as f:
        data = json.load(f)

    stats_font = pygame.font.Font(None, 64)
    stats_title_text = stats_font.render("My Statistics", True, (255, 255, 255))
    back_btn = Button(text="Back", x=SCREENSIZE[0] // 2 - 350, y=525, width=150, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))

    total_score_text = medium_font.render(f"Total Score:    {data['Total Score']}", True, (255, 255, 255))
    high_score_text = medium_font.render(f"High Score:     {data['High Score']}", True, (255, 255, 255))
    kills_text = medium_font.render(f"Total Kills:      {data['Kills']}", True, (255, 255, 255))
    hits_text = medium_font.render(f"Total Hits:       {data['Hits']}", True, (255, 255, 255))
    deaths_text = medium_font.render(f"Total Deaths:   {data['Deaths']}", True, (255, 255, 255))
    crystals_text = medium_font.render(f"Crystals:          {data['Crystals']}", True, (255, 255, 255))

    while True:
        window.blit(title_bg, (0, 0))
        window.blit(stats_title_text, (SCREENSIZE[0] // 2 - stats_title_text.get_width() // 2, SCREENSIZE[1] // 4 - 100))
        
        window.blit(total_score_text, (SCREENSIZE[0] // 2 - 112, SCREENSIZE[1] // 4))
        window.blit(high_score_text, (SCREENSIZE[0] // 2 - 112, SCREENSIZE[1] // 4 + 50))
        window.blit(kills_text, (SCREENSIZE[0] // 2 - 112, SCREENSIZE[1] // 4 + 100))
        window.blit(hits_text, (SCREENSIZE[0] // 2 - 112, SCREENSIZE[1] // 4 + 150))
        window.blit(deaths_text, (SCREENSIZE[0] // 2 - 112 , SCREENSIZE[1] // 4 + 200))
        window.blit(crystals_text, (SCREENSIZE[0] // 2 - 112 , SCREENSIZE[1] // 4 + 250))
        back_btn.draw(window)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            if back_btn.is_clicked(mouse_x, mouse_y):
                title_screen() # End loop & return to title screen.
                break

    f.close()

def title_screen():
    global selected_level
    with open("save/data.json", "r") as f:
        data = json.load(f)

    title_font = pygame.font.Font(None, 64)
    screen_title = title_font.render("Space Battles", True, (255, 255, 255))

    play_btn = Button(text="Play", x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 - 100, width=300, height=50, font=pygame.font.Font(None, 36), color=(50, 168, 100), hover_color=(85, 201, 134))
    if data["Level"] > 1:
        play_btn.text = f"Continue: Level {data['Level']}"
    select_lvl_btn = Button(text="Select Level",  x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 - 30, width=300, height=50, font=pygame.font.Font(None, 36), color=(50, 168, 100), hover_color=(85, 201, 134))
    options_btn = Button(text="Options", x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 + 40, width=300, height=50, font=pygame.font.Font(None, 36), color=(99, 99, 99), hover_color=(145, 145, 145))
    stats_btn = Button(text="My Stats", x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 + 110, width=300, height=50, font=pygame.font.Font(None, 36), color=(99, 99, 99), hover_color=(145, 145, 145))
    quit_btn = Button(text="Quit", x=SCREENSIZE[0] // 2 - 150, y=SCREENSIZE[1] // 2 + 180, width=300, height=50, font=pygame.font.Font(None, 36), color=(156, 30, 42), hover_color=(184, 55, 67))
    
    while True:
        window.blit(title_bg, (0, 0))
        window.blit(screen_title, (SCREENSIZE[0] // 2 - screen_title.get_width() // 2, SCREENSIZE[1] // 4 - 100))

        play_btn.draw(window)
        select_lvl_btn.draw(window)
        options_btn.draw(window)
        stats_btn.draw(window)
        quit_btn.draw(window)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            if play_btn.is_clicked(mouse_x, mouse_y):
                player = Player(PLAYER_SPAWN[0], PLAYER_SPAWN[1], 64, 64, 5, player_img, SCREENSIZE, enemies, 100)
                selected_level = data["Level"]
                start_game(str(player.level))
                return  # Exit the title screen and start the game
            elif select_lvl_btn.is_clicked(mouse_x, mouse_y):
                select_level()
                break
            elif options_btn.is_clicked(mouse_x, mouse_y):
                options_screen()
                break
            elif stats_btn.is_clicked(mouse_x, mouse_y):
                show_stats()
                break
            elif quit_btn.is_clicked(mouse_x, mouse_y):
                pygame.quit()
                sys.exit()
    f.close()

game_text_color = (255, 255, 255)

# Main game loop
running = True

title_screen()  # Display the title screen

while running:
    try:      
        with open("save/data.json", "r") as f:
            data = json.load(f)

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            title_screen() # Pause game & return to title screen

        if not game_over_flag and not win_game_flag:
            window.blit(background, (0, 0))

            if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
                player.fire_projectile(keys)

            player.movement(keys)
            player.check_collision()
            player.draw(window)

            for enemy in enemies:
                enemy.draw(window)
                enemy.movement()
                enemy.fire_projectile()
                enemy.check_collision(player)

                if enemy.kills_player:
                    player.projectiles.clear()
                    game_over(window, player.score, player.high_score)
                    game_over_flag = True
                    break  # Exit the for loop if the game is over

            if not game_over_flag and len(enemies) == 0:
                player.projectiles.clear()
                for heart in heart_drops[:]:
                    if heart.active:
                        heart.active = False
                for crystal in crystal_drops[:]:
                    if crystal.active:
                        crystal.active = False
                win_screen(window, player.score, player.high_score)
                f.close()
                win_game_flag = True

            if player.level > 5:
                if time.time() - heart_drop_attempt_time >= heart_drop_attempt_cooldown:
                    heart_drop_attempt_time = time.time()  # Reset the attempt time
                    spawn_heart_chance = random.choice(heart_drop_rate)

                    if spawn_heart_chance:
                        # Create a new heart and add it to the list
                        heart = Heart(random.randint(64, SCREENSIZE[0] - 64), 32, heart_img, SCREENSIZE) 
                        heart_drops.append(heart)

            # Update and draw hearts
            for heart in heart_drops[:]:
                if heart.active:
                    heart.draw(window)
                    heart.update()

                    if heart.hitbox.colliderect(player.hitbox):
                        heal_sound.play()
                        player.health = 100
                        heart.active = False
                        heart_drops.remove(heart)

                # Remove heart if it goes off-screen
                if heart.y > SCREENSIZE[1]:
                    heart_drops.remove(heart)

            if time.time() - crystal_drop_attempt_time >= crystal_drop_attempt_cooldown:
                crystal_drop_attempt_time = time.time()  # Reset the attempt time
                spawn_crystal_chance = random.choice(crystal_drop_rate)

                if spawn_crystal_chance:
                    # Create a new crystal and add it to the list
                    crystal = Crystal(random.randint(64, SCREENSIZE[0] - 64), 32, crystal_img, SCREENSIZE) 
                    crystal_drops.append(crystal)

            # Update and draw crystals
            for crystal in crystal_drops[:]:
                if crystal.active:
                    crystal.draw(window)
                    crystal.update()
                    if crystal.hitbox.colliderect(player.hitbox):
                        grab_sound.set_volume(1)
                        grab_sound.play()
                        player.score += 300
                        player.crystals += 1
                        crystal.active = False
                        crystal_drops.remove(crystal)

                # Remove crystal if it goes off-screen
                if crystal.y > SCREENSIZE[1]:
                    crystal_drops.remove(crystal)  

            # Text for score, level, enemy count, and health

            if not game_over_flag and not win_game_flag: # Display text and icons until level is beaten or lost.

                score_text = medium_font.render(f"Score: {player.score}", True, game_text_color)
                window.blit(score_text, (10, SCREENSIZE[1] - 40))

                level_text = medium_font.render(f"Level: {data['Level']}", True, game_text_color)
                window.blit(level_text, (200, SCREENSIZE[1] - 40))

                window.blit(player_img_icon, (450, SCREENSIZE[1] - 45))

                enemies_text = medium_font.render(str(len(enemies)), True, game_text_color)
                window.blit(enemies_text, (485, SCREENSIZE[1] - 40))

                window.blit(heart_img, (690, SCREENSIZE[1] - 45))

                health_text = medium_font.render(str(player.health), True, game_text_color)
                window.blit(health_text, (725, SCREENSIZE[1] - 40))
            
            pygame.display.flip()

        if game_over_flag:
            play_again_btn.draw(window)
            quit_btn.draw(window)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:
                with open("save/data.json", "r") as f:
                    data = json.load(f)
                if play_again_btn.is_clicked(mouse_x, mouse_y):
                    start_game(str(data["Level"]))
                    continue
                elif quit_btn.is_clicked(mouse_x, mouse_y):
                    with open("save/data.json", "r+") as f: # Open file in read and write mode before quitting game
                        data["Level"] = player.level
                        data["Crystals"] = player.crystals
                        json.dump(data, f, indent=4)
                    f.close()
                    pygame.quit()
                    sys.exit()

        if win_game_flag:
            play_again_btn.draw(window)
            quit_btn.draw(window)
            next_level_btn.draw(window)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:
                with open("save/data.json", "r") as f:
                    data = json.load(f)
                if play_again_btn.is_clicked(mouse_x, mouse_y):
                    start_game(str(data["Level"]))
                    continue
                elif next_level_btn.is_clicked(mouse_x, mouse_y):
                    if player.level == player.unlocked_levels:
                        if player.unlocked_levels == len(levels):
                            pass
                        player.unlocked_levels += 1
                        data["Unlocked Levels"] = player.unlocked_levels
                    player.level += 1
                    data["Level"] = player.level
                    with open("save/data.json", "w") as f:
                        json.dump(data, f, indent=4)
                    start_game(str(data["Level"]))
                    continue
                elif quit_btn.is_clicked(mouse_x, mouse_y):
                    with open("save/data.json", "r+") as f: # Open file in read and write mode before quitting game
                        data["Level"] = player.level
                        data["Crystals"] = player.crystals
                        json.dump(data, f, indent=4)
                    f.close()
                    pygame.quit()
                    sys.exit()
    except Exception as error:
        directory = "crashdata"
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = f"{directory}/{timestamp}.txt"

        with open(file_path, "w+") as f:
            f.write(f"Error - Fatal - {datetime.now().strftime('%B %d, %Y, %H:%M:%S')}\n")
            f.write(f"Error has occurred in the main game loop: {error}\n")
pygame.quit()
sys.exit()
