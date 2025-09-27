# main.py — Ant Swarm with Roles, Food Delivery, and Pheromone Trails (pygbag-safe)
# Place your sprite at: assets/ant.png  (or ./ant.png)
# Controls:
#   Click: set/clear target pointer (global attractor)
#   Space: pause/resume
#   F: toggle FOV rings
#   B: toggle broadcast rings
#   T: toggle pheromone overlay
#   P: pause/unpause pheromone simulation (for perf testing)
#   +/-: add/remove workers
#   O: add a food object
#   R: reset
#   ?: toggle help overlay

try:
    import asyncio
except Exception:
    import pygbag.aio as asyncio

import random, math, os
import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Roles
QUEENS = 1
NUM_BOIDS = 60                     # total ants (queen + workers)
assert NUM_BOIDS >= QUEENS
WORKERS = NUM_BOIDS - QUEENS

# Motion (base)
MAX_SPEED_WORKER = 4.2
MAX_SPEED_QUEEN  = 3.2
MAX_FORCE_WORKER = 0.10
MAX_FORCE_QUEEN  = 0.07

NEIGHBOR_RADIUS = 90
SEPARATION_RADIUS = 26
TARGET_ATTRACTION = 0.06

# Objects (food)
NUM_OBJECTS = 7
OBJECT_RADIUS = 12
OBJECT_PUSH_FORCE = 0.28
OBJECT_SEPARATION_RADIUS = 60
OBJECT_FRICTION = 0.965
OBJECT_MAX_SPEED = 2.4
ATTRACTION_RADIUS = 140

# Goal (nest)
GOAL_POS = (int(WIDTH * 0.82), int(HEIGHT * 0.25))
GOAL_RADIUS = 100
TARGET_HOLD_TIME_MS = 3000
objects_all_in_goal_since = None
OBJECTS_IN_GOAL = False

# Pheromones (stigmergy)
PHER_VISIBLE = True         # show overlay
PHER_ENABLED = True         # update field
PHER_CELL = 14              # grid cell size (px)
PHER_W = WIDTH // PHER_CELL
PHER_H = HEIGHT // PHER_CELL
PHER_DEPOSIT_RECRUIT = 0.85 # deposited near food/objects
PHER_DEPOSIT_HOME    = 0.40 # deposited when near goal/nest
PHER_FOLLOW_GAIN     = 0.13 # turns gradient into steering
PHER_EVAPORATE       = 0.985 # 0.98..0.995 (lower = faster fade)
PHER_DIFFUSE         = 0.08  # 0..0.15 approx
PHER_MIN_DRAW        = 0.03  # threshold to draw overlay
PHER_CLAMP           = 3.5   # cap the concentration

# Toggles/state
PAUSED = False
DRAW_FOV = False
DRAW_BROADCAST = False
SHOW_HELP = True
BROADCAST_RADIUS = 110

# Counters
FOOD_DELIVERED = 0
LARVA = 0

# Colors
BG_COLOR = (68, 72, 80)
TRI_COLOR = (248, 248, 255)          # fallback triangle color
FOV_COLOR = (135, 150, 170)
OBJECT_COLOR = (70, 165, 255)
OBJECT_IN_GOAL_COLOR = (90, 230, 150)
GOAL_COLOR = (160, 230, 200)
GOAL_RING = (60, 140, 110)
HUD_BG = (240, 245, 255)
HUD_TEXT = (28, 32, 40)
PHER_COLOR_RECRUIT = (255, 120, 70)  # orange-ish for recruit trails
PHER_COLOR_HOME    = (90, 220, 180)  # teal-ish for home trails

# Sprite tuning
ANT_TARGET_HEIGHT = 14
ANGLE_STEP = 5

# ---------- Helpers ----------
def clamp_mag(vec: pygame.math.Vector2, max_mag: float) -> pygame.math.Vector2:
    m = vec.length()
    if m > max_mag:
        vec.scale_to_length(max_mag)
    return vec

def steer_towards(cur_v: pygame.math.Vector2,
                  desired: pygame.math.Vector2,
                  max_force: float) -> pygame.math.Vector2:
    return clamp_mag(desired - cur_v, max_force)

def load_ant_sprite():
    for p in ("assets/ant.png", "ant.png"):
        if os.path.exists(p):
            try:
                return pygame.image.load(p).convert_alpha(), True
            except Exception:
                pass
    return None, False

