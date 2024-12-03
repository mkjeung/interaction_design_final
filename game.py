import pygame
import random
import time
import json
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Makey Makey Game")
exp_sound = pygame.mixer.Sound("Minecraft XP Sound.mp3")
clock_sound = pygame.mixer.Sound("Fast Ticking clock sound effect.mp3")
fail_sound = pygame.mixer.Sound("Buzzer sound effect.wav")
click_sound = pygame.mixer.Sound("Click - Sound Effect (HD).wav")

#Loading images
logo_img = pygame.image.load("logo.png")
logo_img = pygame.transform.scale(logo_img, (500, 500))

diff_img = pygame.image.load("select_diff_title.png")
diff_img = pygame.transform.scale(diff_img, (750, 320))

bg_img = pygame.image.load("bg.png")
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

bg_img_2 = pygame.image.load("bg_2.png")
bg_img_2 = pygame.transform.scale(bg_img_2, (WIDTH, HEIGHT))

long_bg_img = pygame.image.load("long_bg.png")
long_bg_img = pygame.transform.scale(long_bg_img, (WIDTH, HEIGHT * 2))

#variables to track moving bg
bg_y = HEIGHT - long_bg_img.get_height()
bg_speed = 1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
BLUE = (65, 105, 225)
GRAY = (169, 169, 169)
DARK_GRAY = (105, 105, 105)
LIGHT_GRAY = (211, 211, 211)

# Fonts
font = pygame.font.Font("GrinchedRegular.otf", 74)
small_font = pygame.font.Font("GrinchedRegular.otf", 36)
input_font = pygame.font.Font(None, 50)

# Game variables
score = 0
leaderboard = []
choices = ["LEFT", "RIGHT"]
running = True
game_active = False
round_active = False
start_time = 0
current_direction = ""
success_message_time = 0
round_delay_time = 0
game_over = False
name_input_active = False
player_name = ""
difficulty = 'medium'
curr_selection = 'start_button'
diff_selection = 'medium_button'
leaderboard_selection = 'home_button'
LEADERBOARD_FILE = 'leaderboard.json'

# Define Game States
START_SCREEN = "start_screen"
DIFFICULTY_SCREEN = 'difficulty_screen'
COUNTDOWN = "countdown"         # New Game State for Countdown
PLAYING = "playing"
GAME_OVER = "game_over"
NAME_INPUT = "name_input"
LEADERBOARD_DISPLAY = "leaderboard_display"
RULES_SCREEN = "rules_screen"

current_state = START_SCREEN

# Load leaderboard from file
def load_leaderboard():
    global leaderboard
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Validate each entry
                valid_leaderboard = []
                for entry in data:
                    if isinstance(entry, dict) and "name" in entry and "score" in entry:
                        valid_leaderboard.append(entry)
                    else:
                        print(f"Invalid leaderboard entry skipped: {entry}")
                leaderboard = valid_leaderboard
            except json.JSONDecodeError:
                print("Leaderboard file is corrupted. Reinitializing leaderboard.")
                leaderboard = []
    else:
        leaderboard = []

# Save leaderboard to file
def save_leaderboard():
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f)

