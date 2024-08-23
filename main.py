import pygame
import random
import os
import pickle
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Pac-Man
pacman_radius = 20
pacman_speed = 5
pacman_angle = 0

# Ghosts
ghost_radius = 20
ghosts = []
ghost_colors = [RED, (255, 192, 203), (0, 255, 255), (173, 216, 230)]  # Red, Pink, Cyan, LIGHT_BLUE 

# Dots
dot_radius = 5
dots = []

# Score current game
score = 0
font = pygame.font.Font(None, 36)

# Level
level = 1
initial_ghost_speed = 2
dots_per_level = 50

# The angle of Pac-Man's mouth opening
pacman_mouth_angle = 45  
pacman_mouth_direction = 1

# High score management
high_score_file = 'highscore.pkl'

def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, 'rb') as f:
            return pickle.load(f)
    return {'name': 'None', 'score': 0}

def save_high_score(name, score):
    with open(high_score_file, 'wb') as f:
        pickle.dump({'name': name, 'score': score}, f)

high_score = load_high_score()

def prompt_for_name():
    name = ""
    input_box = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        
        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - 70, HEIGHT // 2 - 40))
        
        pygame.display.flip()
        clock.tick(30)

def reset_level():
    global dots, ghosts, level
    print(f"Resetting level: {level}")  # Debug statement

    # Define the area where text is drawn
    text_area_height = 100
    min_y = text_area_height + dot_radius

    # Avoid placing dots in the area reserved for text
    dots = [{'x': random.randint(dot_radius, WIDTH - dot_radius),
             'y': random.randint(min_y, HEIGHT - dot_radius)}
            for _ in range(max(dots_per_level - (level - 1) * 5, 10))]

    ghost_speed = initial_ghost_speed + level - 1
    ghosts.clear()
    for i in range(4):
        ghost = {
            'x': random.randint(ghost_radius, WIDTH - ghost_radius),
            'y': random.randint(ghost_radius + text_area_height, HEIGHT - ghost_radius),
            'dx': random.choice([-1, 1]) * ghost_speed,
            'dy': random.choice([-1, 1]) * ghost_speed,
            'color': ghost_colors[i]
        }
        ghosts.append(ghost)

    print(f"Level {level} started with {len(dots)} dots and {len(ghosts)} ghosts.")  # Debug statement

def restart_game():
    global pacman_x, pacman_y, pacman_speed, ghosts, dots, score, level
    pacman_x = WIDTH // 2
    pacman_y = HEIGHT // 2
    pacman_speed = 5
    ghosts.clear()
    dots.clear()
    score = 0
    level = 1
    reset_level()

def draw_pacman(x, y, angle, mouth_angle):
    # Draw the basic circle for Pac-Man
    pygame.draw.circle(screen, ORANGE, (int(x), int(y)), pacman_radius)

    # Calculate mouth points
    mouth_left = (x, y)
    mouth_right = (x + pacman_radius * math.cos(math.radians(angle)),
                   y - pacman_radius * math.sin(math.radians(angle)))
    
    top_angle = angle - mouth_angle
    bottom_angle = angle + mouth_angle
    
    mouth_top = (x + pacman_radius * math.cos(math.radians(top_angle)),
                 y - pacman_radius * math.sin(math.radians(top_angle)))
    mouth_bottom = (x + pacman_radius * math.cos(math.radians(bottom_angle)),
                    y - pacman_radius * math.sin(math.radians(bottom_angle)))

    # Draw the mouth (or rather, erase part of the circle)
    pygame.draw.polygon(screen, BLACK, [mouth_left, mouth_top, mouth_right, mouth_bottom])

