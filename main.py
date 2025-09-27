# main.py — Clean visuals + ANT SPRITE (pygbag-safe)
# Place your sprite at: assets/ant.png  (or ./ant.png)
# Controls: Click set/clear target | Space pause | F FOV | B rings | +/- boids | O add obj | R reset | ? help

try:
    import asyncio
except Exception:
    import pygbag.aio as asyncio

import random, math, os
import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Boids
NUM_BOIDS = 50
MAX_SPEED = 4.2
MAX_FORCE = 0.10
NEIGHBOR_RADIUS = 90
SEPARATION_RADIUS = 26
TARGET_ATTRACTION = 0.06

# Objects
NUM_OBJECTS = 6
OBJECT_RADIUS = 12
OBJECT_PUSH_FORCE = 0.26
OBJECT_SEPARATION_RADIUS = 60
OBJECT_FRICTION = 0.965
OBJECT_MAX_SPEED = 2.4
ATTRACTION_RADIUS = 140

# Goal
GOAL_POS = (int(WIDTH * 0.82), int(HEIGHT * 0.25))
GOAL_RADIUS = 90
TARGET_HOLD_TIME_MS = 3000
objects_all_in_goal_since = None
OBJECTS_IN_GOAL = False

# Toggles/state
PAUSED = False
DRAW_FOV = False
DRAW_BROADCAST = False
SHOW_HELP = True
BROADCAST_RADIUS = 110

# Colors
BG_COLOR = (68, 72, 80)
TRI_COLOR = (248, 248, 255)      # fallback triangle color
FOV_COLOR = (135, 150, 170)
OBJECT_COLOR = (70, 165, 255)
OBJECT_IN_GOAL_COLOR = (90, 230, 150)
GOAL_COLOR = (160, 230, 200)
GOAL_RING = (60, 140, 110)
HUD_BG = (240, 245, 255)
HUD_TEXT = (28, 32, 40)

# Sprite tuning
ANT_SCALE = 0.05        # scale factor relative to source image
ANGLE_STEP = 5          # degrees between cached rotations

# ---------- Helpers ----------
def clamp_mag(vec: pygame.math.Vector2, max_mag: float) -> pygame.math.Vector2:
    m = vec.length()
    if m > max_mag:
        vec.scale_to_length(max_mag)
    return vec

def steer_towards(current_vel: pygame.math.Vector2,
                  desired: pygame.math.Vector2,
                  max_force: float) -> pygame.math.Vector2:
    return clamp_mag(desired - current_vel, max_force)

def load_ant_sprite():
    """
    Try loading 'assets/ant.png' then './ant.png'.
    Returns (surface, is_loaded_bool).
    """
    paths = ["assets/ant.png", "ant.png"]
    for p in paths:
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                return img, True
            except Exception:
                pass
    return None, False

class SpriteBank:
    """
    Caches rotated/scaled versions of the ant sprite at ANGLE_STEP increments.
    Heading 0deg = pointing EAST; we rotate so heading aligns with velocity.
    """
    def __init__(self, base_surface, scale=1.0, angle_step=5):
        self.ok = base_surface is not None
        self.angle_step = angle_step
        self.cache = {}
        if self.ok:
            w, h = base_surface.get_size()
            scaled = pygame.transform.smoothscale(base_surface, (int(w*scale), int(h*scale)))
            self.base = scaled
        else:
            self.base = None

    def get(self, angle_degrees):
        """
        angle_degrees: 0 points EAST; pygame's rotation is ccw, so use -angle for screen.
        We quantize to nearest ANGLE_STEP for caching.
        """
        if not self.ok:
            return None
        q = int(round(angle_degrees / self.angle_step) * self.angle_step) % 360
        if q not in self.cache:
            # pygame.transform.rotate rotates ccw; we want sprite to face angle
            self.cache[q] = pygame.transform.rotate(self.base, -q)
        return self.cache[q]