# Define Button Class
class Button:
    def __init__(self, x, y, unselected_img, selected_img, width=200, height=50, selected_bool=False):
        original_unselected = pygame.image.load(unselected_img)
        original_selected = pygame.image.load(selected_img)

        self.unselected_img = pygame.transform.scale(original_unselected, (width, height))
        self.selected_img = pygame.transform.scale(original_selected, (width, height))
        
        #makes a rect from the image
        self.rect = self.unselected_img.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.is_selected = selected_bool
        self.was_clicked = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_selected:
            surface.blit(self.selected_img, self.rect)
        elif self.rect.collidepoint(mouse_pos):
            surface.blit(self.selected_img, self.rect)
        else:
            surface.blit(self.unselected_img, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    return True
        return False

# Initialize Buttons
def initialize_buttons():
    global start_button, restart_button, leaderboard_button, rules_button, back_button, easy_button, medium_button, hard_button, home_button
    BTN_WIDTH = 160
    BTN_HEIGHT = 60

    DIFF_WIDTH = 290
    DIFF_HEIGHT = 150

    #alignment variables for menu screen
    spacing = 20
    total_width = (BTN_WIDTH * 3) + (spacing * 2)
    start_x = (WIDTH - total_width) // 2
    menu_y = HEIGHT // 2

    #alignment variables for difficulty
    total_width_diff = (DIFF_WIDTH * 3) + (spacing * 2)
    start_x_diff = ((WIDTH - total_width_diff) // 2) - 10

    start_button = Button(
        x=start_x + BTN_WIDTH + spacing,
        y=menu_y + 100,
        unselected_img="buttons/start_button.png",
        selected_img="buttons/start_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT,
        selected_bool=True
    )
    leaderboard_button = Button(
        x=start_x,
        y=menu_y + 100,
        unselected_img="buttons/leaderboard_button.png",
        selected_img="buttons/leaderboard_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT
    )

    rules_button = Button(
        x=start_x + (BTN_WIDTH + spacing) * 2,
        y=menu_y + 100,
        unselected_img="buttons/rules_button.png",
        selected_img="buttons/rules_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT
    )

    easy_button = Button(
        x=start_x_diff,
        y=menu_y + 10,
        unselected_img="buttons/easy_button.png",
        selected_img="buttons/easy_button_selected.png",
        width=DIFF_WIDTH,
        height=DIFF_HEIGHT,
    )

    medium_button = Button(
        x=start_x_diff + DIFF_WIDTH + spacing*2,
        y=menu_y + 10,
        unselected_img="buttons/medium_button.png",
        selected_img="buttons/medium_button_selected.png",
        width=DIFF_WIDTH,
        height=DIFF_HEIGHT,
        selected_bool=True
    )

    hard_button = Button(
        x= start_x_diff + (DIFF_WIDTH + spacing*2) * 2,
        y=menu_y + 10,
        unselected_img="buttons/hard_button.png",
        selected_img="buttons/hard_button_selected.png",
        width=DIFF_WIDTH,
        height=DIFF_HEIGHT
    )
    restart_button = Button(
        x=(WIDTH + spacing) // 2,
        y=HEIGHT - 100,  # Initial Y-coordinate; will adjust dynamically
        unselected_img="buttons/restart_button.png",
        selected_img="buttons/restart_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT
    )
    home_button = Button(
        x=(WIDTH - spacing - BTN_WIDTH*2) // 2,
        y=HEIGHT - 100,
        unselected_img="buttons/home_button.png",
        selected_img="buttons/home_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT,
        selected_bool=True
    )
    
    back_button = Button(
        x=(WIDTH - BTN_WIDTH) // 2,
        y=HEIGHT - 100,
        unselected_img="buttons/back_button.png",
        selected_img="buttons/back_button_selected.png",
        width=BTN_WIDTH,
        height=BTN_HEIGHT,
        selected_bool = True
    )


# Function to draw text centered
def draw_text_custom(text, color, center_x, center_y, font):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(center_x, center_y))
    screen.blit(rendered_text, text_rect)

# Function to reset the game
def reset_game():
    global score, game_active, round_active, start_time, current_direction, success_message_time, round_delay_time, game_over, name_input_active, player_name, current_state
    score = 0
    game_active = True
    round_active = False
    start_time = 0
    current_direction = ""
    success_message_time = 0
    round_delay_time = 0
    game_over = False
    name_input_active = False
    player_name = ""
    current_state = COUNTDOWN  # Transition to COUNTDOWN instead of PLAYING

# Function to update the leaderboard
def update_leaderboard(name):
    global leaderboard
    leaderboard.append({"name": name, "score": score})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:5]  # Keep top 5
    save_leaderboard()

