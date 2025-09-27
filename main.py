# main.py
# Pygbag-friendly Pygame app with a simple boids swarm.
# - Async main loop (await asyncio.sleep(0)) so the browser doesn't freeze
# - No blocking time.sleep or threads
# - Uses pygame.math.Vector2 (no NumPy required)
# - Audio disabled by default to avoid autoplay issues on the web

try:
    import asyncio
except Exception:
    import pygbag.aio as asyncio

import random, math
import pygame

WIDTH, HEIGHT = 1000, 1000
FPS = 60

NUM_BOIDS = 50
MAX_SPEED = 3.5
MAX_FORCE = 0.08

NEIGHBOR_RADIUS = 80
SEPARATION_RADIUS = 24

DRAW_FOV = False
PAUSED = False

BG_COLOR = (10, 10, 12)
BOID_COLOR = (220, 220, 240)
FOV_COLOR = (60, 60, 80)
TARGET_COLOR = (255, 180, 60)

TARGET_ATTRACTION = 0.05

def clamp_mag(vec: pygame.math.Vector2, max_mag: float) -> pygame.math.Vector2:
    m = vec.length()
    if m > max_mag:
        vec.scale_to_length(max_mag)
    return vec

def steer_towards(current_vel: pygame.math.Vector2,
                  desired: pygame.math.Vector2,
                  max_force: float) -> pygame.math.Vector2:
    steer = desired - current_vel
    return clamp_mag(steer, max_force)

class Boid:
    __slots__ = ("pos", "vel")
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.vel.scale_to_length(MAX_SPEED * 0.5)

    def update(self, accel, dt):
        self.vel += accel
        clamp_mag(self.vel, MAX_SPEED)
        self.pos += self.vel * dt
        if self.pos.x < 0: self.pos.x += WIDTH
        elif self.pos.x >= WIDTH: self.pos.x -= WIDTH
        if self.pos.y < 0: self.pos.y += HEIGHT
        elif self.pos.y >= HEIGHT: self.pos.y -= HEIGHT

    def draw(self, surf):
        forward = self.vel.normalize() if self.vel.length_squared() > 1e-6 else pygame.math.Vector2(1, 0)
        left = pygame.math.Vector2(-forward.y, forward.x)
        tip = self.pos + forward * 8
        base_left = self.pos - forward * 6 + left * 4
        base_right = self.pos - forward * 6 - left * 4
        pygame.draw.polygon(surf, BOID_COLOR, (tip, base_left, base_right))

class Swarm:
    def __init__(self, n_boids: int):
        self.boids = [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(n_boids)]
        self.target = None

    def set_target(self, pos_or_none):
        self.target = pos_or_none

    def step(self, dt):
        for i, b in enumerate(self.boids):
            align = pygame.math.Vector2(0, 0)
            coh = pygame.math.Vector2(0, 0)
            sep = pygame.math.Vector2(0, 0)
            total = 0

            for j, other in enumerate(self.boids):
                if i == j: continue
                offset = other.pos - b.pos
                d2 = offset.length_squared()
                if d2 < NEIGHBOR_RADIUS * NEIGHBOR_RADIUS:
                    total += 1
                    align += other.vel
                    coh += other.pos
                    if d2 < SEPARATION_RADIUS * SEPARATION_RADIUS and d2 > 0:
                        sep -= offset / (math.sqrt(d2) + 1e-6)

            accel = pygame.math.Vector2(0, 0)
            if total > 0:
                align /= total
                if align.length_squared() > 1e-12:
                    align = align.normalize() * MAX_SPEED
                accel += steer_towards(b.vel, align, MAX_FORCE)

                coh /= total
                desired_to_center = (coh - b.pos)
                if desired_to_center.length_squared() > 1e-12:
                    desired_to_center = desired_to_center.normalize() * MAX_SPEED
                accel += steer_towards(b.vel, desired_to_center, MAX_FORCE * 0.85)

                if sep.length_squared() > 1e-12:
                    sep = sep.normalize() * MAX_SPEED
                accel += steer_towards(b.vel, sep, MAX_FORCE * 1.2)

            if self.target is not None:
                to_target = pygame.math.Vector2(self.target) - b.pos
                if to_target.length_squared() > 1e-12:
                    desired = to_target.normalize() * MAX_SPEED
                    accel += steer_towards(b.vel, desired, MAX_FORCE) * TARGET_ATTRACTION

            b.update(accel, dt)

    def draw(self, surf, draw_fov=False):
        for b in self.boids:
            b.draw(surf)
            if draw_fov:
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), NEIGHBOR_RADIUS, 1)
                pygame.draw.circle(surf, FOV_COLOR, (int(b.pos.x), int(b.pos.y)), SEPARATION_RADIUS, 1)
        if self.target is not None:
            pygame.draw.circle(surf, TARGET_COLOR, (int(self.target[0]), int(self.target[1])), 6)

def draw_ui(screen, fps, boid_count, paused):
    font = pygame.font.SysFont(None, 20)
    lines = [
        f"FPS: {fps:.0f}",
        f"Boids: {boid_count}",
        f"{'PAUSED' if paused else 'RUNNING'}",
        "Mouse click: toggle target",
        "Space: pause/resume | F: toggle FOV | +/-: boids | R: reset",
    ]
    y = 8
    for line in lines:
        surf = font.render(line, True, (200, 200, 210))
        screen.blit(surf, (8, y))
        y += 18

async def main():
    pygame.init()
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Swarms (pygbag)")
    clock = pygame.time.Clock()
    swarm = Swarm(NUM_BOIDS)
    global PAUSED, DRAW_FOV

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
                elif e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    swarm.boids.append(Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
                elif e.key == pygame.K_MINUS and len(swarm.boids) > 1:
                    swarm.boids.pop()
                elif e.key == pygame.K_r:
                    swarm = Swarm(NUM_BOIDS)
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

        dt = clock.tick(FPS) / 1000.0
        if not PAUSED:
            swarm.step(dt)

        screen.fill(BG_COLOR)
        swarm.draw(screen, draw_fov=DRAW_FOV)
        draw_ui(screen, clock.get_fps(), len(swarm.boids), PAUSED)
        pygame.display.flip()

        # CRITICAL for pygbag/browser
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
