import pygame
import sys
import random
import math
import os
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

# Initialize the joystick
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Helper function to find resource paths for Pyninstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def play_music(song):
    global music_Current
    if song == music_Current:
        pass
    else:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path(song))
        pygame.mixer.music.play(loops=-1)
        music_Current = song

def play_sfx(sound):
    pygame.mixer.Sound.play(pygame.mixer.Sound(resource_path(sound)))

font_path = resource_path("GresickMetal-51LXV.otf")

font = pygame.font.Font(font_path, 32)

def draw_text(surface, text, color, font_size, x, y):
    if text.isdigit():
        default_font = pygame.font.Font(None, font_size)
        text_surface = default_font.render(text, True, color)
    else:
        text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

def save_score(player_name, score):
    if score > 9:
        with open("scores.txt", "a") as file:
            file.write(f"{player_name}: {score}\n")

def load_scores():
    scores = {}
    if os.path.exists("scores.txt"):
        with open("scores.txt", "r") as file:
            for line in file:
                parts = line.split(":")
                name = parts[0].strip()
                score = int(parts[1])
                scores[name] = score
    return scores

def get_input():
    keys_layout = [
        "1 2 3 4 5 6 7 8 9 0",
        "Q W E R T Y U I O P",
        "A S D F G H J K L",
        "Z X C V B N M",
        "BACK SPACE ENTER"
    ]
    text = ""
    row, col = 0, 0
    key_width, key_height = 60, 60
    spacing = 10
    cursor_blink = True
    cursor_timer = 0

    while True:
        win.fill((200, 200, 200))
        draw_text(win, "Enter your name:", (30, 30, 30), 32, width // 2, height // 6)
        draw_text(win, text, (30, 30, 30), 32, width // 2, height // 3)

        cursor_timer += 1
        if cursor_timer % 30 == 0:
            cursor_blink = not cursor_blink

        if cursor_blink and len(text) < 10:
            draw_text(win, text + "|", (30, 30, 30), 32, width // 2, height // 3)
        else:
            draw_text(win, text, (30, 30, 30), 32, width // 2, height // 3)

        if joystick and pygame.joystick.get_count() > 0:
            for r, row_keys in enumerate(keys_layout):
                row_keys_split = row_keys.split()
                for c, key in enumerate(row_keys_split):
                    key_x = (width // 2 - (len(row_keys_split) * (key_width + spacing)) // 2) + c * (key_width + spacing)
                    key_y = (height // 2 + r * (key_height + spacing))
                    key_rect = pygame.Rect(key_x, key_y, key_width, key_height)
                    pygame.draw.rect(win, (0, 0, 0) if (r, c) == (row, col) else (255, 255, 255), key_rect)
                    draw_text(win, key, (0, 0, 0), 32, key_x + key_width // 2, key_y + 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    text = text[:-1]
                elif event.key == K_RETURN:
                    return text
                else:
                    text += event.unicode
            elif joystick and pygame.joystick.get_count() > 0:
                if event.type == pygame.JOYHATMOTION:
                    hat = joystick.get_hat(0)
                    row_keys_split = keys_layout[row].split()
                    if hat[0] == 1:
                        col = min(col + 1, len(row_keys_split) - 1)
                    elif hat[0] == -1:
                        col = max(col - 1, 0)
                    if hat[1] == 1:
                        row = max(row - 1, 0)
                        col = min(col, len(keys_layout[row].split()) - 1)
                    elif hat[1] == -1:
                        row = min(row + 1, len(keys_layout) - 1)
                        col = min(col, len(keys_layout[row].split()) - 1)
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        if event.value < -0.5:
                            col = max(col - 1, 0)
                        elif event.value > 0.5:
                            col = min(col + 1, len(keys_layout[row].split()) - 1)
                    elif event.axis == 1:
                        if event.value < -0.5:
                            row = max(row - 1, 0)
                            col = min(col, len(keys_layout[row].split()) - 1)
                        elif event.value > 0.5:
                            row = min(row + 1, len(keys_layout) - 1)
                            col = min(col, len(keys_layout[row].split()) - 1)
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A button
                        key = keys_layout[row].split()[col]
                        if key == "BACK":
                            text = text[:-1]
                        elif key == "SPACE":
                            text += " "
                        elif key == "ENTER":
                            return text
                        else:
                            text += key
                    elif event.button == 1:  # B button
                        return text
                    elif event.button == 2:  
                        text = text[:-1]

def reset_game():
    global player, rectangles, player_score, game_over, score_saved, last_rect_creation_time, rect_creation_interval, ramp_up, car_counter
    player = Player(width // 2, height // 2, 20, (200, 200, 200))
    rectangles = []
    player_score = 0
    game_over = False
    score_saved = False
    last_rect_creation_time = pygame.time.get_ticks()
    rect_creation_interval = random.randint(2000, 3000)
    ramp_up = 1
    car_counter = 0
    title_screen_display()
    get_input()
    play_music(music_Game)

def pause_menu_display():
    global is_paused
    options = ["Resume", "Quit"]
    selected_option = 0
    while is_paused:
        win.fill((50, 50, 50))
        draw_text(win, "Paused", (200, 200, 200), 72, width // 2, height // 4)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, 36, width // 2, height // 2 + i * 50)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        is_paused = False
                    elif selected_option == 1:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
            elif event.type == pygame.JOYBUTTONDOWN:
                if joystick:
                    if event.button == 0:  # A button
                        if selected_option == 0:
                            is_paused = False
                        elif selected_option == 1:
                            pygame.quit()
                            sys.exit()
            elif event.type == pygame.JOYAXISMOTION:
                if joystick:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(200)  # Add delay to prevent rapid scrolling
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(200)  # Add delay to prevent rapid scrolling
            elif event.type == pygame.JOYHATMOTION:
                if joystick:
                    hat = joystick.get_hat(0)
                    if hat[1] == 1:
                        selected_option = (selected_option - 1) % len(options)
                    elif hat[1] == -1:
                        selected_option = (selected_option + 1) % len(options)

def title_screen_display():
    global running, cars_per_spawn, difficulty 
    play_music(music_MainMenu)
    selected_option = 0
    options = ["Easy", "Medium", "Rush Hour", "" ] #<<feature not bug
    
    while True:
        win.fill((100, 100, 100))
        draw_text(win, "Child in Traffic (True Story)", (200, 200, 200), 72, width // 2, height // 6)
        draw_text(win, "Select Difficulty:", (200, 200, 200), 48, width // 2, height // 3)

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, 36, width // 2, height // 2 + i * 40)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        difficulty = 0
                    elif selected_option == 1:
                        difficulty = 1
                    elif selected_option == 2:
                        difficulty = 2
                    elif selected_option == 3:
                        difficulty = 3
                    return
            elif event.type == pygame.JOYAXISMOTION:
                if joystick:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(50)  
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(50)  
            elif event.type == pygame.JOYHATMOTION:
                if joystick:
                    hat = joystick.get_hat(0)
                    if hat[1] == 1:
                        selected_option = (selected_option - 1) % len(options)
                    elif hat[1] == -1:
                        selected_option = (selected_option + 1) % len(options)
            elif event.type == pygame.JOYBUTTONDOWN:
                if selected_option == 0:
                    difficulty = 0
                elif selected_option == 1:
                    difficulty = 1
                elif selected_option == 2:
                    difficulty = 2
                elif selected_option == 3:
                    difficulty = 3
                return

# Set up the display
displayInfo = pygame.display.Info()
width, height = displayInfo.current_w, displayInfo.current_h
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Child In Traffic")

class Player:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = 5

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def collide_with(self, rect):
        closest_x = max(rect.x, min(self.x, rect.x + rect.width))
        closest_y = max(rect.y, min(self.y, rect.y + rect.height))
        dist_x = self.x - closest_x
        dist_y = self.y - closest_y
        distance = math.sqrt((dist_x * dist_x) + (dist_y * dist_y))
        return distance < self.radius

class Rectangle:
    def __init__(self, x, y, width, height, color, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y > height

backstories = [
    # Sensible Stories
    "Somewhere, the child heard the GigaChad song before he was cruched",
    "The child was chasing a runaway ball when a car suddenly appeared.",
    "The child was riding a bike and lost control, veering into the busy road.",
    "In a rush to get home for dinner, the child didn't notice the speeding car.",
    "The child was helping an elderly person cross the street when tragedy struck.",
    "Distracted by their phone, the child wandered into the traffic without realizing.",
    "Trying to catch the school bus, the child dashed across the street without looking.",
    "The child was playing a game with friends and didn't notice the traffic signal change.",
    "After a long day at school, the child was distracted and didn't see the oncoming traffic.",
    "Believing they were in a video game, the child attempted to 'respawn' by getting hit by a car.",
    "Dressed as a ninja, the child tried to perform an epic street-crossing stunt and failed miserably.",
    "Chasing after a runaway kite, the child didn't notice the massive eighteen-wheeler bearing down on them.",
    "In an attempt to impress their friends, the child tried to jump over a moving car and didn't quite make it.",
    "Trying to catch a falling star, the child ran into the street and met their end under the wheels of a truck.",
    "The child thought they saw a unicorn on the other side of the street and darted across without checking for cars.",
    "Lured by the sweet smell of ice cream from the truck, the child ran into the road, only to be flattened by a car.",
    "The child, convinced they had super speed, dashed across the road to prove it, only to be painfully proven wrong.", 
    "During an intense game of tag, the child zigged when they should have zagged, right into the path of a speeding car.",
    "A child was crossing the highway, when a HUGE caravan of trucks came zooming at him. The child was never seen again.",
    "The child, pretending to be a superhero, decided to stop traffic with their 'super strength' and got splatted instead.",
    "As the innocent little child crossed the street, the driver of the car was too busy watching anime to notice the child.",
    "The Child did not want to live anymore. After contemplating his life,\n he decided to end it in the best way possible, death by car.",
    # Quirky Stories
    "Well, he gone",
    "Thats what you get for not looking both ways before crossing the street.",
    "My brother was hit by a car once. He's fine now, but he's a little... flat-brained.",
    # Minor "Humor" Stories
    "L",
    "F",
    "Rest in Peperonis",
    "Uh oh!\n Stinky!",
    # COMPLETE BRAINROT REMOVE IF ADULTS PLAY PLEASE!!!!!
    "YA BOI WAS HIT BY A BIG ASS TRUCK.",
    "Oh, they're gonna have to glue you back together... IN HELL!",
    "BEEP BEEP MO- (The driver's lawyer advised him not to finish this sentence)",
    "Bro thought he was in GTAVI and tried to steal a car. He got hit by a car instead.",
    "The van with free candy didn't have free candy... nor black men... nor furries... nor drug addicts..."
    "The little shit got yeeted into the shadow realm by some\n booze-cranked driver in his skyscraper-like pimped-up diesel 48ft Uhaul.",
    "The child was wearing a fursuit. Someone apperently called the SWAT on them,\n and \"it\" got splattered in front of a cheering crowd. The end.",
    "YOU FAT BALD BASTARD YOU PIECE OF SUBHUMAN TRASH 2000 YEARS OF CONSTANT EVOLUTION TO CREATE\n A HAIRLESS FUCKING COCONUT MY GOD WHAT IS WRONG WITH YOU???",
    "Are ya listening? Okay. Grass grows, birds, fly, sun shines, and brudda?\n I HURT PEOPLE! Im a force of nature. If you were from, where I was from, you'd be from, where I was from. You'd be ded."
]

player = Player(width// 2, height // 2, 20, (200, 200, 200))
rectangles = []
gap_size = 100
ramp_up = 1
point_increase_timer = 0

sfx_Death = "audio/sfx_splat.mp3"
music_MainMenu = "audio/music_mariokartwii.mp3"
music_Game = "audio/music_metal-dark-matter-111451.mp3"
music_GameOver = "audio/music_lose.mp3"
music_Current = ""

last_rect_creation_time = pygame.time.get_ticks()
rect_creation_interval = random.randint(2000, 3000)  # 2-3 seconds in milliseconds
min_rect_creation_interval = 200  # Minimum creation interval

# Detects if x or y values have changed, and uses to set up normalised movement vectors
x_axis_changed = 0
y_axis_changed = 0

player_score = 0
difficulty = 0
is_paused = False
title_screen = True
running = True
game_over = False
score_saved = False

selected_backstory = ""

car_counter = 0
cars_per_spawn = 1

def main_game_loop():
    global running, game_over, is_paused, player_name, player_score, score_saved, selected_backstory, car_counter, ramp_up, rect_creation_interval, last_rect_creation_time, rectangles, point_increase_timer
    title_screen_display()
    player_name = get_input()
    play_music(music_Game)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_paused = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if joystick:
                    if event.button == 0:  # A button
                        if game_over:
                            running = False
                    elif event.button == 1:  # B button
                        game_over = True
            if not game_over and not is_paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        is_paused = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    if joystick and event.button in [2, 3]:
                        is_paused = True

        if game_over:
            play_music(music_GameOver)
            win.fill((100, 100, 100))
            draw_text(win, "Game Over", (200, 200, 200), 100, width // 2, height // 3)
            draw_text(win, "Press any key to play again", (200, 200, 200), 36, width // 2, height // 3 + 40)
            draw_text(win, "Press 'Esc' or 'B' button to quit", (200, 200, 200), 36, width // 2, height // 3 + 80)
            draw_text(win, f"Your Score: {player_score}", (200, 200, 200), 36, width // 2, height // 2)
            draw_text(win, "", (200, 200, 200), 15, width // 2, height * 2 // 3 - 40)

            if not score_saved:
                save_score(player_name, player_score)
                score_saved = True
                selected_backstory = random.choice(backstories)

            scores = load_scores()
            top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_scores:
                draw_text(win, "Top Scores:", (200, 200, 200), 36, width // 2, height // 2 + 100)
                y_offset = 0
                for i, (name, score) in enumerate(top_scores):
                    draw_text(win, f"{i+1}. {name}: {score}", (200, 200, 200), 24, width // 2, height // 2 + 150 + y_offset)
                    y_offset += 30

            backstory_lines = selected_backstory.split('\n')
            for i, line in enumerate(backstory_lines):
                draw_text(win, line, (200, 200, 200), 24, width // 2, height - 100 + i * 30)

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        reset_game()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1:  # B button
                        running = False
                    else:
                        reset_game()

        elif is_paused:
            pause_menu_display()
        else:
            keys = pygame.key.get_pressed()

            x_axis_changed, y_axis_changed = 0, 0
            if keys[pygame.K_DOWN] or keys[pygame.K_UP]:
                y_axis_changed = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                x_axis_changed = 1

            if keys[pygame.K_LEFT]:
                player.x -= player.speed / (1 + (.4 * y_axis_changed))
            elif keys[pygame.K_RIGHT]:
                player.x += player.speed / (1 + (.4 * y_axis_changed))
            if keys[pygame.K_UP]:
                player.y -= player.speed / (1 + (.4 * x_axis_changed))
            elif keys[pygame.K_DOWN]:
                player.y += player.speed / (1 + (.4 * x_axis_changed))

            if joystick:
                axis0 = joystick.get_axis(0)
                axis1 = joystick.get_axis(1)
                player.x += (axis0 * player.speed) / (1 + (.4 * abs(axis1)))
                player.y += (axis1 * player.speed) / (1 + (.4 * abs(axis0)))

            player.x = max(player.radius, min(player.x, width - player.radius))
            player.y = max(player.radius, min(player.y, height - player.radius))

            for rect in rectangles:
                rect.update()
            rectangles = [rect for rect in rectangles if not rect.is_off_screen()]

            for rect in rectangles:
                if player.collide_with(rect):
                    play_sfx(sfx_Death)
                    game_over = True
                    break

            if difficulty == 0:
                cars_per_spawn = 1
            elif difficulty == 1:
                cars_per_spawn = 2
            elif difficulty == 2:
                cars_per_spawn = 3
            elif difficulty == 3 and player_score < 11:
                cars_per_spawn = 0
            elif difficulty == 3 and player_score >= 11:
                cars_per_spawn = 50
            current_time = pygame.time.get_ticks()
            time_until_next_rect = max(0, int(rect_creation_interval - (current_time - last_rect_creation_time)))
            if current_time - last_rect_creation_time >= rect_creation_interval:
                last_rect_creation_time = current_time
                for i in range(cars_per_spawn):
                    rect_x = random.randint(0, width - 50)
                    rect_y = -50
                    rect_width = 50
                    rect_height = random.randint(50, 150)
                    rect_color = (30, 30, 30)
                    rect_speed = random.randint(5, 10)
                    rectangles.append(Rectangle(rect_x, rect_y, rect_width, rect_height, rect_color, rect_speed))

                car_counter += cars_per_spawn
                ramp_up += 0.1
                rect_creation_interval = max(min_rect_creation_interval, rect_creation_interval - 300)

            if point_increase_timer > 60:
                player_score += 1
                point_increase_timer = 0
            else:
                point_increase_timer += 1

            if player_score >= 200:
                game_over = True

            win.fill((100, 100, 100))
            player.draw(win)

            for rect in rectangles:
                rect.draw(win)

            draw_text(win, f"Next Rectangle in: {time_until_next_rect/1000:.1f} seconds", (200, 200, 200), 24, width // 2, 30)
            draw_text(win, f"Score: {player_score}", (200, 200, 200), 24, width // 2, 60)
            draw_text(win, f"Cars Spawned: {car_counter}", (200, 200, 200), 24, width // 2, 90)  # Display car counter

            pygame.display.update()
            clock.tick(60)

    pygame.quit()
    sys.exit()

main_game_loop()