# Function to draw the game-over screen with name input
def draw_game_over_screen():
    screen.fill(WHITE)
    draw_text_custom("Game Over!", RED, WIDTH // 2, HEIGHT // 2 - 200, font)
    draw_text_custom(f"Final Score: {score}", BLACK, WIDTH // 2, HEIGHT // 2 - 100, font)
    draw_text_custom("Enter Your Name:", BLACK, WIDTH // 2, HEIGHT // 2, small_font)
    
    # Draw input box
    input_box_width, input_box_height = 400, 50
    input_box_x = (WIDTH - input_box_width) // 2
    input_box_y = HEIGHT // 2 + 50
    input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
    pygame.draw.rect(screen, LIGHT_GRAY, input_box_rect)
    pygame.draw.rect(screen, BLACK, input_box_rect, 2)

    # Render the player's name
    name_surf = input_font.render(player_name, True, BLACK)
    name_rect = name_surf.get_rect(center=input_box_rect.center)
    screen.blit(name_surf, name_rect)
    
    # Instruction to press Enter
    draw_text_custom("Press Enter to Submit", BLACK, WIDTH // 2, input_box_y + 100, small_font)
    
    pygame.display.flip()

# Function to draw the initial start screen
def draw_start_screen():
    screen.blit(bg_img, (0, 0))

    logo_rect = logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(logo_img, logo_rect)

    start_button.draw(screen)
    leaderboard_button.draw(screen)
    rules_button.draw(screen)
    pygame.display.flip()

def draw_difficulty_screen():
    screen.blit(bg_img_2, (0, 0))
    title_rect = diff_img.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(diff_img, title_rect)

    easy_button.draw(screen)
    medium_button.draw(screen)
    hard_button.draw(screen)
    pygame.display.flip()

# Function to draw the leaderboard on game-over screen or Leaderboard Screen
def draw_leaderboard_screen():
    screen.fill(WHITE)
    draw_text_custom("Leaderboard", BLACK, WIDTH // 2, HEIGHT // 2 - 200, font)
    for i, entry in enumerate(leaderboard):
        entry_text = f"{i + 1}. {entry['name']} - {entry['score']}"
        draw_text_custom(entry_text, BLACK, WIDTH // 2, HEIGHT // 2 - 100 + i * 40, small_font)
    # Draw restart button and home button
    restart_button.draw(screen)
    home_button.draw(screen)
    pygame.display.flip()

def return_to_home():
    global current_state, score, game_active, round_active, start_time, current_direction
    global success_message_time, round_delay_time, game_over, name_input_active, player_name
    # Reset everything and go back to start screen
    score = 0
    game_active = False
    round_active = False
    start_time = 0
    current_direction = ""
    success_message_time = 0
    round_delay_time = 0
    game_over = False
    name_input_active = False
    player_name = ""
    current_state = START_SCREEN
    curr_selection = 'start_button'

# Function to draw the rules screen
def draw_rules_screen():
    screen.fill(WHITE)
    draw_text_custom("Game Rules", BLACK, WIDTH // 2, 100, font)
    rules_text = [
        "Welcome to the Makey Makey Game!",
        "",
        "How to Play:",
        "1. The game will display a direction (LEFT or RIGHT).",
        "2. Do a pull up in the correct direction.",
        "3. You have 5 seconds to complete the pull up.",
        "4. Each correct response increases your score by 1.",
        "5. Incorrect responses decrease your score by 1.",
        "6. The game ends when you fail to respond within the time limit.",
        "Try to achieve the highest score possible!"
    ]
    for i, line in enumerate(rules_text):
        draw_text_custom(line, BLACK, WIDTH // 2, 200 + i * 30, small_font)
    # Draw Back button
    back_button.draw(screen)
    pygame.display.flip()

# Function to handle name input
def handle_name_input(event):
    global player_name, name_input_active, current_state
    if event.type == pygame.KEYUP and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
        current_state = LEADERBOARD_DISPLAY
    if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_RETURN:
            if player_name.strip() != "":
                update_leaderboard(player_name.strip())
                name_input_active = False
                current_state = LEADERBOARD_DISPLAY
        elif event.key == pygame.K_BACKSPACE:
            player_name = player_name[:-1]
        else:
            if len(player_name) < 20 and event.unicode.isprintable():
                player_name += event.unicode

# Function to check if score qualifies for leaderboard
def is_score_qualify(score):
    if len(leaderboard) < 5:
        return True
    min_score = min(entry["score"] for entry in leaderboard)
    return score > min_score

# Initialize buttons and load leaderboard
initialize_buttons()
load_leaderboard()

# Initialize countdown variables
countdown_start_ticks = 0  # will be set when entering COUNTDOWN state
countdown_duration = 5      # 5 seconds

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_sound.play()

        # Handle events based on current state
        if current_state == START_SCREEN:
            if event.type == pygame.KEYUP:
                click_sound.play()
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if curr_selection == 'start_button':
                        current_state = DIFFICULTY_SCREEN
                    if curr_selection == 'leaderboard_button':
                        current_state = LEADERBOARD_DISPLAY
                    if curr_selection == 'rules_button':
                        current_state = RULES_SCREEN
                elif event.key == pygame.K_UP:
                    if curr_selection == 'start_button':
                        start_button.is_selected = False
                        rules_button.is_selected  = True
                        curr_selection = 'rules_button'
                        print(curr_selection)
                    elif curr_selection == 'leaderboard_button':
                        leaderboard_button.is_selected = False
                        start_button.is_selected = True
                        curr_selection = 'start_button'
                        print(curr_selection)
                elif event.key == pygame.K_DOWN:
                    if curr_selection == 'rules_button':
                        rules_button.is_selected = False
                        start_button.is_selected = True
                        curr_selection = 'start_button'
                        print(curr_selection)
                    elif curr_selection == 'start_button':
                        start_button.is_selected = False
                        leaderboard_button.is_selected = True
                        curr_selection = 'leaderboard_button'
                        print(curr_selection)
            if start_button.is_clicked(event):
                current_state = DIFFICULTY_SCREEN
            if leaderboard_button.is_clicked(event):
                current_state = LEADERBOARD_DISPLAY
            if rules_button.is_clicked(event):
                current_state = RULES_SCREEN
        elif current_state == DIFFICULTY_SCREEN:
            if event.type == pygame.KEYUP:
                click_sound.play()
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    current_state = COUNTDOWN
                    countdown_start_ticks = pygame.time.get_ticks()  # Record the start time
                elif event.key == pygame.K_DOWN:
                    if diff_selection == 'medium_button':
                        countdown_duration = 10
                        medium_button.is_selected = False
                        easy_button.is_selected  = True
                        diff_selection = 'easy_button'
                    elif diff_selection == 'hard_button':
                        coutndown_duration = 5
                        hard_button.is_selected = False
                        medium_button.is_selected = True
                        diff_selection = 'medium_button'
                elif event.key == pygame.K_UP:
                    if diff_selection == 'medium_button':
                        countdown_duration = 3
                        medium_button.is_selected = False
                        hard_button.is_selected = True
                        diff_selection = 'hard_button'
                    elif diff_selection == 'easy_button':
                        countdown_duration = 5
                        easy_button.is_selected = False
                        medium_button.is_selected = True
                        diff_selection = 'medium_button'
            if easy_button.is_clicked(event):
                countdown_duration = 10
                current_state = COUNTDOWN
                countdown_start_ticks = pygame.time.get_ticks()  # Record the start time
            elif medium_button.is_clicked(event):
                countdown_duration = 5
                current_state = COUNTDOWN
                countdown_start_ticks = pygame.time.get_ticks()  # Record the start time
            elif hard_button.is_clicked(event):
                countdown_duration = 3
                current_state = COUNTDOWN
                countdown_start_ticks = pygame.time.get_ticks()  # Record the start time

        elif current_state == PLAYING:
            if event.type == pygame.KEYDOWN and round_active:
                key_matched = False
                if event.key == pygame.K_LEFT and current_direction == "LEFT":
                    score += 1
                    key_matched = True
                    clock_sound.stop()
                    exp_sound.play()
                elif event.key == pygame.K_RIGHT and current_direction == "RIGHT":
                    score += 1
                    key_matched = True
                    clock_sound.stop()
                    exp_sound.play()
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    score -= 1
                    clock_sound.stop()
                    fail_sound.play()
                if key_matched or event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    success_message_time = time.time()
                    round_active = False
                    round_delay_time = time.time()
            # --- Change Start ---
            # Trigger Game Over on Up/Down Key Release
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    clock_sound.stop()
                    fail_sound.play()
                    current_state = GAME_OVER
            # --- Change End ---

        elif current_state == GAME_OVER:
            if is_score_qualify(score):
                current_state = NAME_INPUT
            else:
                current_state = LEADERBOARD_DISPLAY
                if not any(entry["score"] == score for entry in leaderboard):
                    update_leaderboard("Anonymous")

        elif current_state == NAME_INPUT:
            handle_name_input(event)

        elif current_state == LEADERBOARD_DISPLAY:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if leaderboard_selection == 'home_button':
                        current_state = START_SCREEN
                    else:
                        restart_button.is_selected = False
                        home_button.is_selected = True
                        leaderboard_selection = 'home_button'
                        leaderboard_button.is_selected = False
                        start_button.is_selected = True
                        curr_selection = 'start_button'
                        current_state = DIFFICULTY_SCREEN
                if event.key == pygame.K_DOWN and leaderboard_selection == 'home_button':
                    home_button.is_selected = False
                    restart_button.is_selected = True
                    leaderboard_selection = 'restart_button'
                elif event.key == pygame.K_UP and leaderboard_selection == 'restart_button':
                    restart_button.is_selected = False
                    home_button.is_selected = True
                    leaderboard_selection = 'home_button'
            if restart_button.is_clicked(event):
                restart_button.is_selected = False
                home_button.is_selected = True
                leaderboard_button.is_selected = False
                start_button.is_selected = True
                curr_selection = 'start_button'
                leaderboard_selection = 'home_button'
                current_state = DIFFICULTY_SCREEN
            elif home_button.is_clicked(event):
                return_to_home()

        elif current_state == RULES_SCREEN:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    current_state = START_SCREEN
            if back_button.is_clicked(event):
                current_state = START_SCREEN

        elif current_state == COUNTDOWN:
            pass  # No event handling needed during countdown

    # Handle game states
    if current_state == START_SCREEN:
        draw_start_screen()

    elif current_state == DIFFICULTY_SCREEN:
        draw_difficulty_screen()

    elif current_state == COUNTDOWN:
        # Calculate elapsed time in seconds
        seconds_elapsed = (pygame.time.get_ticks() - countdown_start_ticks) // 1000
        seconds_left = 5 - seconds_elapsed

        if seconds_left > 0:
            screen.fill(WHITE)
            countdown_text = str(seconds_left)
            draw_text_custom(countdown_text, BLACK, WIDTH // 2, HEIGHT // 2, font)
            pygame.display.flip()
        else:
            # Countdown finished, transition to PLAYING
            current_state = PLAYING
            game_active = True
            round_active = False
            start_time = 0
            current_direction = ""
            success_message_time = 0
            round_delay_time = 0
            game_over = False
            name_input_active = False
            player_name = ""

    elif current_state == PLAYING:
        screen.fill(WHITE)

        if not round_active:
            if time.time() - round_delay_time > 1:  # 1-second delay between rounds
                clock_sound.play()
                current_direction = random.choice(choices)
                round_active = True
                start_time = time.time()

        # Calculate remaining time
        elapsed_time = time.time() - start_time
        remaining_time = max(0, countdown_duration - int(elapsed_time))  # Countdown from 5 seconds

        if round_active and remaining_time == 0:
            clock_sound.stop()
            fail_sound.play()
            game_active = False
            game_over = True
            current_state = GAME_OVER

        if round_active:
            if bg_y < 0:
                bg_y += bg_speed
            else:
                bg_y = 0
        else:
            bg_y = HEIGHT - long_bg_img.get_height()

        screen.blit(long_bg_img, (0, bg_y))
        print(f"bg_y: {bg_y}")

        # Display the direction and timer if the round is active
        if round_active:
            draw_text_custom(current_direction, BLUE, WIDTH // 2, HEIGHT // 2 - 50, font)
            draw_text_custom(f"Time: {remaining_time}", BLACK, WIDTH // 2, HEIGHT // 2 - 150, small_font)

        # Display the score
        draw_text_custom(f"Score: {score}", BLACK, 70, 30, small_font)

        # Display success or failure message
        if success_message_time > 0 and time.time() - success_message_time < 2:  # Show message for 2 seconds
            if score >= 0:
                message = "Great Job!" if score > 0 else "Try Again!"
                message_color = GREEN if score > 0 else RED
                draw_text_custom(message, message_color, WIDTH // 2, HEIGHT // 2 + 100, small_font)

        pygame.display.flip()

    elif current_state == GAME_OVER:
        if is_score_qualify(score):
            current_state = NAME_INPUT
        else:
            current_state = LEADERBOARD_DISPLAY
            if not any(entry["score"] == score for entry in leaderboard):
                update_leaderboard("Anonymous")

    elif current_state == NAME_INPUT:
        draw_game_over_screen()

    elif current_state == LEADERBOARD_DISPLAY:
        draw_leaderboard_screen()

    elif current_state == RULES_SCREEN:
        draw_rules_screen()

pygame.quit()