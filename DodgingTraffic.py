import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Helper function to find resource paths for Pyninstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
clock = pygame.time.Clock()

# Initialize the joysticks for two controllers
pygame.joystick.init()
joystick1 = None
joystick2 = None
if pygame.joystick.get_count() > 0:
    joystick1 = pygame.joystick.Joystick(0)
    joystick1.init()
if pygame.joystick.get_count() > 1:
    joystick2 = pygame.joystick.Joystick(1)
    joystick2.init()

font_path = resource_path("GresickMetal-51LXV.otf")
font = pygame.font.Font(font_path, 32)

displayInfo = pygame.display.Info()
width, height = displayInfo.current_w, displayInfo.current_h
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Child In Traffic")

# Define scalable text sizes
MEDIUM_TEXT_SIZE = max(24, int(height * 0.04))
LARGE_TEXT_SIZE = max(48, int(height * 0.09))

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
rect_creation_interval = random.randint(2000, 3000)
min_rect_creation_interval = 200

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

score_increment_period = {0: 60, 1: 30, 2: 10, 3: 30} # Increase score every x frames

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
    "There is the possibility that your parents (if exising) might win the lawsuit, \n but I doubt that driver will share the dash-cam",
    "The Child did not want to live anymore. After contemplating his life,\n he decided to end it in the best way possible, death by car.",
    # Quirky Stories
    "Well, he gone",
    "Nooo, my boy. Anyways...",
    "You are DEAD, not big surprise.",
    "Thats what you get for not looking both ways before crossing the street.",
    "My brother was hit by a car once. He's fine now, but he's a little... flat-brained.",
    # Minor "Humor" Stories
    "L",
    "F",
    "...",
    "Rest in Peperonis",
    "Uh oh!\n Stinky!",
    "Would you consider 'cracked' as in the child's skull, or as in the driver is doing some HEAVY weed?",
    # COMPLETE BRAINROT REMOVE IF ADULTS PLAY PLEASE!!!!!
    "YA BOI WAS HIT BY A BIG ASS TRUCK.",
    "Oh, they're gonna have to glue you back together... IN HELL!",
    "transgender?, more like, trans-plowed into a STEAMING HOT PILE OF TRASH!"
    "BEEP BEEP MO- (The driver's lawyer advised him not to finish this sentence)",
    "Bro thought he was in GTAVI and tried to steal a car. He got hit by a car instead.",
    "The van with free candy didn't have free candy... nor black men... nor furries... nor drug addicts...",
    "The little shit got yeeted into the shadow realm by some\n booze-cranked driver in his skyscraper-like pimped-up diesel 48ft Uhaul.",
    "The child was wearing a fursuit. Someone apperently called the SWAT on them,\n and \"it\" got splattered in front of a cheering crowd. The end.",
    "YOU FAT BALD BASTARD YOU PIECE OF SUBHUMAN TRASH 2000 YEARS OF CONSTANT EVOLUTION TO CREATE\n A HAIRLESS FUCKING COCONUT MY GOD WHAT IS WRONG WITH YOU???",
    "Are ya listening? Okay. Grass grows, birds, fly, sun shines, and brudda?\n I HURT PEOPLE! Im a force of nature. If you were from, where I was from, you'd be from, where I was from. You'd be ded."
    # LORE DROPS
    "[purple] parallel universes, are they real?"
    "INSERT LORE HERE" # do so me (matt)
]


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

