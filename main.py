import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60
PLAYER_SPEED = 2.5
BULLET_SPEED = 10
TANK_WIDTH, TANK_HEIGHT = 60, 40
TURRET_WIDTH, TURRET_HEIGHT = 15, 25
BARREL_LENGTH = 30

BACKGROUND = (60, 100, 60)
RED = (180, 50, 50)
DARK_RED = (120, 30, 30)
BLUE = (50, 80, 180)
DARK_BLUE = (30, 50, 120)
GREEN = (90, 140, 90)
DARK_GREEN = (50, 100, 50)
OLIVE_GREEN = (85, 107, 47)
YELLOW = (255, 255, 0)
BLACK = (30, 30, 30)
DARK_GRAY = (60, 60, 60)
GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (119, 49, 0)
SAND = (210, 180, 140)
METAL = (150, 150, 160)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (180, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Танчики")
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 48, bold=True)


class Tank:
    def __init__(self, x, y, color, dark_color, controls, player_num):
        self.x = x
        self.y = y
        self.color = color
        self.dark_color = dark_color
        self.controls = controls
        self.player_num = player_num
        self.angle = 0 if player_num == 1 else 180
        self.turret_angle = 0 if player_num == 1 else 180
        self.health = 100
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 40
        self.speed = PLAYER_SPEED
        self.alive = True
        self.hit_timer = 0
        self.tracks_offset = 0
        self.has_taken_damage = False
        self.speed_buff_active = False
        self.speed_buff_timer = 0

    def move(self, keys, obstacles):
        old_x, old_y = self.x, self.y

        moved = False
        if keys[self.controls['up']]:
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y -= math.sin(math.radians(self.angle)) * self.speed
            moved = True
        if keys[self.controls['down']]:
            self.x -= math.cos(math.radians(self.angle)) * self.speed
            self.y += math.sin(math.radians(self.angle)) * self.speed
            moved = True

        if moved:
            self.tracks_offset = (self.tracks_offset + 5) % 20

        if keys[self.controls['left']]:
            self.angle += 2.5
        if keys[self.controls['right']]:
            self.angle -= 2.5

        if keys[self.controls['turret_left']]:
            self.turret_angle += 2.5
        if keys[self.controls['turret_right']]:
            self.turret_angle -= 2.5

        self.angle %= 360
        self.turret_angle %= 360

        self.x = max(TANK_WIDTH // 2 + 30, min(WIDTH - TANK_WIDTH // 2 - 30, self.x))
        self.y = max(TANK_HEIGHT // 2 + 30, min(HEIGHT - TANK_HEIGHT // 2 - 30, self.y))

        tank_rect = self.get_rect()
        for obstacle in obstacles:
            if tank_rect.colliderect(obstacle.rect):
                self.x, self.y = old_x, old_y
                break

    def shoot(self):
        if self.shoot_cooldown <= 0:
            barrel_end_x = self.x + math.cos(math.radians(self.turret_angle)) * (BARREL_LENGTH + TURRET_HEIGHT / 2)
            barrel_end_y = self.y - math.sin(math.radians(self.turret_angle)) * (BARREL_LENGTH + TURRET_HEIGHT / 2)

            self.bullets.append(Bullet(barrel_end_x, barrel_end_y, self.turret_angle, self.player_num))
            self.shoot_cooldown = self.shoot_cooldown_max

    def update(self, obstacles, other_tank, game_state):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.hit_timer > 0:
            self.hit_timer -= 1

        if self.speed_buff_active:
            self.speed_buff_timer -= 1
            if self.speed_buff_timer <= 0:
                self.speed = PLAYER_SPEED
                self.speed_buff_active = False

        for bullet in self.bullets[:]:
            bullet.update()

            if (bullet.x < 0 or bullet.x > WIDTH or
                    bullet.y < 0 or bullet.y > HEIGHT):
                self.bullets.remove(bullet)
                continue

            bullet_hit_obstacle = False
            for obstacle in obstacles:
                if bullet.rect.colliderect(obstacle.rect):
                    self.bullets.remove(bullet)
                    bullet_hit_obstacle = True
                    obstacle.create_explosion_effect(bullet.x, bullet.y)
                    break

            if bullet_hit_obstacle:
                continue

            if bullet.rect.colliderect(other_tank.get_rect()):
                other_tank.take_damage(25)
                self.bullets.remove(bullet)

                if not game_state['damage_taken']:
                    game_state['damage_taken'] = True

    def take_damage(self, damage):
        self.health -= damage
        self.hit_timer = 15
        self.has_taken_damage = True

        if self.health <= 0:
            self.health = 0
            self.alive = False

    def apply_speed_buff(self):
        self.speed = PLAYER_SPEED * 1.8
        self.speed_buff_active = True
        self.speed_buff_timer = 600

    def apply_health_buff(self):
        self.health = min(100, self.health + 40)

    def get_rect(self):
        return pygame.Rect(self.x - TANK_WIDTH // 2, self.y - TANK_HEIGHT // 2, TANK_WIDTH, TANK_HEIGHT)

    def draw(self, screen):
        if not self.alive:
            return

        tank_surface = pygame.Surface((TANK_WIDTH + 20, TANK_HEIGHT + 20), pygame.SRCALPHA)

        if self.hit_timer > 0 and self.hit_timer % 5 < 3:
            draw_color = LIGHT_GRAY
            draw_dark_color = GRAY
        else:
            draw_color = self.color
            draw_dark_color = self.dark_color

        pygame.draw.rect(tank_surface, draw_color,
                         (10, 10, TANK_WIDTH, TANK_HEIGHT), border_radius=5)

        pygame.draw.rect(tank_surface, draw_dark_color,
                         (15, 5, TANK_WIDTH - 10, TANK_HEIGHT - 15), border_radius=3)

        pygame.draw.circle(tank_surface, METAL, (TANK_WIDTH // 2 + 10, TANK_HEIGHT // 2 + 5), 8)
        pygame.draw.circle(tank_surface, DARK_GRAY, (TANK_WIDTH // 2 + 10, TANK_HEIGHT // 2 + 5), 8, 2)

        pygame.draw.rect(tank_surface, BROWN, (25, 15, 15, 10), border_radius=2)
        pygame.draw.rect(tank_surface, BROWN, (TANK_WIDTH - 5, 15, 15, 10), border_radius=2)

        for i in range(0, TANK_WIDTH + 20, 20):
            pygame.draw.rect(tank_surface, BLACK,
                             (i - self.tracks_offset, 0, 15, 8), border_radius=2)
            pygame.draw.rect(tank_surface, BLACK,
                             (i - self.tracks_offset, TANK_HEIGHT + 12, 15, 8), border_radius=2)

        pygame.draw.rect(tank_surface, DARK_GRAY, (0, 8, 8, TANK_HEIGHT + 4), border_radius=2)
        pygame.draw.rect(tank_surface, DARK_GRAY, (TANK_WIDTH + 12, 8, 8, TANK_HEIGHT + 4), border_radius=2)

        for i in range(3):
            y_pos = 15 + i * 10
            pygame.draw.circle(tank_surface, METAL, (8, y_pos), 6)
            pygame.draw.circle(tank_surface, METAL, (TANK_WIDTH + 12, y_pos), 6)

        rotated_tank = pygame.transform.rotate(tank_surface, self.angle)
        tank_rect = rotated_tank.get_rect(center=(self.x, self.y))
        screen.blit(rotated_tank, tank_rect)

        self.draw_turret(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

    def draw_turret(self, screen):
        turret_surface = pygame.Surface((TURRET_WIDTH + BARREL_LENGTH, TURRET_HEIGHT * 2), pygame.SRCALPHA)

        if self.hit_timer > 0 and self.hit_timer % 5 < 3:
            draw_dark_color = GRAY
        else:
            draw_dark_color = self.dark_color

        turret_center_x = BARREL_LENGTH // 2
        turret_center_y = TURRET_HEIGHT

        pygame.draw.circle(turret_surface, draw_dark_color,
                           (turret_center_x, turret_center_y), TURRET_HEIGHT)

        pygame.draw.circle(turret_surface, METAL,
                           (turret_center_x, turret_center_y), TURRET_HEIGHT - 5)

        pygame.draw.circle(turret_surface, BLACK,
                           (turret_center_x, turret_center_y - 5), 6)

        pygame.draw.rect(turret_surface, DARK_GRAY,
                         (turret_center_x - 8, turret_center_y + 5, 16, 4), border_radius=1)

        barrel_end_x = BARREL_LENGTH + TURRET_WIDTH
        barrel_mid_y = TURRET_HEIGHT

        pygame.draw.rect(turret_surface, DARK_GRAY,
                         (TURRET_HEIGHT - 5, barrel_mid_y - 3, BARREL_LENGTH + 10, 6), border_radius=2)

        pygame.draw.rect(turret_surface, METAL,
                         (TURRET_HEIGHT, barrel_mid_y - 2, BARREL_LENGTH, 4), border_radius=1)

        pygame.draw.rect(turret_surface, BLACK,
                         (barrel_end_x - 3, barrel_mid_y - 3, 3, 6))

        rotated_turret = pygame.transform.rotate(turret_surface, self.turret_angle)
        turret_rect = rotated_turret.get_rect(center=(self.x, self.y))
        screen.blit(rotated_turret, turret_rect)


class Bullet:
    def __init__(self, x, y, angle, player_num):
        self.x = x
        self.y = y
        self.angle = angle
        self.player_num = player_num
        self.radius = 6
        self.color = ORANGE if player_num == 1 else YELLOW
        self.trail = []
        self.trail_length = 5
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        self.x += math.cos(math.radians(self.angle)) * BULLET_SPEED
        self.y -= math.sin(math.radians(self.angle)) * BULLET_SPEED

        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 255 * (i / len(self.trail))
            radius = self.radius * (i / len(self.trail))
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, int(alpha)),
                               (radius, radius), radius)
            screen.blit(trail_surface, (trail_x - radius, trail_y - radius))

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        highlight_x = self.x + math.cos(math.radians(self.angle + 45)) * (self.radius * 0.7)
        highlight_y = self.y - math.sin(math.radians(self.angle + 45)) * (self.radius * 0.7)
        pygame.draw.circle(screen, LIGHT_GRAY, (int(highlight_x), int(highlight_y)), self.radius // 3)

        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)


class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BROWN
        self.explosion_effects = []

    def create_explosion_effect(self, x, y):
        self.explosion_effects.append({
            'x': x,
            'y': y,
            'radius': 5,
            'max_radius': 25,
            'alpha': 255,
            'color': ORANGE
        })

    def update(self):
        for effect in self.explosion_effects[:]:
            effect['radius'] += 1
            effect['alpha'] -= 15

            if effect['alpha'] <= 0 or effect['radius'] >= effect['max_radius']:
                self.explosion_effects.remove(effect)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        block_size = 20
        for i in range(0, self.rect.width, block_size):
            for j in range(0, self.rect.height, block_size):
                block_rect = pygame.Rect(
                    self.rect.x + i + 1,
                    self.rect.y + j + 1,
                    block_size - 2,
                    block_size - 2
                )
                pygame.draw.rect(screen, SAND, block_rect)
                pygame.draw.rect(screen, DARK_BROWN, block_rect, 2)

        for effect in self.explosion_effects:
            if effect['alpha'] > 0:
                explosion_surface = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    explosion_surface,
                    (*effect['color'], effect['alpha']),
                    (effect['radius'], effect['radius']),
                    effect['radius']
                )
                screen.blit(
                    explosion_surface,
                    (effect['x'] - effect['radius'], effect['y'] - effect['radius'])
                )


class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.radius = 20
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                self.radius * 2, self.radius * 2)
        self.active = True
        self.collected = False
        self.timer = 0
        self.blink_timer = 0
        self.rotation = 0

    def update(self):
        if self.collected:
            self.active = False
            return

        self.timer += 1
        self.blink_timer += 1
        self.rotation = (self.rotation + 2) % 360

        if self.timer > 450:
            self.active = False
        elif self.timer > 400:
            if self.blink_timer % 10 < 5:
                self.active = False
            else:
                self.active = True

    def collect(self):
        self.collected = True
        self.active = False

    def draw(self, screen):
        if not self.active:
            return

        bonus_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        if self.type == 'speed':
            color = PURPLE
            light_color = LIGHT_PURPLE

            pygame.draw.circle(bonus_surface, color, (self.radius, self.radius), self.radius - 4)

            pygame.draw.circle(bonus_surface, light_color, (self.radius, self.radius), self.radius - 8)

            points = [
                (self.radius, self.radius - 12),
                (self.radius + 8, self.radius - 4),
                (self.radius - 3, self.radius),
                (self.radius + 3, self.radius + 12),
                (self.radius - 8, self.radius + 4),
                (self.radius + 3, self.radius)
            ]
            pygame.draw.polygon(bonus_surface, YELLOW, points)

            pygame.draw.circle(bonus_surface, WHITE, (self.radius, self.radius), self.radius - 4, 3)

        elif self.type == 'health':
            color = DARK_GREEN
            light_color = GREEN

            pygame.draw.circle(bonus_surface, color, (self.radius, self.radius), self.radius - 4)

            pygame.draw.circle(bonus_surface, light_color, (self.radius, self.radius), self.radius - 8)

            cross_width = 4
            cross_length = 12

            pygame.draw.rect(bonus_surface, WHITE,
                             (self.radius - cross_length // 2, self.radius - cross_width // 2,
                              cross_length, cross_width))
            pygame.draw.rect(bonus_surface, WHITE,
                             (self.radius - cross_width // 2, self.radius - cross_length // 2,
                              cross_width, cross_length))

            pygame.draw.circle(bonus_surface, WHITE, (self.radius, self.radius), self.radius - 4, 3)

        rotated_bonus = pygame.transform.rotate(bonus_surface, self.rotation)
        bonus_rect = rotated_bonus.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bonus, bonus_rect)


def create_obstacles():
    obstacles = []

    obstacle_positions = [
        (WIDTH // 2 - 75, HEIGHT // 2 - 75, 150, 150),
        (50, 50, 80, 80),
        (WIDTH - 130, 50, 80, 80),
        (50, HEIGHT - 130, 80, 80),
        (WIDTH - 130, HEIGHT - 130, 80, 80),
        (WIDTH // 4, 100, 60, 100),
        (3 * WIDTH // 4 - 60, 100, 60, 100),
        (WIDTH // 4, HEIGHT - 200, 60, 100),
        (3 * WIDTH // 4 - 60, HEIGHT - 200, 60, 100),
    ]

    for x, y, width, height in obstacle_positions:
        obstacles.append(Obstacle(x, y, width, height))

    obstacles.append(Obstacle(0, 0, WIDTH, 30))
    obstacles.append(Obstacle(0, HEIGHT - 30, WIDTH, 30))
    obstacles.append(Obstacle(0, 0, 30, HEIGHT))
    obstacles.append(Obstacle(WIDTH - 30, 0, 30, HEIGHT))

    return obstacles


def create_speed_powerup(obstacles):
    max_attempts = 50
    for _ in range(max_attempts):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        powerup_rect = pygame.Rect(x - 20, y - 20, 40, 40)

        collision = False
        for obstacle in obstacles:
            if powerup_rect.colliderect(obstacle.rect):
                collision = True
                break

        if not collision:
            return PowerUp(x, y, 'speed')

    return PowerUp(WIDTH // 2, HEIGHT // 2, 'speed')


def create_health_powerup(obstacles):
    max_attempts = 50
    for _ in range(max_attempts):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        powerup_rect = pygame.Rect(x - 20, y - 20, 40, 40)

        collision = False
        for obstacle in obstacles:
            if powerup_rect.colliderect(obstacle.rect):
                collision = True
                break

        if not collision:
            return PowerUp(x, y, 'health')

    return PowerUp(WIDTH // 2, HEIGHT // 2, 'health')


def draw_health_bar(screen, x, y, health, max_health, color, dark_color):
    pygame.draw.rect(screen, BLACK, (x - 55, y - 45, 114, 19), border_radius=4)

    health_width = 110 * health / max_health
    pygame.draw.rect(screen, dark_color, (x - 53, y - 43, 110, 15), border_radius=3)
    pygame.draw.rect(screen, color, (x - 53, y - 43, health_width, 15), border_radius=3)

    pygame.draw.rect(screen, WHITE, (x - 53, y - 43, 110, 15), 2, border_radius=3)

    health_text = font.render(f"{health}%", True, WHITE)
    screen.blit(health_text, (x - health_text.get_width() // 2, y - 65))


def draw_controls_info(screen):
    controls1 = [
        "Игрок 1 (Красный танк):",
        "W/S - движение вперед/назад",
        "A/D - поворот корпуса",
        "Q/E - поворот башни",
        "ПРОБЕЛ - огонь"
    ]

    controls2 = [
        "Игрок 2 (Синий танк):",
        "↑/↓ - движение вперед/назад",
        "←/→ - поворот корпуса",
        "L/J - поворот башни",
        "ПРАВЫЙ CTRL - огонь"
    ]

    pygame.draw.rect(screen, (0, 0, 0, 180), (15, 15, 240, 145), border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0, 180), (WIDTH - 255, 15, 240, 145), border_radius=8)

    for i, line in enumerate(controls1):
        color = RED if i == 0 else WHITE
        text = font.render(line, True, color)
        screen.blit(text, (25, 25 + i * 28))

    for i, line in enumerate(controls2):
        color = BLUE if i == 0 else WHITE
        text = font.render(line, True, color)
        screen.blit(text, (WIDTH - 245, 25 + i * 28))


def draw_background(screen):
    screen.fill(BACKGROUND)

    for i in range(0, WIDTH, 80):
        pygame.draw.line(screen, (BACKGROUND[0] + 10, BACKGROUND[1] + 10, BACKGROUND[2] + 10),
                         (i, 0), (i, HEIGHT), 1)
    for j in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (BACKGROUND[0] + 10, BACKGROUND[1] + 10, BACKGROUND[2] + 10),
                         (0, j), (WIDTH, j), 1)


def is_valid_position(x, y, obstacles, tank_rect=None):
    test_rect = tank_rect if tank_rect else pygame.Rect(x - 30, y - 30, 60, 60)

    for obstacle in obstacles:
        if test_rect.colliderect(obstacle.rect):
            return False
    return True


def main():
    obstacles = create_obstacles()

    tank1_pos = (150, HEIGHT // 2)
    tank2_pos = (WIDTH - 150, HEIGHT // 2)

    tank1_rect = pygame.Rect(tank1_pos[0] - TANK_WIDTH // 2, tank1_pos[1] - TANK_HEIGHT // 2,
                             TANK_WIDTH, TANK_HEIGHT)
    tank2_rect = pygame.Rect(tank2_pos[0] - TANK_WIDTH // 2, tank2_pos[1] - TANK_HEIGHT // 2,
                             TANK_WIDTH, TANK_HEIGHT)

    if not is_valid_position(tank1_pos[0], tank1_pos[1], obstacles, tank1_rect):
        for x in range(100, 300, 20):
            for y in range(100, HEIGHT - 100, 20):
                test_rect = pygame.Rect(x - TANK_WIDTH // 2, y - TANK_HEIGHT // 2, TANK_WIDTH, TANK_HEIGHT)
                if is_valid_position(x, y, obstacles, test_rect):
                    tank1_pos = (x, y)
                    break

    if not is_valid_position(tank2_pos[0], tank2_pos[1], obstacles, tank2_rect):
        for x in range(WIDTH - 100, WIDTH - 300, -20):
            for y in range(100, HEIGHT - 100, 20):
                test_rect = pygame.Rect(x - TANK_WIDTH // 2, y - TANK_HEIGHT // 2, TANK_WIDTH, TANK_HEIGHT)
                if is_valid_position(x, y, obstacles, test_rect):
                    tank2_pos = (x, y)
                    break

    player1_controls = {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'turret_left': pygame.K_q,
        'turret_right': pygame.K_e,
        'shoot': pygame.K_SPACE
    }

    player2_controls = {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'turret_left': pygame.K_j,
        'turret_right': pygame.K_l,
        'shoot': pygame.K_RCTRL
    }

    player1 = Tank(tank1_pos[0], tank1_pos[1], RED, DARK_RED, player1_controls, 1)
    player2 = Tank(tank2_pos[0], tank2_pos[1], BLUE, DARK_BLUE, player2_controls, 2)

    game_state = {
        'damage_taken': False,
        'speed_powerup': None,
        'health_powerup': None,
        'health_powerup_spawned': False
    }

    game_state['speed_powerup'] = create_speed_powerup(obstacles)

    running = True
    game_over = False
    winner = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    obstacles = create_obstacles()

                    tank1_pos = (150, HEIGHT // 2)
                    tank2_pos = (WIDTH - 150, HEIGHT // 2)

                    tank1_rect = pygame.Rect(tank1_pos[0] - TANK_WIDTH // 2, tank1_pos[1] - TANK_HEIGHT // 2,
                                             TANK_WIDTH, TANK_HEIGHT)
                    tank2_rect = pygame.Rect(tank2_pos[0] - TANK_WIDTH // 2, tank2_pos[1] - TANK_HEIGHT // 2,
                                             TANK_WIDTH, TANK_HEIGHT)

                    if not is_valid_position(tank1_pos[0], tank1_pos[1], obstacles, tank1_rect):
                        for x in range(100, 300, 20):
                            for y in range(100, HEIGHT - 100, 20):
                                test_rect = pygame.Rect(x - TANK_WIDTH // 2, y - TANK_HEIGHT // 2, TANK_WIDTH,
                                                        TANK_HEIGHT)
                                if is_valid_position(x, y, obstacles, test_rect):
                                    tank1_pos = (x, y)
                                    break

                    if not is_valid_position(tank2_pos[0], tank2_pos[1], obstacles, tank2_rect):
                        for x in range(WIDTH - 100, WIDTH - 300, -20):
                            for y in range(100, HEIGHT - 100, 20):
                                test_rect = pygame.Rect(x - TANK_WIDTH // 2, y - TANK_HEIGHT // 2, TANK_WIDTH,
                                                        TANK_HEIGHT)
                                if is_valid_position(x, y, obstacles, test_rect):
                                    tank2_pos = (x, y)
                                    break

                    player1 = Tank(tank1_pos[0], tank1_pos[1], RED, DARK_RED, player1_controls, 1)
                    player2 = Tank(tank2_pos[0], tank2_pos[1], BLUE, DARK_BLUE, player2_controls, 2)
                    game_state = {
                        'damage_taken': False,
                        'speed_powerup': create_speed_powerup(obstacles),
                        'health_powerup': None,
                        'health_powerup_spawned': False
                    }
                    game_over = False
                    winner = None

        keys = pygame.key.get_pressed()

        if not game_over:
            player1.move(keys, obstacles)
            player2.move(keys, obstacles)

            if keys[player1.controls['shoot']]:
                player1.shoot()
            if keys[player2.controls['shoot']]:
                player2.shoot()

            player1.update(obstacles, player2, game_state)
            player2.update(obstacles, player1, game_state)

            for obstacle in obstacles:
                obstacle.update()

            if game_state['speed_powerup']:
                game_state['speed_powerup'].update()

                if game_state['speed_powerup'].active:
                    if game_state['speed_powerup'].rect.colliderect(player1.get_rect()):
                        player1.apply_speed_buff()
                        game_state['speed_powerup'].collect()
                    elif game_state['speed_powerup'].rect.colliderect(player2.get_rect()):
                        player2.apply_speed_buff()
                        game_state['speed_powerup'].collect()

            if game_state['damage_taken'] and not game_state['health_powerup_spawned']:
                game_state['health_powerup'] = create_health_powerup(obstacles)
                game_state['health_powerup_spawned'] = True

            if game_state['health_powerup']:
                game_state['health_powerup'].update()

                if game_state['health_powerup'].active:
                    if game_state['health_powerup'].rect.colliderect(player1.get_rect()):
                        player1.apply_health_buff()
                        game_state['health_powerup'].collect()
                    elif game_state['health_powerup'].rect.colliderect(player2.get_rect()):
                        player2.apply_health_buff()
                        game_state['health_powerup'].collect()

            if not player1.alive:
                game_over = True
                winner = 2
            elif not player2.alive:
                game_over = True
                winner = 1

        draw_background(screen)

        for obstacle in obstacles:
            obstacle.draw(screen)

        if game_state['speed_powerup'] and game_state['speed_powerup'].active:
            game_state['speed_powerup'].draw(screen)

        if game_state['health_powerup'] and game_state['health_powerup'].active:
            game_state['health_powerup'].draw(screen)

        player1.draw(screen)
        player2.draw(screen)

        if player1.alive:
            draw_health_bar(screen, player1.x, player1.y - 60, player1.health, 100, RED, DARK_RED)
        if player2.alive:
            draw_health_bar(screen, player2.x, player2.y - 60, player2.health, 100, BLUE, DARK_BLUE)

        draw_controls_info(screen)

        speed1_indicator = "⚡" if player1.speed_buff_active else ""
        speed2_indicator = "⚡" if player2.speed_buff_active else ""

        speed1_text = font.render(f"Скорость: {player1.speed:.1f} {speed1_indicator}", True, WHITE)
        speed2_text = font.render(f"Скорость: {player2.speed:.1f} {speed2_indicator}", True, WHITE)

        screen.blit(speed1_text, (20, HEIGHT - 50))
        screen.blit(speed2_text, (WIDTH - speed2_text.get_width() - 20, HEIGHT - 50))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            if winner == 1:
                winner_text = big_font.render("КРАСНЫЙ ТАНК ПОБЕДИЛ!", True, RED)
                sub_text = font.render("Игрок 1 уничтожил противника", True, WHITE)
            else:
                winner_text = big_font.render("СИНИЙ ТАНК ПОБЕДИЛ!", True, BLUE)
                sub_text = font.render("Игрок 2 уничтожил противника", True, WHITE)

            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 70))
            screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 10))

            restart_text = font.render("Нажмите R для новой битвы или ESC для выхода", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()