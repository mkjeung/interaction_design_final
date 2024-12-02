import pygame
import random
import time
import json
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Makey Makey Game")
exp_sound = pygame.mixer.Sound("Minecraft XP Sound.mp3")
clock_sound = pygame.mixer.Sound("Fast Ticking clock sound effect.mp3")
fail_sound = pygame.mixer.Sound("Buzzer sound effect.wav")
click_sound = pygame.mixer.Sound("Click - Sound Effect (HD).wav")


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
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
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
LEADERBOARD_FILE = 'leaderboard.json'

# Define Game States
START_SCREEN = "start_screen"
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
    def __init__(self, x, y, width, height, color, hover_color, text, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = font

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        
        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    return True
        return False

# Initialize Buttons
def initialize_buttons():
    global start_button, restart_button, leaderboard_button, rules_button, back_button
    button_width, button_height = 200, 50
    start_button = Button(
        x=(WIDTH - button_width) // 2,
        y=(HEIGHT) // 2 - 100,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Start",
        text_color=BLACK,
        font=small_font
    )
    leaderboard_button = Button(
        x=(WIDTH - button_width) // 2,
        y=(HEIGHT) // 2 - 30,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Leaderboard",
        text_color=BLACK,
        font=small_font
    )
    rules_button = Button(
        x=(WIDTH - button_width) // 2,
        y=(HEIGHT) // 2 + 40,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Rules",
        text_color=BLACK,
        font=small_font
    )

    easy_button = Button(
        x=(WIDTH - button_width) // 2 - 250,
        y=(HEIGHT) // 2 + 110,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Easy",
        text_color=BLACK,
        font=small_font
    )

    medium_button = Button(
        x=(WIDTH - button_width) // 2,
        y=(HEIGHT) // 2 + 110,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Medium",
        text_color=BLACK,
        font=small_font
    )

    hard_button = Button(
        x=(WIDTH - button_width) // 2 + 250,
        y=(HEIGHT) // 2 + 110,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Hard",
        text_color=BLACK,
        font=small_font
    )
    restart_button = Button(
        x=(WIDTH - button_width) // 2,
        y=HEIGHT - 100,  # Initial Y-coordinate; will adjust dynamically
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Restart",
        text_color=BLACK,
        font=small_font
    )
    back_button = Button(
        x=WIDTH - button_width - 50,
        y=HEIGHT - button_height - 50,
        width=button_width,
        height=button_height,
        color=GRAY,
        hover_color=DARK_GRAY,
        text="Back",
        text_color=BLACK,
        font=small_font
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
    screen.fill(WHITE)
    draw_text_custom("Makey Makey Game", BLACK, WIDTH // 2, HEIGHT // 2 - 200, font)
    start_button.draw(screen)
    leaderboard_button.draw(screen)
    rules_button.draw(screen)
    pygame.display.flip()

# Function to draw the leaderboard on game-over screen or Leaderboard Screen
def draw_leaderboard_screen():
    screen.fill(WHITE)
    draw_text_custom("Leaderboard", BLACK, WIDTH // 2, HEIGHT // 2 - 200, font)
    for i, entry in enumerate(leaderboard):
        entry_text = f"{i + 1}. {entry['name']} - {entry['score']}"
        draw_text_custom(entry_text, BLACK, WIDTH // 2, HEIGHT // 2 - 100 + i * 40, small_font)
    # Draw Back button
    back_button.draw(screen)
    pygame.display.flip()

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
            if start_button.is_clicked(event):
                # Transition to COUNTDOWN state
                current_state = COUNTDOWN
                countdown_start_ticks = pygame.time.get_ticks()  # Record the start time
            if leaderboard_button.is_clicked(event):
                current_state = LEADERBOARD_DISPLAY
            if rules_button.is_clicked(event):
                current_state = RULES_SCREEN

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
            if back_button.is_clicked(event):
                current_state = START_SCREEN
            if restart_button.is_clicked(event):
                reset_game()

        elif current_state == RULES_SCREEN:
            if back_button.is_clicked(event):
                current_state = START_SCREEN

        elif current_state == COUNTDOWN:
            pass  # No event handling needed during countdown

    # Handle game states
    if current_state == START_SCREEN:
        draw_start_screen()

    elif current_state == COUNTDOWN:
        # Calculate elapsed time in seconds
        seconds_elapsed = (pygame.time.get_ticks() - countdown_start_ticks) // 1000
        seconds_left = countdown_duration - seconds_elapsed

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
        remaining_time = max(0, 5 - int(elapsed_time))  # Countdown from 5 seconds

        if round_active and remaining_time == 0:  # Timeout ends the game
            clock_sound.stop()
            fail_sound.play()
            game_active = False
            game_over = True
            current_state = GAME_OVER

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