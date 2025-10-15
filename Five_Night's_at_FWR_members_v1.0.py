import pygame
import math
import time
import random

pygame.init()

WIDTH, HEIGHT = (1000, 800)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Five Night's at FWR members")

BACKGROUND = pygame.transform.scale(pygame.image.load("bg.jpg"), (WIDTH, HEIGHT))
BACKGROUND_LEFT = pygame.transform.scale(pygame.image.load("bg_left.jpg"), (WIDTH, HEIGHT))
BACKGROUND_RIGHT = pygame.transform.scale(pygame.image.load("bg_right.jpg"), (WIDTH, HEIGHT))
BACKGROUND_BOTH = pygame.transform.scale(pygame.image.load("bg_both.jpg"), (WIDTH, HEIGHT))
BACKGROUND_END = pygame.transform.scale(pygame.image.load("bg_end.jpg"), (WIDTH, HEIGHT))

BG_KOKO = pygame.transform.scale(pygame.image.load("bg_koko.jpg"), (WIDTH, HEIGHT))
BG_NUKE = pygame.transform.scale(pygame.image.load("bg_nuke.png"), (WIDTH, HEIGHT))
BG_BRAINLESS = pygame.transform.scale(pygame.image.load("bg_brainless.png"), (WIDTH, HEIGHT))
BG_CRIS = pygame.transform.scale(pygame.image.load("bg_cris.jpg"), (WIDTH, HEIGHT))

PLAYER_IMAGE = pygame.transform.scale(pygame.image.load("player.png").convert_alpha(), (100, 100))
ENEMY_IMAGE_1 = pygame.transform.scale(pygame.image.load("Koko.png").convert_alpha(), (30, 30))
ENEMY_IMAGE_2 = pygame.transform.scale(pygame.image.load("Nuke.png").convert_alpha(), (30, 30))
ENEMY_IMAGE_3 = pygame.transform.scale(pygame.image.load("Brainless.png").convert_alpha(), (30, 30))
ENEMY_IMAGE_4 = pygame.transform.scale(pygame.image.load("Cris.png").convert_alpha(), (30, 30))

BATTERY_0 = pygame.transform.scale(pygame.image.load("battery_0.png").convert_alpha(), (150, 100))
BATTERY_1 = pygame.transform.scale(pygame.image.load("battery_1.png").convert_alpha(), (150, 100))
BATTERY_2 = pygame.transform.scale(pygame.image.load("battery_2.png").convert_alpha(), (150, 100))
BATTERY_3 = pygame.transform.scale(pygame.image.load("battery_3.png").convert_alpha(), (150, 100))
BATTERY_4 = pygame.transform.scale(pygame.image.load("battery_4.png").convert_alpha(), (150, 100))
BATTERY_IMAGES = [BATTERY_0, BATTERY_1, BATTERY_2, BATTERY_3, BATTERY_4]
BATTERY_FONT = pygame.font.Font("LcdSolid.ttf", 42)

LEFT_DOOR_POS = (390, 730)
RIGHT_DOOR_POS = (520, 730)
DOOR_RADIUS = 40

PLAYER_POS = (456, 730)