class SpriteBank:
    def __init__(self, base_surface, target_height=ANT_TARGET_HEIGHT, angle_step=ANGLE_STEP):
        self.ok = base_surface is not None
        self.angle_step = angle_step
        self.cache = {}
        if self.ok:
            w, h = base_surface.get_size()
            if h <= 0:
                self.ok = False
                self.base = None
            else:
                new_h = max(6, int(target_height))
                new_w = max(6, int(w * (new_h / h)))
                self.base = pygame.transform.smoothscale(base_surface, (new_w, new_h))
        else:
            self.base = None

    def get(self, angle_degrees):
        if not self.ok:
            return None
        q = int(round(angle_degrees / self.angle_step) * self.angle_step) % 360
        got = self.cache.get(q)
        if got is None:
            self.cache[q] = pygame.transform.rotate(self.base, -q)
            got = self.cache[q]
        return got

# ---------- Pheromone Field ----------
class PherField:
    """Two-channel field: recruit (to food) and home (to nest)."""
    __slots__ = ("w","h","cell","recruit","home","surface_recruit","surface_home")
    def __init__(self, w, h, cell):
        self.w, self.h, self.cell = w, h, cell
        self.recruit = [[0.0]*h for _ in range(w)]
        self.home    = [[0.0]*h for _ in range(w)]
        # cached surfaces to draw overlay efficiently
        self.surface_recruit = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        self.surface_home    = pygame.Surface((w, h), flags=pygame.SRCALPHA)

    def idx(self, x, y):
        gx = int(x // self.cell); gy = int(y // self.cell)
        if gx < 0: gx = 0
        elif gx >= self.w: gx = self.w-1
        if gy < 0: gy = 0
        elif gy >= self.h: gy = self.h-1
        return gx, gy

    def deposit_recruit(self, x, y, amount):
        gx, gy = self.idx(x, y)
        v = self.recruit[gx][gy] + amount
        self.recruit[gx][gy] = v if v < PHER_CLAMP else PHER_CLAMP

    def deposit_home(self, x, y, amount):
        gx, gy = self.idx(x, y)
        v = self.home[gx][gy] + amount
        self.home[gx][gy] = v if v < PHER_CLAMP else PHER_CLAMP

    def sample_grad(self, arr, x, y):
        # central difference in grid; returns approximate gradient vector in world coords
        gx, gy = self.idx(x, y)
        x0 = max(0, gx-1); x1 = min(self.w-1, gx+1)
        y0 = max(0, gy-1); y1 = min(self.h-1, gy+1)
        dx = (arr[x1][gy] - arr[x0][gy]) / (x1 - x0 if x1 != x0 else 1)
        dy = (arr[gx][y1] - arr[gx][y0]) / (y1 - y0 if y1 != y0 else 1)
        # map grid gradient to world—scale by 1/cell
        return pygame.math.Vector2(dx, dy) / self.cell

    def evaporate_and_diffuse(self):
        # evaporate
        for chan in (self.recruit, self.home):
            for x in range(self.w):
                row = chan[x]
                for y in range(self.h):
                    row[y] *= PHER_EVAPORATE

        if PHER_DIFFUSE <= 0:
            return

        # simple 4-neighbour diffusion (one pass)
        def diffuse_one(chan):
            # create a shallow copy grid
            nxt = [row[:] for row in chan]
            for x in range(self.w):
                for y in range(self.h):
                    v = chan[x][y]
                    acc = 0.0; n = 0
                    if x > 0:   acc += chan[x-1][y]; n += 1
                    if x < self.w-1: acc += chan[x+1][y]; n += 1
                    if y > 0:   acc += chan[x][y-1]; n += 1
                    if y < self.h-1: acc += chan[x][y+1]; n += 1
                    if n:
                        nxt[x][y] = (1-PHER_DIFFUSE)*v + PHER_DIFFUSE*(acc/n)
            return nxt
        self.recruit = diffuse_one(self.recruit)
        self.home    = diffuse_one(self.home)

    def rebuild_surfaces(self):
        # Draw tiny 1x1 alpha pixels representing intensity; scaled when blitted
        self.surface_recruit.fill((0,0,0,0))
        self.surface_home.fill((0,0,0,0))
        pr = self.surface_recruit
        ph = self.surface_home
        r,g,b = PHER_COLOR_RECRUIT
        r2,g2,b2 = PHER_COLOR_HOME
        for x in range(self.w):
            cr = self.recruit[x]; ch = self.home[x]
            for y in range(self.h):
                vr = cr[y]; vh = ch[y]
                if vr > PHER_MIN_DRAW:
                    a = max(15, min(160, int(60 + 80*(vr/PHER_CLAMP))))
                    pr.set_at((x,y), (r,g,b,a))
                if vh > PHER_MIN_DRAW:
                    a = max(15, min(160, int(60 + 80*(vh/PHER_CLAMP))))
                    ph.set_at((x,y), (r2,g2,b2,a))

    def draw(self, screen):
        # scale tiny field to world size
        if self.surface_recruit.get_width() != self.w:
            return
        rw = self.w * self.cell; rh = self.h * self.cell
        # build scaled surfaces on the fly (fast enough at these sizes)
        screen.blit(pygame.transform.scale(self.surface_recruit, (rw, rh)), (0,0))
        screen.blit(pygame.transform.scale(self.surface_home,    (rw, rh)), (0,0))

# ---------- Entities ----------
class Boid:
    __slots__ = ("pos","vel","is_queen")
    def __init__(self, x, y, is_queen=False):
        self.pos = pygame.math.Vector2(x, y)
        ang = random.uniform(0, 2*math.pi)
        self.vel = pygame.math.Vector2(math.cos(ang), math.sin(ang))
        self.vel.scale_to_length((MAX_SPEED_QUEEN if is_queen else MAX_SPEED_WORKER) * 0.75)
        self.is_queen = is_queen

    def update(self, accel, dt):
        if self.is_queen:
            accel *= 0.6
        self.vel += accel
        clamp_mag(self.vel, MAX_SPEED_QUEEN if self.is_queen else MAX_SPEED_WORKER)
        self.pos += self.vel * dt
        if self.pos.x < 0: self.pos.x += WIDTH
        elif self.pos.x >= WIDTH: self.pos.x -= WIDTH
        if self.pos.y < 0: self.pos.y += HEIGHT
        elif self.pos.y >= HEIGHT: self.pos.y -= HEIGHT

    def draw(self, surf, sprite_bank):
        # sprite if available; else triangle
        if sprite_bank and sprite_bank.ok and self.vel.length_squared() > 1e-6:
            angle = math.degrees(math.atan2(self.vel.y, self.vel.x))
            img = sprite_bank.get(angle)
            if img:
                rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                surf.blit(img, rect)
                return
        fwd = self.vel.normalize() if self.vel.length_squared() > 1e-6 else pygame.math.Vector2(1,0)
        left = pygame.math.Vector2(-fwd.y, fwd.x)
        size = 10 if self.is_queen else 8
        tip = self.pos + fwd * size
        bl  = self.pos - fwd * (size - 3) + left * (size/2.4)
        br  = self.pos - fwd * (size - 3) - left * (size/2.4)
        pygame.draw.polygon(surf, TRI_COLOR, (tip, bl, br))

class PushObject:
    __slots__ = ("pos","vel","delivered")
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.delivered = False

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
        pygame.draw.circle(surf, OBJECT_IN_GOAL_COLOR if in_goal else OBJECT_COLOR,
                           (int(self.pos.x), int(self.pos.y)), OBJECT_RADIUS)

# ---------- Simulation ----------
class Swarm:
    def __init__(self, total_ants: int, n_objects: int):
        # queen + workers
        n_q = min(QUEENS, max(0, total_ants))
        n_w = max(0, total_ants - n_q)
        self.boids = [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), True) for _ in range(n_q)]
        self.boids += [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), False) for _ in range(n_w)]

        # food objects
        self.objects = []
        for _ in range(n_objects):
            x = random.uniform(WIDTH * 0.12, WIDTH * 0.45)
            y = random.uniform(HEIGHT * 0.55, HEIGHT * 0.88)
            self.objects.append(PushObject(x, y))

        self.target = None

    def set_target(self, pos_or_none):
        self.target = pos_or_none

    def _all_objects_in_goal(self):
        for o in self.objects:
            if (o.pos - pygame.math.Vector2(GOAL_POS)).length() > GOAL_RADIUS - OBJECT_RADIUS:
                return False
        return True

    def step(self, dt, now_ms, pher: "PherField"):
        global objects_all_in_goal_since, OBJECTS_IN_GOAL, FOOD_DELIVERED, LARVA

        # --- Boids ---
        for i, b in enumerate(self.boids):
            max_speed = MAX_SPEED_QUEEN if b.is_queen else MAX_SPEED_WORKER
            max_force = MAX_FORCE_QUEEN if b.is_queen else MAX_FORCE_WORKER

            align = pygame.math.Vector2(0, 0)
            coh   = pygame.math.Vector2(0, 0)
            sep   = pygame.math.Vector2(0, 0)
            total = 0

            # neighbors
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
                # alignment / cohesion / separation
                align /= total
                if align.length_squared() > 1e-12:
                    align = align.normalize() * max_speed
                a += steer_towards(b.vel, align, max_force)

                coh  /= total
                to_c = (coh - b.pos)
                if to_c.length_squared() > 1e-12:
                    to_c = to_c.normalize() * max_speed
                a += steer_towards(b.vel, to_c, max_force * 0.85)

                if sep.length_squared() > 1e-12:
                    sep = sep.normalize() * max_speed
                a += steer_towards(b.vel, sep, max_force * 1.2)

            # pheromone guidance (workers mostly)
            if not b.is_queen:
                # follow recruit (toward food) if stronger; else follow home (toward nest)
                grad_r = pher.sample_grad(pher.recruit, b.pos.x, b.pos.y)
                grad_h = pher.sample_grad(pher.home,    b.pos.x, b.pos.y)
                # choose channel with stronger local magnitude
                if grad_r.length_squared() > grad_h.length_squared() * 1.3:
                    desired = grad_r.normalize() * max_speed if grad_r.length() > 1e-6 else pygame.math.Vector2()
                    a += steer_towards(b.vel, desired, max_force) * PHER_FOLLOW_GAIN
                elif grad_h.length_squared() > 0.0:
                    desired = grad_h.normalize() * max_speed if grad_h.length() > 1e-6 else pygame.math.Vector2()
                    a += steer_towards(b.vel, desired, max_force) * PHER_FOLLOW_GAIN

            # objects interaction + recruiting deposit
            near_food = False
            for o in self.objects:
                to_o = o.pos - b.pos
                d = to_o.length()

                if d < ATTRACTION_RADIUS and d > 1e-6:
                    desired = to_o.normalize() * max_speed * 0.8
                    a += steer_towards(b.vel, desired, max_force * 0.9)

                if d < OBJECT_SEPARATION_RADIUS and d > 1e-6:
                    away = (-to_o).normalize() * max_speed
                    a += steer_towards(b.vel, away, max_force * 1.1)

                if d < OBJECT_RADIUS + 12 and b.vel.length_squared() > 1e-6:
                    o.vel += b.vel.normalize() * OBJECT_PUSH_FORCE
                    near_food = True

            if PHER_ENABLED and near_food and not b.is_queen:
                # deposit recruit pheromone near food
                pher.deposit_recruit(b.pos.x, b.pos.y, PHER_DEPOSIT_RECRUIT)

            # optional pointer (global attractor)
            if self.target is not None:
                to_t = pygame.math.Vector2(self.target) - b.pos
                if to_t.length_squared() > 1e-12:
                    desired = to_t.normalize() * max_speed
                    a += steer_towards(b.vel, desired, max_force) * TARGET_ATTRACTION

            # deposit home pheromone near nest
            if PHER_ENABLED:
                if (b.pos - pygame.math.Vector2(GOAL_POS)).length() < GOAL_RADIUS * 1.2:
                    if not b.is_queen:
                        pher.deposit_home(b.pos.x, b.pos.y, PHER_DEPOSIT_HOME * 0.7)
                elif not b.is_queen:
                    # small ongoing home scent to build paths
                    pher.deposit_home(b.pos.x, b.pos.y, PHER_DEPOSIT_HOME * 0.12)

            b.update(a, dt)

        # --- Objects ---
        delivered_now = 0
        for o in self.objects:
            o.step(dt)
            in_goal = (o.pos - pygame.math.Vector2(GOAL_POS)).length() <= GOAL_RADIUS - OBJECT_RADIUS
            if in_goal and not o.delivered:
                o.delivered = True
                delivered_now += 1
                FOOD_DELIVERED += 1

        # goal hold timer for "mission success"
        if self._all_objects_in_goal():
            if objects_all_in_goal_since is None:
                objects_all_in_goal_since = now_ms
            elif now_ms - objects_all_in_goal_since >= TARGET_HOLD_TIME_MS:
                OBJECTS_IN_GOAL = True
                # hatch a larva on mission lock (once per hold window)
                if delivered_now > 0:
                    LARVA += delivered_now
        else:
            objects_all_in_goal_since = None
            OBJECTS_IN_GOAL = False

    def draw(self, surf, sprite_bank, draw_fov=False, draw_broadcast=False):
        # nest goal
        pygame.draw.circle(surf, GOAL_COLOR, GOAL_POS, GOAL_RADIUS)
        pygame.draw.circle(surf, GOAL_RING, GOAL_POS, GOAL_RADIUS, 3)

        # food objects
        for o in self.objects:
            in_goal = (o.pos - pygame.math.Vector2(GOAL_POS)).length() <= GOAL_RADIUS - OBJECT_RADIUS
            o.draw(surf, in_goal)

        # ants
        for b in self.boids:
            b.draw(surf, sprite_bank)
            if draw_fov:
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), NEIGHBOR_RADIUS, 1)
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), SEPARATION_RADIUS, 1)
            if draw_broadcast:
                pygame.draw.circle(surf, (120,130,150), (int(b.pos.x), int(b.pos.y)), BROADCAST_RADIUS, 1)

