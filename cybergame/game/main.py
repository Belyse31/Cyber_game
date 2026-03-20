import pygame
import random
import json
import os
import sys

# ================= INITIALIZATION =================
pygame.init()

# Fullscreen — get actual screen dimensions
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Airplane Shooter")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE  = (240, 240, 240)
BLACK  = (10, 10, 12)
RED    = (220, 40, 40)
YELLOW = (255, 220, 60)
CYAN   = (60, 220, 255)
GRAY   = (160, 160, 180)

font       = pygame.font.SysFont("consolas", 32, bold=True)
small_font = pygame.font.SysFont("consolas", 24)


def _disable_close_button():
    """Strip the X / system-menu button on Windows."""
    if os.name != "nt":
        return
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            GWL_STYLE  = -16
            WS_SYSMENU = 0x00080000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style & ~WS_SYSMENU)
    except Exception:
        pass


_disable_close_button()

# ================= HIGH SCORE HANDLING =================
HIGHSCORE_FILE = "highscore.json"


def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception:
            pass
    return 0


def save_high_score(score):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)


high_score = load_high_score()

# ================= CLASSES =================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, CYAN,           [(30, 0),  (0, 80),  (60, 80)])
        pygame.draw.polygon(self.image, (100, 220, 255), [(30, 5), (10, 70), (50, 70)])
        self.rect     = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.speed    = 6
        self.cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())
        if keys[pygame.K_SPACE] and self.cooldown <= 0:
            bullets.add(Bullet(self.rect.centerx, self.rect.top))
            self.cooldown = 5
        if self.cooldown > 0:
            self.cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 18))
        self.image.fill(YELLOW)
        pygame.draw.rect(self.image, WHITE, (1, 1, 4, 16))
        self.rect  = self.image.get_rect(center=(x, y))
        self.speed = -14

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
        pts = [(25, 0), (0, 60), (50, 60)]
        pygame.draw.polygon(self.image, RED,          pts)
        pygame.draw.polygon(self.image, (180, 30, 30), [(25, 8), (8, 52), (42, 52)])
        self.rect  = self.image.get_rect(center=(random.randint(40, WIDTH - 40), -40))
        self.speed = random.uniform(2.5, 4.2)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# ================= SPRITE GROUPS =================
all_sprites = pygame.sprite.Group()
bullets     = pygame.sprite.Group()
enemies     = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# ================= GAME VARIABLES =================
score          = 0
game_over      = False
spawn_timer    = 0
SPAWN_INTERVAL = 35

# Auto-restart countdown (ms)
RESTART_DELAY_MS  = 4000
restart_timer_ms  = 0

# ================= MAIN LOOP =================
running = True
while running:
    clock.tick(FPS)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        # Block window close — do nothing on QUIT
        if event.type == pygame.QUIT:
            pass

        if event.type == pygame.KEYDOWN:
            # Block ALL keys that could exit — no exit path exists
            # Only remove_game.bat can stop this process
            if event.key == pygame.K_ESCAPE:
                pass

    if not game_over:
        # ---------------- UPDATE ----------------
        all_sprites.update()
        bullets.update()
        enemies.update()

        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            score += 10

        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True
            restart_timer_ms = 0
            if score > high_score:
                high_score = score
                save_high_score(high_score)
    else:
        # Auto-restart countdown
        restart_timer_ms += clock.get_time()
        if restart_timer_ms >= RESTART_DELAY_MS:
            # Reset game
            score         = 0
            game_over     = False
            restart_timer_ms = 0
            enemies.empty()
            bullets.empty()
            player.rect.midbottom = (WIDTH // 2, HEIGHT - 20)
            spawn_timer = 0

    # ---------------- DRAW ----------------
    screen.fill(BLACK)

    # Subtle grid background
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (30, 30, 50), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (30, 30, 50), (0, y), (WIDTH, y), 1)

    all_sprites.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)

    # Always show current score + high score
    score_text = small_font.render(f"SCORE: {score}", True, WHITE)
    high_text  = small_font.render(f"HIGH: {high_score}", True, CYAN)
    screen.blit(score_text, (15, 12))
    screen.blit(high_text,  (15, 45))

    if game_over:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        # Game Over title
        go = font.render("GAME OVER", True, RED)
        screen.blit(go, go.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90)))

        # Final score
        final = small_font.render(f"Your Score: {score}", True, YELLOW)
        screen.blit(final, final.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        # High score
        if score == high_score and score > 0:
            hs_text = font.render(f"NEW HIGH SCORE: {high_score}", True, YELLOW)
        else:
            hs_text = small_font.render(f"High Score: {high_score}", True, CYAN)
        screen.blit(hs_text, hs_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        # Countdown to auto-restart
        secs_left = max(0, (RESTART_DELAY_MS - restart_timer_ms) // 1000 + 1)
        restart_hint = small_font.render(f"Restarting in {secs_left}...", True, GRAY)
        screen.blit(restart_hint, restart_hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

    pygame.display.flip()

# Final save on exit (only reachable if process is killed externally by remove_game.bat)
if score > high_score:
    save_high_score(score)
pygame.quit()
sys.exit()