class Player(pygame.sprite.Sprite):
    def __init__(self, position, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)
        self.pos = (float(self.rect.x), float(self.rect.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, path_nodes, image, start_index=0, speed=120,
                 move_chance=1.0, initial_wait=True, pause_at_waypoints=True):
        super().__init__()
        self.name = name
        self.path = [tuple(p) for p in path_nodes]
        self.image = image
        self.index = start_index
        self.speed = speed
        self.move_chance = move_chance
        self.pause_at_waypoints = pause_at_waypoints
        self.active = True
        self.pos = [float(self.path[start_index][0]), float(self.path[start_index][1])]
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        self.target_index = start_index
        self.moving = False
        self.waiting = initial_wait
        self.last_wait_time = time.time()
        self.wait_interval = random.uniform(1.5, 4.0)

    def at_target(self):
        tx, ty = self.path[self.target_index]
        return math.hypot(tx - self.pos[0], ty - self.pos[1]) < 3.0

    def move_towards(self, target_pos, dt):
        tx, ty = target_pos
        dx, dy = tx - self.pos[0], ty - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        max_move = self.speed * dt
        if dist <= max_move:
            self.pos = [tx, ty]
        else:
            self.pos[0] += (dx / dist) * max_move
            self.pos[1] += (dy / dist) * max_move
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    def reset_path(self):
        self.index = 0
        self.target_index = 0
        self.pos = [float(self.path[0][0]), float(self.path[0][1])]
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))
        self.active = True
        self.moving = False
        self.waiting = True
        self.last_wait_time = time.time()
        self.wait_interval = random.uniform(1.5, 4.0)

    def update(self, dt):
        if not self.active:
            return

        now = time.time()
        if self.waiting:
            if now - self.last_wait_time >= self.wait_interval:
                if random.random() <= self.move_chance:
                    if self.index < len(self.path) - 1:
                        self.target_index = self.index + 1
                        self.moving = True
                        self.waiting = False
                    else:
                        self.active = False
                else:
                    self.last_wait_time = now
                    self.wait_interval = random.uniform(1.5, 4.0)
            return
        
        if self.moving:
            self.move_towards(self.path[self.target_index], dt)
            if self.at_target():
                self.index = self.target_index
                self.moving = False
                if self.index == len(self.path) - 1:
                    self.active = False
                    self.waiting = False
                    return
                if self.pause_at_waypoints:
                    self.waiting = True
                    self.last_wait_time = now
                    self.wait_interval = random.uniform(1.5, 4.0)
                else:
                    if self.index < len(self.path) - 1:
                        self.target_index = self.index + 1
                        self.moving = True
                    else:
                        self.active = False

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

NUKE_PATH = [
    (360, 50), (360, 131), (50, 131), (50, 220), (50, 131),
    (313, 131), (313, 500), (313, 595), (160, 595), (313, 595),
    (313, 730), PLAYER_POS
]

BRAINLESS_PATH = [
    (550, 50), (550, 131), (601, 131), (601, 208), (725, 208),
    (850, 208), (850, 400), (850, 208), (725, 208), (725, 530),
    (725, 208), (601, 208), (601, 500), (601, 730), PLAYER_POS
]

KOKO_PATH = [
    (455, 50), (455, 131), (750, 131), (750, 208), (850, 208),
    (850, 160), (850, 208), (725, 208), (725, 520), (890, 520),
    (725, 520), (725, 400), (601, 400), (601, 500), (601, 730), PLAYER_POS
]

CRIS_PATH = [
    (87, 350), (313, 350), (313, 730), PLAYER_POS
]