# ---------- HUD ----------
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
        f"Queen {QUEENS}  Workers {len(swarm.boids)-QUEENS}",
        f"Food {FOOD_DELIVERED}",
        f"Larva {LARVA}",
        f"Goal {'OK' if OBJECTS_IN_GOAL else '--'}",
        "[Space] pause  F FOV  B rings  T pher  P pher-pause  +/- ants  O add food  R reset  ? help",
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
        "T: toggle pheromone overlay",
        "P: pause/unpause pheromone simulation",
        "+ / -: add/remove workers",
        "O: add food object  |  R: reset",
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
    pygame.display.set_caption("Ant Swarm — Roles + Pheromones (pygbag)")
    clock = pygame.time.Clock()

    base_ant, ok = load_ant_sprite()
    sprite_bank = SpriteBank(base_ant) if ok else None

    swarm = Swarm(NUM_BOIDS, NUM_OBJECTS)
    pher = PherField(PHER_W, PHER_H, PHER_CELL)

    global PAUSED, DRAW_FOV, DRAW_BROADCAST, SHOW_HELP, PHER_VISIBLE, PHER_ENABLED

    last_ticks = pygame.time.get_ticks()
    rebuild_timer = 0.0   # for pher overlay refresh throttling

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running = False
                elif e.key == pygame.K_SPACE: PAUSED = not PAUSED
                elif e.key == pygame.K_f: DRAW_FOV = not DRAW_FOV
                elif e.key == pygame.K_b: DRAW_BROADCAST = not DRAW_BROADCAST
                elif e.key == pygame.K_t: PHER_VISIBLE = not PHER_VISIBLE
                elif e.key == pygame.K_p: PHER_ENABLED = not PHER_ENABLED
                elif e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    swarm.boids.append(Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), False))
                elif e.key == pygame.K_MINUS and len(swarm.boids) > QUEENS:
                    # remove a worker, keep queens
                    for i, b in enumerate(swarm.boids[::-1]):
                        if not b.is_queen:
                            swarm.boids.pop(len(swarm.boids)-1-i)
                            break
                elif e.key == pygame.K_o:
                    x = random.uniform(WIDTH*0.12, WIDTH*0.45)
                    y = random.uniform(HEIGHT*0.55, HEIGHT*0.88)
                    swarm.objects.append(PushObject(x, y))
                elif e.key == pygame.K_r:
                    # full reset
                    while len(swarm.boids) > QUEENS:
                        swarm.boids.pop()
                    # re-add workers
                    for _ in range(WORKERS):
                        swarm.boids.append(Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), False))
                    swarm.objects = []
                    for _ in range(NUM_OBJECTS):
                        x = random.uniform(WIDTH*0.12, WIDTH*0.45)
                        y = random.uniform(HEIGHT*0.55, HEIGHT*0.88)
                        swarm.objects.append(PushObject(x, y))
                    globals()['objects_all_in_goal_since'] = None
                    globals()['OBJECTS_IN_GOAL'] = False
                    globals()['FOOD_DELIVERED'] = 0
                    globals()['LARVA'] = 0
                    pher = PherField(PHER_W, PHER_H, PHER_CELL)
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
        if dt_ms <= 0: dt_ms = 1000 // FPS
        dt_ms = max(1000 // 300, min(dt_ms, 1000 // 30))
        dt = dt_ms / 1000.0

        if not PAUSED:
            swarm.step(dt, now, pher)
            if PHER_ENABLED:
                pher.evaporate_and_diffuse()

        # limited overlay rebuild (every ~0.15s) to save CPU in browser
        rebuild_timer += dt
        if PHER_VISIBLE and rebuild_timer > 0.15:
            pher.rebuild_surfaces()
            rebuild_timer = 0.0

        # draw
        screen.fill(BG_COLOR)
        if PHER_VISIBLE:
            pher.draw(screen)
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