def draw_text(surface, text, color, font_size, x, y):
    color_map = {
        "[red]": (255, 0, 0),
        "[blue]": (0, 0, 255),
        "[green]": (0, 255, 0),
        "[yellow]": (255, 255, 0),
        "[purple]": (128, 0, 128),
        "[orange]": (255, 165, 0),
        "[pink]": (255, 192, 203),
        "[black]": (0, 0, 0),
        # Add more colors if needed
    }
    default_color = (30, 30, 30)
    words = text.split()
    current_color = color

    # Use a temp font for the requested size
    temp_font = pygame.font.Font(font_path, font_size)
    # Find the max ascent (height above baseline)
    max_ascent = temp_font.get_ascent()
    total_width = sum(temp_font.size(word + " ")[0] for word in words if word not in color_map)
    current_x = x - total_width // 2

    for word in words:
        if word in color_map:
            current_color = color_map[word]
        else:
            text_surface = temp_font.render(word + " ", True, current_color)
            text_rect = text_surface.get_rect()
            # Align all words to the same baseline
            blit_y = y + (max_ascent - text_rect.height + temp_font.get_descent())
            surface.blit(text_surface, (current_x, blit_y))
            current_x += text_surface.get_width()

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
        draw_text(win, "Enter your name:", (30, 30, 30), MEDIUM_TEXT_SIZE, width // 2, height // 6)
        draw_text(win, text, (30, 30, 30), MEDIUM_TEXT_SIZE, width // 2, height // 3)

        cursor_timer += 1
        if cursor_timer % 1000 == 0: 
            cursor_blink = not cursor_blink

        if cursor_blink:
            draw_text(win, "|", (30, 30, 30), MEDIUM_TEXT_SIZE, width // 2 + font.size(text)[0] // 2, height // 3)

        if joystick1 and pygame.joystick.get_count() > 0:
            for r, row_keys in enumerate(keys_layout):
                row_keys_split = row_keys.split()
                for c, key in enumerate(row_keys_split):
                    key_x = (width // 2 - (len(row_keys_split) * (key_width + spacing)) // 2) + c * (key_width + spacing)
                    key_y = (height // 2 + r * (key_height + spacing))
                    key_rect = pygame.Rect(key_x, key_y, key_width, key_height)
                    pygame.draw.rect(win, (0, 0, 0) if (r, c) == (row, col) else (255, 255, 255), key_rect)
                    draw_text(win, key, (0, 0, 0), MEDIUM_TEXT_SIZE, key_x + key_width // 2, key_y + 10)

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
            elif joystick1 and pygame.joystick.get_count() > 0:
                if event.type == pygame.JOYHATMOTION:
                    hat = joystick1.get_hat(0)
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
    single_player_menu()
    get_input()
    play_music(music_Game)

def pause_menu_display():
    global is_paused
    options = ["Resume", "Quit"]
    selected_option = 0
    while is_paused:
        win.fill((50, 50, 50))
        draw_text(win, "Paused", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 4)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, MEDIUM_TEXT_SIZE, width // 2, height // 2 + i * (MEDIUM_TEXT_SIZE + 10))
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
                if joystick1:
                    if event.button == 0:  # A button
                        if selected_option == 0:
                            is_paused = False
                        elif selected_option == 1:
                            pygame.quit()
                            sys.exit()
            elif event.type == pygame.JOYAXISMOTION:
                if joystick1:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(200)  # Add delay to prevent rapid scrolling
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(200)  # Add delay to prevent rapid scrolling
            elif event.type == pygame.JOYHATMOTION:
                if joystick1:
                    hat = joystick1.get_hat(0)
                    if hat[1] == 1:
                        selected_option = (selected_option - 1) % len(options)
                    elif hat[1] == -1:
                        selected_option = (selected_option + 1) % len(options)

def intro_sequence():
    fade_duration = 2500
    text = "Presented by:\n\nBailiwicks Studios"
    font_size = LARGE_TEXT_SIZE
    text_color = (255, 255, 255)
    bg_color = (0, 0, 0)
    win.fill(bg_color)
    pygame.display.update()
    wait_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - wait_start < 1000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)
    try:
        play_sfx("audio/ding.mp3")
    except:
        pass
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill(bg_color)
    start_time = pygame.time.get_ticks()
    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed > fade_duration:
            break
        alpha = int(255 * (elapsed / fade_duration))
        win.fill(bg_color)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            draw_text(win, line, text_color, font_size, width // 2, height // 2 - (len(lines)-1)*font_size//2 + i*font_size)
        fade_surface.set_alpha(alpha)
        win.blit(fade_surface, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)
    win.fill((100, 100, 100))
    pygame.display.update()

def single_player_menu():
    global running, cars_per_spawn, difficulty 
    play_music(music_MainMenu)
    selected_option = 0
    options = ["Easy", "Medium", "Rush Hour", "" ] #<<feature not bug
    
    while True:
        win.fill((100, 100, 100))
        draw_text(win, "Child in Traffic (True Story)", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 6)
        draw_text(win, "Select Difficulty:", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3)

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, MEDIUM_TEXT_SIZE, width // 2, height // 2 + i * (MEDIUM_TEXT_SIZE + 10))

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
                if joystick1:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(50)  
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(50)  
            elif event.type == pygame.JOYHATMOTION:
                if joystick1:
                    hat = joystick1.get_hat(0)
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

def main_menu():
    global running
    play_music(music_MainMenu)
    selected_option = 0
    options = ["Single Player", "Multiplayer", "Credits", "Quit"]
    while running:
        win.fill((100, 100, 100))
        draw_text(win, "Child in Traffic", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 6)
        draw_text(win, "Choose a Mode", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, MEDIUM_TEXT_SIZE, width // 2, height // 2 + i * (MEDIUM_TEXT_SIZE + 10))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return 'single'
                    elif selected_option == 1:
                        return 'multi'
                    elif selected_option == 2:
                        credits()
                    elif selected_option == 3:
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if selected_option == 0:
                        return 'single'
                    elif selected_option == 1:
                        return 'multi'
                    elif selected_option == 2:
                        credits()
                    elif selected_option == 3:
                        pygame.quit()
                        sys.exit()
                elif event.button == 1:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.JOYAXISMOTION:
                if joystick1:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(200)
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(200)
            elif event.type == pygame.JOYHATMOTION:
                if joystick1:
                    hat = joystick1.get_hat(0)
                    if hat[1] == 1:
                        selected_option = (selected_option - 1) % len(options)
                    elif hat[1] == -1:
                        selected_option = (selected_option + 1) % len(options)

def multiplayer_menu():
    global running, cars_per_spawn, difficulty
    play_music(music_MainMenu)
    selected_option = 0
    options = ["Easy", "Medium", "Rush Hour", ""]
    while True:
        win.fill((100, 100, 100))
        draw_text(win, "Multiplayer Menu", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 6)
        draw_text(win, "Select Difficulty:", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (200, 200, 200)
            draw_text(win, option, color, MEDIUM_TEXT_SIZE, width // 2, height // 2 + i * (MEDIUM_TEXT_SIZE + 4))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return None
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    difficulty = selected_option
                    return
            elif event.type == pygame.JOYAXISMOTION:
                if joystick1:
                    if event.axis == 1:
                        if event.value < -0.5:
                            selected_option = (selected_option - 1) % len(options)
                            pygame.time.wait(50)
                        elif event.value > 0.5:
                            selected_option = (selected_option + 1) % len(options)
                            pygame.time.wait(50)
            elif event.type == pygame.JOYHATMOTION:
                if joystick1:
                    hat = joystick1.get_hat(0)
                    if hat[1] == 1:
                        selected_option = (selected_option - 1) % len(options)
                    elif hat[1] == -1:
                        selected_option = (selected_option + 1) % len(options)
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    difficulty = selected_option
                    return

def multiplayer_game_loop():
    global running, game_over, is_paused, player_score, score_saved, selected_backstory, car_counter, ramp_up, rect_creation_interval, last_rect_creation_time, rectangles, point_increase_timer, score_increment_period, difficulty
    multiplayer_menu()
    play_music(music_Game)
    player1 = Player(2 * width // 3, height // 2, 20, (200, 200, 200))
    player2 = Player(width // 3, height // 2, 20, (0, 200, 0))
    rectangles = []
    player_score = 0
    game_over = False
    score_saved = False
    last_rect_creation_time = pygame.time.get_ticks()
    rect_creation_interval = random.randint(2000, 3000)
    ramp_up = 1
    car_counter = 0
    i4_mode_start_time = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_paused = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if joystick1:
                    if event.button == 0:
                        if game_over:
                            running = False
                    elif event.button == 1:
                        game_over = True
            if not game_over and not is_paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        is_paused = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    if joystick1 and event.button in [2, 3]:
                        is_paused = True
        if game_over:
            pygame.mixer.music.stop()
            win.fill((100, 100, 100))
            player1_hit = False
            player2_hit = False
            for rect in rectangles:
                if player1.collide_with(rect):
                    player1_hit = True
                if player2.collide_with(rect):
                    player2_hit = True
            if player1_hit and player2_hit:
                hit_text = "Both players were hit at the same time"
            elif player1_hit:
                hit_text = "Player 1 was hit"
            elif player2_hit:
                hit_text = "Player 2 was hit"
            else:
                hit_text = "A player was hit"
            draw_text(win, hit_text, (255, 100, 100), MEDIUM_TEXT_SIZE, width // 2, height // 3 - 100)
            draw_text(win, "Game Over", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 3 - 20)
            draw_text(win, "Press any key to play again", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3 + 50)
            draw_text(win, "Press 'Esc' or 'B' button to quit", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3 + 100)
            draw_text(win, f"Score: {player_score}", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 2)
            draw_text(win, "", (200, 200, 200), 15, width // 2, height * 2 // 3 - 40)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key not in [
                        pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
                    ]:
                        return
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1:
                        running = False
                    else:
                        return
        elif is_paused:
            pause_menu_display()
        else:
            keys = pygame.key.get_pressed()
            # Player 1: Arrow keys or joystick1
            x_axis_changed1, y_axis_changed1 = 0, 0
            if keys[pygame.K_DOWN] or keys[pygame.K_UP]:
                y_axis_changed1 = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                x_axis_changed1 = 1
            if keys[pygame.K_LEFT]:
                player1.x -= player1.speed / (1 + (.4 * y_axis_changed1))
            elif keys[pygame.K_RIGHT]:
                player1.x += player1.speed / (1 + (.4 * y_axis_changed1))
            if keys[pygame.K_UP]:
                player1.y -= player1.speed / (1 + (.4 * x_axis_changed1))
            elif keys[pygame.K_DOWN]:
                player1.y += player1.speed / (1 + (.4 * x_axis_changed1))
            # Joystick 1 (controller 1, player 1)
            if joystick1:
                axis0 = joystick1.get_axis(0)
                axis1 = joystick1.get_axis(1)
                player1.x += (axis0 * player1.speed) / (1 + (.4 * abs(axis1)))
                player1.y += (axis1 * player1.speed) / (1 + (.4 * abs(axis0)))
            # Player 2: WASD or joystick2
            x_axis_changed2, y_axis_changed2 = 0, 0
            if keys[pygame.K_s] or keys[pygame.K_w]:
                y_axis_changed2 = 1
            if keys[pygame.K_a] or keys[pygame.K_d]:
                x_axis_changed2 = 1
            if keys[pygame.K_a]:
                player2.x -= player2.speed / (1 + (.4 * y_axis_changed2))
            elif keys[pygame.K_d]:
                player2.x += player2.speed / (1 + (.4 * y_axis_changed2))
            if keys[pygame.K_w]:
                player2.y -= player2.speed / (1 + (.4 * x_axis_changed2))
            elif keys[pygame.K_s]:
                player2.y += player2.speed / (1 + (.4 * x_axis_changed2))
            # Joystick 2 (controller 2, player 2)
            if joystick2:
                axis0 = joystick2.get_axis(0)
                axis1 = joystick2.get_axis(1)
                player2.x += (axis0 * player2.speed) / (1 + (.4 * abs(axis1)))
                player2.y += (axis1 * player2.speed) / (1 + (.4 * abs(axis0)))
            # Clamp player positions
            player1.x = max(player1.radius, min(player1.x, width - player1.radius))
            player1.y = max(player1.radius, min(player1.y, height - player1.radius))
            player2.x = max(player2.radius, min(player2.x, width - player2.radius))
            player2.y = max(player2.radius, min(player2.y, height - player2.radius))
            # Prevent player overlap and allow pushing
            dx = player2.x - player1.x
            dy = player2.y - player1.y
            dist = math.hypot(dx, dy)
            min_dist = player1.radius + player2.radius
            if dist < min_dist and dist != 0:
                overlap = min_dist - dist
                nx = dx / dist
                ny = dy / dist
                player1.x -= nx * (overlap / 2)
                player1.y -= ny * (overlap / 2)
                player2.x += nx * (overlap / 2)
                player2.y += ny * (overlap / 2)
                player1.x = max(player1.radius, min(player1.x, width - player1.radius))
                player1.y = max(player1.radius, min(player1.y, height - player1.radius))
                player2.x = max(player2.radius, min(player2.x, width - player2.radius))
                player2.y = max(player2.radius, min(player2.y, height - player2.radius))
            for rect in rectangles:
                rect.update()
            rectangles = [rect for rect in rectangles if not rect.is_off_screen()]
            for rect in rectangles:
                if player1.collide_with(rect) or player2.collide_with(rect):
                    play_sfx(sfx_Death)
                    game_over = True
                    break
            if difficulty == 0:
                cars_per_spawn = 1
            elif difficulty == 1:
                cars_per_spawn = 2
            elif difficulty == 2:
                cars_per_spawn = 3
            elif difficulty == 3:
                if i4_mode_start_time is None:
                    i4_mode_start_time = pygame.time.get_ticks()
                time_in_i4 = (pygame.time.get_ticks() - i4_mode_start_time) / 1000.0
                if (player_score >= 21) or (i4_mode_start_time and (pygame.time.get_ticks() - i4_mode_start_time) > 11000):
                    cars_per_spawn = 50
                else:
                    ramp_up += 1
                    cars_per_spawn = 0
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
                ramp_up += 0.06
                rect_creation_interval = max(min_rect_creation_interval, rect_creation_interval - 300)
            if point_increase_timer > score_increment_period[difficulty]:
                player_score += 1
                point_increase_timer = 0
            else:
                point_increase_timer += 1
            if player_score >= 500 and difficulty != 3:
                win.fill((100, 100, 100))
                draw_text(win, "Is this too easy?", (200, 200, 200), 72, width // 2, height // 3)
                draw_text(win, "Difficulty set to I4-MODE!", (200, 200, 200), 36, width // 2, height // 2)
                pygame.display.update()
                pygame.time.wait(3000)
                difficulty = 3
            win.fill((100, 100, 100))
            player1.draw(win)
            player2.draw(win)
            for rect in rectangles:
                rect.draw(win)
            draw_text(win, f"Next Car in: {time_until_next_rect/1000:.1f} seconds", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, 30)
            draw_text(win, f"Score: {player_score}", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, 70)

            pygame.display.update()
            clock.tick(60)
    pygame.quit()
    sys.exit()

def main_game_loop():
    global running, game_over, score_saved, is_paused, player_score, selected_backstory, rectangles, last_rect_creation_time, rect_creation_interval, ramp_up, car_counter, point_increase_timer, score_increment_period, difficulty
    while running:
        mode = main_menu()
        if mode == 'single':
            single_player_menu()
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
                        if joystick1:
                            if event.button == 0:
                                if game_over:
                                    running = False
                            elif event.button == 1:
                                game_over = True
                if game_over:
                    pygame.mixer.music.stop()
                    win.fill((100, 100, 100))
                    draw_text(win, "Game Over", (200, 200, 200), LARGE_TEXT_SIZE, width // 2, height // 3 - 60)
                    draw_text(win, "Press any key to play again", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3 + 40)
                    draw_text(win, "Press 'Esc' or 'B' button to quit", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 3 + 80)
                    draw_text(win, f"Your Score: {player_score}", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 2)
                    draw_text(win, "", (200, 200, 200), 15, width // 2, height * 2 // 3 - 40)

                    if not score_saved:
                        save_score(player_name, player_score)
                        score_saved = True
                        selected_backstory = random.choice(backstories)

                    scores = load_scores()
                    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
                    if top_scores:
                        draw_text(win, "Top Scores:", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 2 + 100)
                        y_offset = 0
                        for i, (name, score) in enumerate(top_scores):
                            draw_text(win, f"{i+1}. {name}: {score}", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height // 2 + 150 + y_offset)
                            y_offset += MEDIUM_TEXT_SIZE + 6

                    # Display only one backstory, split by \n
                    backstory_lines = selected_backstory.split('\n')
                    for i, line in enumerate(backstory_lines):
                        draw_text(win, line, (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, height - 100 + i * (MEDIUM_TEXT_SIZE + 4))

                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                            else:
                                reset_game()
                elif is_paused:
                    pause_menu_display()
                else:
                    keys = pygame.key.get_pressed()

                    # Keyboard movement
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
                    # Joystick 1 (controller 1, player 1)
                    if joystick1:
                        axis0 = joystick1.get_axis(0)
                        axis1 = joystick1.get_axis(1)
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
                    elif difficulty == 3 and player_score < 21:
                        ramp_up +=1
                        cars_per_spawn = 0
                    elif difficulty == 3 and player_score >= 21:
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
                        ramp_up += 0.06
                        rect_creation_interval = max(min_rect_creation_interval, rect_creation_interval - 300)

                    if point_increase_timer > score_increment_period[difficulty]:
                        player_score += 1
                        point_increase_timer = 0
                    else:
                        point_increase_timer += 1

                    if player_score >= 500 and difficulty != 3:
                        win.fill((100, 100, 100))
                        draw_text(win, "Is this too easy?", (200, 200, 200), 72, width // 2, height // 3)
                        draw_text(win, "Difficulty set to I4-MODE!", (200, 200, 200), 36, width // 2, height // 2)
                        pygame.display.update()
                        pygame.time.wait(3000)  # Wait for 3 seconds
                        difficulty = 3

                    win.fill((100, 100, 100))
                    player.draw(win)

                    for rect in rectangles:
                        rect.draw(win)

                    draw_text(win, f"Next Car in: {time_until_next_rect/1000:.1f} seconds", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2, 30)
                    draw_text(win, f"Score: {player_score}", (200, 200, 200), MEDIUM_TEXT_SIZE, width // 2 + 10, 70)

                    pygame.display.update()
                    clock.tick(60)
        elif mode == 'multi':
            multiplayer_game_loop()
        else:
            break

def credits():
    main_credits = [
        ("Kian", "Original Concept Design"),
        ("Matthew", "Lead Developer and Designer"),
        ("Ethan Ortiz", "Sénior Dévélopér")
    ]
    scrolling_credits = [
        "Music:",
        "Mario Kart Wii - Game Menu",
        "Mario Kart Wii - Loss",
        "AlexGrohl - Metal (Dark Matter)",
        "Credits - Bach No. 1 in G Major",
        "",
        "Special Thanks: Scott, Kian, and all playtesters!",
        "",
        "Made with Python",
        "Bailiwicks Studios (c)2025"
    ]

    play_music(music_MainMenu)

    display_time = 2500 
    for name, note in main_credits:
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < display_time:
            win.fill((30, 30, 30))
            draw_text(win, name, (255, 255, 255), 72, width // 2, height // 2 - 40)
            draw_text(win, note, (200, 200, 200), 36, width // 2, height // 2 + 40)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(60)

    # Scrolling credits
    font_size = MEDIUM_TEXT_SIZE
    spacing = int(MEDIUM_TEXT_SIZE * 0.55)
    total_height = len(scrolling_credits) * (font_size + spacing)
    scroll_speed = 2  # pixels per frame
    y_start = height
    y_end = -total_height
    y = y_start
    while y > y_end:
        win.fill((30, 30, 30))
        for i, line in enumerate(scrolling_credits):
            y_pos = y + i * (font_size + spacing)
            draw_text(win, line, (255, 255, 255), font_size, width // 2, y_pos)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        y -= scroll_speed
        clock.tick(60)
    # Wait a moment at the end
    pygame.time.wait(1000)

intro_sequence()
main_game_loop()