def draw_ghost(x, y, color):
    # Draw the main body
    pygame.draw.circle(screen, color, (int(x), int(y) - ghost_radius // 2), ghost_radius)
    body_rect = pygame.Rect(x - ghost_radius, y - ghost_radius // 2, ghost_radius * 2, ghost_radius)
    pygame.draw.rect(screen, color, body_rect)
    
    # Draw wavy bottom
    wave_height = ghost_radius // 4
    wave_width = ghost_radius // 2
    num_waves = 4
    points = []
    for i in range(num_waves * 2 + 1):
        wave_x = x - ghost_radius + (i * wave_width // 2)
        wave_y = y + ghost_radius // 2
        if i % 2 == 0:
            wave_y += wave_height
        points.append((wave_x, wave_y))
    
    pygame.draw.lines(screen, color, False, points, 1)
    pygame.draw.polygon(screen, color, [points[0]] + points + [points[-1], (x + ghost_radius, y - ghost_radius // 2), (x - ghost_radius, y - ghost_radius // 2)])
    
    # Draw eyes
    eye_radius = ghost_radius // 4
    left_eye_pos = (int(x - ghost_radius // 2), int(y - ghost_radius // 2))
    right_eye_pos = (int(x + ghost_radius // 2), int(y - ghost_radius // 2))
    pygame.draw.circle(screen, WHITE, left_eye_pos, eye_radius)
    pygame.draw.circle(screen, WHITE, right_eye_pos, eye_radius)
    
    # Draw pupils
    pupil_radius = eye_radius // 2
    pygame.draw.circle(screen, BLUE, left_eye_pos, pupil_radius)
    pygame.draw.circle(screen, BLUE, right_eye_pos, pupil_radius)
def main_game():
    global pacman_x, pacman_y, ghosts, dots, score, level, high_score, pacman_angle, pacman_mouth_angle, pacman_mouth_direction
    restart_game()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move Pac-Man
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pacman_x -= pacman_speed
            pacman_angle = 180
        if keys[pygame.K_RIGHT]:
            pacman_x += pacman_speed
            pacman_angle = 0
        if keys[pygame.K_UP]:
            pacman_y -= pacman_speed
            pacman_angle = 90
        if keys[pygame.K_DOWN]:
            pacman_y += pacman_speed
            pacman_angle = 270

        # Keep Pac-Man on screen
        pacman_x = max(pacman_radius, min(pacman_x, WIDTH - pacman_radius))
        pacman_y = max(pacman_radius, min(pacman_y, HEIGHT - pacman_radius))

        # Animate Pac-Man's mouth
        pacman_mouth_angle += pacman_mouth_direction * 3
        if pacman_mouth_angle >= 45:
            pacman_mouth_angle = 45
            pacman_mouth_direction = -1
        elif pacman_mouth_angle <= 0:
            pacman_mouth_angle = 0
            pacman_mouth_direction = 1

        # Move ghosts
        for ghost in ghosts:
            ghost['x'] += ghost['dx']
            ghost['y'] += ghost['dy']

            # Bounce off walls
            if ghost['x'] <= ghost_radius or ghost['x'] >= WIDTH - ghost_radius:
                ghost['dx'] *= -1
            if ghost['y'] <= ghost_radius or ghost['y'] >= HEIGHT - ghost_radius:
                ghost['dy'] *= -1

        # Check for dot collection
        for dot in dots[:]:
            if ((dot['x'] - pacman_x) ** 2 + (dot['y'] - pacman_y) ** 2) ** 0.5 < pacman_radius + dot_radius:
                dots.remove(dot)
                score += 10

        # Check for ghost collision
        for ghost in ghosts:
            if ((ghost['x'] - pacman_x) ** 2 + (ghost['y'] - pacman_y) ** 2) ** 0.5 < pacman_radius + ghost_radius:
                if score > high_score['score']:
                    name = prompt_for_name()
                    save_high_score(name, score)
                    high_score = load_high_score()
                restart_game()
                break  # Exit the ghost loop after restarting

        # Check if all dots are collected to advance to the next level
        if not dots:
            level += 1
            reset_level()

        # Draw everything
        screen.fill(BLACK)

        # Draw Pac-Man
        draw_pacman(pacman_x, pacman_y, pacman_angle, pacman_mouth_angle)

        # Draw ghosts
        for ghost in ghosts:
            draw_ghost(ghost['x'], ghost['y'], ghost['color'])

        # Draw dots
        for dot in dots:
            pygame.draw.circle(screen, WHITE, (int(dot['x']), int(dot['y'])), dot_radius)

        # Draw score and level
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score['score']} by {high_score['name']}", True, GREEN)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(high_score_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main_game()