# ---------- Entities ----------
class Boid:
    __slots__ = ("pos", "vel")
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        ang = random.uniform(0, 2*math.pi)
        self.vel = pygame.math.Vector2(math.cos(ang), math.sin(ang))
        self.vel.scale_to_length(MAX_SPEED * 0.75)

    def update(self, accel, dt):
        self.vel += accel
        clamp_mag(self.vel, MAX_SPEED)
        self.pos += self.vel * dt
        if self.pos.x < 0: self.pos.x += WIDTH
        elif self.pos.x >= WIDTH: self.pos.x -= WIDTH
        if self.pos.y < 0: self.pos.y += HEIGHT
        elif self.pos.y >= HEIGHT: self.pos.y -= HEIGHT

    def draw(self, surf, sprite_bank: SpriteBank | None):
        if sprite_bank and sprite_bank.ok and self.vel.length_squared() > 1e-6:
            # angle in degrees where 0 = east, atan2 gives angle from x-axis (radians)
            angle = math.degrees(math.atan2(self.vel.y, self.vel.x))
            img = sprite_bank.get(angle)
            if img:
                rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                surf.blit(img, rect)
                return
        # Fallback: draw as a small triangle
        fwd = self.vel.normalize() if self.vel.length_squared() > 1e-6 else pygame.math.Vector2(1,0)
        left = pygame.math.Vector2(-fwd.y, fwd.x)
        size = 9
        tip = self.pos + fwd * size
        bl  = self.pos - fwd * (size - 3) + left * (size/2.4)
        br  = self.pos - fwd * (size - 3) - left * (size/2.4)
        pygame.draw.polygon(surf, TRI_COLOR, (tip, bl, br))

class PushObject:
    __slots__ = ("pos", "vel")
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)

    def step(self, dt):
        self.pos += self.vel * dt
        clamp_mag(self.vel, OBJECT_MAX_SPEED)
        self.vel *= OBJECT_FRICTION
        bounced = False
        if self.pos.x < OBJECT_RADIUS:
            self.pos.x = OBJECT_RADIUS; self.vel.x *= -0.4; bounced = True
        elif self.pos.x > WIDTH - OBJECT_RADIUS:
            self.pos.x = WIDTH - OBJECT_RADIUS; self.vel.x *= -0.4; bounced = True
        if self.pos.y < OBJECT_RADIUS:
            self.pos.y = OBJECT_RADIUS; self.vel.y *= -0.4; bounced = True
        elif self.pos.y > HEIGHT - OBJECT_RADIUS:
            self.pos.y = HEIGHT - OBJECT_RADIUS; self.vel.y *= -0.4; bounced = True
        if bounced: self.vel *= 0.9

    def draw(self, surf, in_goal=False):
        pygame.draw.circle(
            surf,
            OBJECT_IN_GOAL_COLOR if in_goal else OBJECT_COLOR,
            (int(self.pos.x), int(self.pos.y)),
            OBJECT_RADIUS
        )