def main():
    player = Player(position=PLAYER_POS, image=PLAYER_IMAGE)

    enemies = [
        Enemy(name="Koko", path_nodes=KOKO_PATH, image=ENEMY_IMAGE_1, speed=140, move_chance=0.85),
        Enemy(name="Nuke", path_nodes=NUKE_PATH, image=ENEMY_IMAGE_2, speed=130, move_chance=0.9),
        Enemy(name="Brainless", path_nodes=BRAINLESS_PATH, image=ENEMY_IMAGE_3, speed=125, move_chance=0.9),
        Enemy(name="Cris", path_nodes=CRIS_PATH, image=ENEMY_IMAGE_4, speed=110, move_chance=1.0, pause_at_waypoints=False),
    ]

    left_door_closed = False
    right_door_closed = False
    current_background = BACKGROUND

    battery = 100.0
    last_time = time.time()
    night_start_time = time.time()
    night_duration = 8 * 60 + 30
    clock_font = pygame.font.Font("LcdSolid.ttf", 50)
    game_ended = False

    flash_active = False
    flash_start_time = 0
    flash_duration = 0.3
    new_background_pending = None
    got_jumpscared = False

    def update_background():
        nonlocal current_background
        if left_door_closed and right_door_closed:
            current_background = BACKGROUND_BOTH
        elif left_door_closed:
            current_background = BACKGROUND_LEFT
        elif right_door_closed:
            current_background = BACKGROUND_RIGHT
        else:
            current_background = BACKGROUND

    def get_battery_image():
        if battery >= 75:
            return BATTERY_IMAGES[4]
        elif battery >= 50:
            return BATTERY_IMAGES[3]
        elif battery >= 25:
            return BATTERY_IMAGES[2]
        elif battery > 0:
            return BATTERY_IMAGES[1]
        else:
            return BATTERY_IMAGES[0]

    clock = pygame.time.Clock()
    run = True

    while run:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and not game_ended and not got_jumpscared:
                if battery > 0:
                    if event.key == pygame.K_a:
                        left_door_closed = not left_door_closed
                        update_background()
                    elif event.key == pygame.K_d:
                        right_door_closed = not right_door_closed
                        update_background()

        now = time.time()
        elapsed = now - last_time
        last_time = now

        night_elapsed = now - night_start_time
        progress = night_elapsed / night_duration

        if progress >= 1.0 and not game_ended and not got_jumpscared:
            game_ended = True
            current_background = BACKGROUND_END

        if not game_ended and not got_jumpscared:
            doors_closed = int(left_door_closed) + int(right_door_closed)
            if doors_closed > 0 and battery > 0:
                battery -= (2 * doors_closed) * elapsed
                if battery <= 0:
                    battery = 0
                    left_door_closed = right_door_closed = False
                    update_background()

            for e in enemies:
                e.update(dt)

                ex, ey = e.pos
                if e.name in ("Nuke", "Cris") and left_door_closed and math.hypot(ex - LEFT_DOOR_POS[0], ey - LEFT_DOOR_POS[1]) < DOOR_RADIUS:
                    e.reset_path()
                elif e.name in ("Brainless", "Koko") and right_door_closed and math.hypot(ex - RIGHT_DOOR_POS[0], ey - RIGHT_DOOR_POS[1]) < DOOR_RADIUS:
                    e.reset_path()

                if not flash_active and math.hypot(ex - PLAYER_POS[0], ey - PLAYER_POS[1]) < 5:
                    flash_active = True
                    flash_start_time = now
                    if e.name == "Koko":
                        new_background_pending = BG_KOKO
                    elif e.name == "Nuke":
                        new_background_pending = BG_NUKE
                    elif e.name == "Brainless":
                        new_background_pending = BG_BRAINLESS
                    elif e.name == "Cris":
                        new_background_pending = BG_CRIS

        WINDOW.blit(current_background, (0, 0))

        if not got_jumpscared:
            if not game_ended:
                player.draw(WINDOW)
                for e in enemies:
                    e.draw(WINDOW)

                battery_img = get_battery_image()
                WINDOW.blit(battery_img, (670, HEIGHT - 110))
                text = BATTERY_FONT.render(f"{int(battery)}%", True, (255, 255, 255))
                WINDOW.blit(text, (840, HEIGHT - 80))

                hours_passed = int(progress * 6)
                display_hour = 12 + hours_passed
                if display_hour > 12:
                    display_hour -= 12
                clock_text = clock_font.render(f"{display_hour} AM", True, (255, 255, 255))
                WINDOW.blit(clock_text, (40, HEIGHT - 75))
            else:
                WINDOW.blit(current_background, (0, 0))

        if flash_active:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((255, 0, 0))
            overlay.set_alpha(150)
            WINDOW.blit(overlay, (0, 0))

            if now - flash_start_time >= flash_duration:
                flash_active = False
                got_jumpscared = True
                if new_background_pending:
                    current_background = new_background_pending
                    new_background_pending = None
                WINDOW.blit(current_background, (0, 0))

        pygame.display.update()

        if got_jumpscared and now - flash_start_time > 20:
            run = False
        elif game_ended and night_elapsed > night_duration + 30:
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()