# ---------- Simulation ----------
class Swarm:
    def __init__(self, n_boids: int, n_objects: int):
        self.boids = [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(n_boids)]
        self.objects = [
            PushObject(
                random.uniform(WIDTH * 0.12, WIDTH * 0.45),
                random.uniform(HEIGHT * 0.55, HEIGHT * 0.88),
            )
            for _ in range(n_objects)
        ]
        self.target = None

    def set_target(self, pos_or_none):
        self.target = pos_or_none

    def _all_objects_in_goal(self):
        for o in self.objects:
            if (o.pos - pygame.math.Vector2(GOAL_POS)).length() > GOAL_RADIUS - OBJECT_RADIUS:
                return False
        return True

    def step(self, dt, now_ms):
        global objects_all_in_goal_since, OBJECTS_IN_GOAL

        for i, b in enumerate(self.boids):
            align = pygame.math.Vector2(0, 0)
            coh   = pygame.math.Vector2(0, 0)
            sep   = pygame.math.Vector2(0, 0)
            total = 0

            for j, other in enumerate(self.boids):
                if i == j: continue
                off = other.pos - b.pos
                d2 = off.length_squared()
                if d2 < NEIGHBOR_RADIUS * NEIGHBOR_RADIUS:
                    total += 1
                    align += other.vel
                    coh   += other.pos
                    if d2 < SEPARATION_RADIUS * SEPARATION_RADIUS and d2 > 0:
                        sep -= off / (math.sqrt(d2) + 1e-6)

            a = pygame.math.Vector2(0, 0)
            if total > 0:
                align /= total
                if align.length_squared() > 1e-12:
                    align = align.normalize() * MAX_SPEED
                a += steer_towards(b.vel, align, MAX_FORCE)

                coh  /= total
                to_c = (coh - b.pos)
                if to_c.length_squared() > 1e-12:
                    to_c = to_c.normalize() * MAX_SPEED
                a += steer_towards(b.vel, to_c, MAX_FORCE * 0.85)

                if sep.length_squared() > 1e-12:
                    sep = sep.normalize() * MAX_SPEED
                a += steer_towards(b.vel, sep, MAX_FORCE * 1.2)

            # object interactions
            for o in self.objects:
                to_o = o.pos - b.pos
                d = to_o.length()

                if d < ATTRACTION_RADIUS and d > 1e-6:
                    desired = to_o.normalize() * MAX_SPEED * 0.8
                    a += steer_towards(b.vel, desired, MAX_FORCE * 0.9)

                if d < OBJECT_SEPARATION_RADIUS and d > 1e-6:
                    away = (-to_o).normalize() * MAX_SPEED
                    a += steer_towards(b.vel, away, MAX_FORCE * 1.1)

                if d < OBJECT_RADIUS + 12 and b.vel.length_squared() > 1e-6:
                    o.vel += b.vel.normalize() * OBJECT_PUSH_FORCE

            if self.target is not None:
                to_t = pygame.math.Vector2(self.target) - b.pos
                if to_t.length_squared() > 1e-12:
                    desired = to_t.normalize() * MAX_SPEED
                    a += steer_towards(b.vel, desired, MAX_FORCE) * TARGET_ATTRACTION

            b.update(a, dt)

        for o in self.objects:
            o.step(dt)

        if self._all_objects_in_goal():
            if objects_all_in_goal_since is None:
                objects_all_in_goal_since = now_ms
            elif now_ms - objects_all_in_goal_since >= TARGET_HOLD_TIME_MS:
                OBJECTS_IN_GOAL = True
        else:
            objects_all_in_goal_since = None
            OBJECTS_IN_GOAL = False

    def draw(self, surf, sprite_bank: SpriteBank | None, draw_fov=False, draw_broadcast=False):
        # goal
        pygame.draw.circle(surf, GOAL_COLOR, GOAL_POS, GOAL_RADIUS)
        pygame.draw.circle(surf, GOAL_RING, GOAL_POS, GOAL_RADIUS, 3)

        # objects
        for o in self.objects:
            in_goal = (o.pos - pygame.math.Vector2(GOAL_POS)).length() <= GOAL_RADIUS - OBJECT_RADIUS
            o.draw(surf, in_goal)

        # boids
        for b in self.boids:
            b.draw(surf, sprite_bank)
            if draw_fov:
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), NEIGHBOR_RADIUS, 1)
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), SEPARATION_RADIUS, 1)
            if draw_broadcast:
                pygame.draw.circle(surf, (120,130,150), (int(b.pos.x), int(b.pos.y)), BROADCAST_RADIUS, 1)

# ---------- HUD (text, safe fallback) ----------
def draw_hud(screen, dt_ms, fps, swarm):
    try:
        font = pygame.font.Font(None, 20)
    except Exception:
        pygame.draw.rect(screen, HUD_BG, (0, 0, WIDTH, 26))
        return

    pygame.draw.rect(screen, HUD_BG, (0, 0, WIDTH, 26))
    info = [
        f"FPS {fps:.0f}",
        f"dt {dt_ms}ms",
        f"Boids {len(swarm.boids)}",
        f"Objs {len(swarm.objects)}",
        f"Goal {'OK' if OBJECTS_IN_GOAL else '--'}",
        "[Space] pause  [F] FOV  [B] rings  [+/-] boids  [O] obj  [R] reset  [?] help",
    ]
    x = 8
    for s in info:
        surf = font.render(s, True, HUD_TEXT)
        screen.blit(surf, (x, 6))
        x += surf.get_width() + 12

def draw_help_overlay(screen):
    try:
        font = pygame.font.Font(None, 22)
    except Exception:
        return
    pad = 10
    lines = [
        "Controls:",
        "Click: set/clear target pointer",
        "Space: pause/resume",
        "F: toggle FOV rings",
        "B: toggle broadcast rings",
        "+ / -: add/remove boids",
        "O: add object  |  R: reset",
        "?: toggle this help",
    ]
    w = max(font.size(l)[0] for l in lines) + pad*2
    h = (len(lines) * (font.get_height()+2)) + pad*2
    rect = pygame.Rect(8, HEIGHT - h - 8, w, h)
    pygame.draw.rect(screen, (250, 250, 255), rect)
    pygame.draw.rect(screen, (40, 45, 55), rect, 2)
    y = rect.top + pad
    for l in lines:
        surf = font.render(l, True, (30, 34, 44))
        screen.blit(surf, (rect.left + pad, y))
        y += font.get_height() + 2

# ---------- Main (async) ----------
async def main():
    pygame.init()
    try: pygame.mixer.quit()
    except Exception: pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Swarms — Ant Sprite (pygbag)")
    clock = pygame.time.Clock()

    # Load ant sprite (safe fallback if missing)
    base_ant, ok = load_ant_sprite()
    sprite_bank = SpriteBank(base_ant, scale=ANT_SCALE, angle_step=ANGLE_STEP) if ok else None

    swarm = Swarm(NUM_BOIDS, NUM_OBJECTS)
    global PAUSED, DRAW_FOV, DRAW_BROADCAST, SHOW_HELP

    last_ticks = pygame.time.get_ticks()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE:
                    PAUSED = not PAUSED
                elif e.key == pygame.K_f:
                    DRAW_FOV = not DRAW_FOV
                elif e.key == pygame.K_b:
                    DRAW_BROADCAST = not DRAW_BROADCAST
                elif e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    swarm.boids.append(Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
                elif e.key == pygame.K_MINUS and len(swarm.boids) > 1:
                    swarm.boids.pop()
                elif e.key == pygame.K_o:
                    x = random.uniform(WIDTH*0.12, WIDTH*0.45)
                    y = random.uniform(HEIGHT*0.55, HEIGHT*0.88)
                    swarm.objects.append(PushObject(x, y))
                elif e.key == pygame.K_r:
                    swarm = Swarm(NUM_BOIDS, NUM_OBJECTS)
                    globals()['objects_all_in_goal_since'] = None
                    globals()['OBJECTS_IN_GOAL'] = False
                elif e.key == pygame.K_SLASH:  # '?' (Shift+/)
                    SHOW_HELP = not SHOW_HELP

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = pygame.mouse.get_pos()
                if swarm.target is None:
                    swarm.set_target(pos)
                else:
                    old = pygame.math.Vector2(swarm.target)
                    if (old - pygame.math.Vector2(pos)).length() < 12:
                        swarm.set_target(None)
                    else:
                        swarm.set_target(pos)

        # dt using ticks (clamped)
        now = pygame.time.get_ticks()
        dt_ms = now - last_ticks
        last_ticks = now
        if dt_ms <= 0:
            dt_ms = 1000 // FPS
        dt_ms = max(1000 // 300, min(dt_ms, 1000 // 30))  # ~3.3ms .. ~33ms
        dt = dt_ms / 1000.0

        if not PAUSED:
            swarm.step(dt, now)

        screen.fill(BG_COLOR)
        swarm.draw(screen, sprite_bank, draw_fov=DRAW_FOV, draw_broadcast=DRAW_BROADCAST)
        draw_hud(screen, dt_ms, clock.get_fps(), swarm)
        if SHOW_HELP:
            draw_help_overlay(screen)
        pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
