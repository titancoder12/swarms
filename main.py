import os
os.environ["SDL_AUDIODRIVER"] = "dummy"      # don't try to open real audio in the browser
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import os
import random
import math
import asyncio  # <-- added for pygbag async loop

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
# Boid settings
NUM_BOIDS = 10
MAX_SPEED = 5
MAX_FORCE = 1
OBJECT_PUSH_FORCE = 0.2
NEIGHBOR_RADIUS = 200
SEPARATION_RADIUS = 30
OBJECT_SEPERATION_RADIUS = 50
TRIANGLE_SIZE = 5
ATTRACTION_RADIUS = 100
OBJECTS_IN_GOAL = False  # Flag to check if all objects are in the goal
BROADCAST_RADIUS = 100
TARGET_HOLD_TIME = 3000  # 3 seconds in milliseconds
target_start_time = None  # Tracks when all objects entered the target
QUEENS = 1
WORKERS = 10
LARVA = 0
FOOD = 0

def render_UI(screen, boids):
    global NUM_BOIDS, MAX_SPEED, MAX_FORCE, NEIGHBOR_RADIUS, SEPARATION_RADIUS, OBJECT_SEPERATION_RADIUS, WIDTH, HEIGHT
    font = pygame.font.SysFont(None, 15)

    a = 140
    b = 10
    c = 50
    d = 10

    button_add_boids = pygame.Rect(a, b, c, d)  # Button to add boids
    button_remove_boids = pygame.Rect(a+60, b, c, d)  # Button to remove boids
    button_add_speed = pygame.Rect(a, b+20, c, d)  # Button to increase speed
    button_remove_speed = pygame.Rect(a+60, b+20, c, d)
    button_add_force = pygame.Rect(a, b+40, c, d)  # Button to increase force
    button_remove_force = pygame.Rect(a+60, b+40, c, d)
    button_add_neighbor_radius = pygame.Rect(a, b+60, c, d)
    button_remove_neighbor_radius = pygame.Rect(a+60, b+60, c, d)
    button_add_separation_radius = pygame.Rect(a, b+80, c, d)
    button_remove_separation_radius = pygame.Rect(a+60, b+80, c, d)
    button_add_object_separation_radius = pygame.Rect(a, b+100, c, d)
    button_remove_object_separation_radius = pygame.Rect(a+60, b+100, c, d)
    button_hatch_worker = pygame.Rect(a+60, b+240, c+40, d)
    button_hatch_queen = pygame.Rect(a+60, b+260, c+40, d)

    pygame.draw.rect(screen, (255, 255, 255), button_add_boids)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_boids)
    pygame.draw.rect(screen, (255, 255, 255), button_add_speed)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_speed)
    pygame.draw.rect(screen, (255, 255, 255), button_add_force)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_force)
    pygame.draw.rect(screen, (255, 255, 255), button_add_neighbor_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_neighbor_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_add_separation_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_separation_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_add_object_separation_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_remove_object_separation_radius)
    pygame.draw.rect(screen, (255, 255, 255), button_hatch_worker)
    pygame.draw.rect(screen, (255, 255, 255), button_hatch_queen)

    for button, label in [
            (button_add_boids, "+"),
            (button_remove_boids, "-"),
            (button_add_speed, "+"),
            (button_remove_speed, "-"),
            (button_add_force, "+"),
            (button_remove_force, "-"),
            (button_add_neighbor_radius, "+"),
            (button_remove_neighbor_radius, "-"),
            (button_add_separation_radius, "+"),
            (button_remove_separation_radius, "-"),
            (button_add_object_separation_radius, "+"),
            (button_remove_object_separation_radius, "-")
        ]:
            text = font.render(label, True, (0, 0, 0))  # Black text
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)

    boid_count_text = font.render(f"Ants: {len(boids)}", True, (255, 255, 255))  # White text
    max_speed_text = font.render(f"Max Speed: {MAX_SPEED}", True, (255, 255, 255))
    max_force_text = font.render(f"Max Force: {round(MAX_FORCE, 2)}", True, (255, 255, 255))
    neighbor_radius_text = font.render(f"Neighbor Radius: {NEIGHBOR_RADIUS}", True, (255, 255, 255))
    separation_radius_text = font.render(f"Separation Radius: {SEPARATION_RADIUS}", True, (255, 255, 255))
    width_text = font.render(f"Window Width: {WIDTH}", True, (255, 255, 255))
    height_text = font.render(f"Window Height: {HEIGHT}", True, (255, 255, 255))
    object_separation_radius_text = font.render(f"Object Separation: {OBJECT_SEPERATION_RADIUS}", True, (255, 255, 255))
    queens_text = font.render(f"Queens: {QUEENS}", True, (255, 255, 255))
    larva_text = font.render(f"Larva: {LARVA}", True, (255, 255, 255))
    food_text = font.render(f"Food: {FOOD}", True, (255, 255, 255))
    worker_text = font.render(f"Workers: {len(boids)}", True, (255, 255, 255))
    hatch_worker_text = font.render(f"Hatch Worker for 10 food and 1 larva", True, (255, 255, 255))
    hatch_queen_text = font.render(f"Hatch Queen for 500 food and 10 larva", True, (255, 255, 255))

    # Draw it on screen at top-left
    screen.blit(boid_count_text, (10, 10))  # Position: (x=10, y=10)
    screen.blit(max_speed_text, (10, 30))
    screen.blit(max_force_text, (10, 50))
    screen.blit(neighbor_radius_text, (10, 70))
    screen.blit(separation_radius_text, (10, 90))
    screen.blit(object_separation_radius_text, (10, 110))
    screen.blit(width_text, (10, 130))
    screen.blit(height_text, (10, 150))
    screen.blit(queens_text, (10, 170))
    screen.blit(larva_text, (10, 190))
    screen.blit(food_text, (10, 210))
    screen.blit(worker_text, (10, 230))
    screen.blit(hatch_worker_text, (10, 250))
    screen.blit(hatch_queen_text, (10, 270))

    return [
        button_add_boids,
        button_remove_boids,
        button_add_speed,
        button_remove_speed,
        button_add_force,
        button_remove_force,
        button_add_neighbor_radius,
        button_remove_neighbor_radius,
        button_add_separation_radius,
        button_remove_separation_radius,
        button_add_object_separation_radius,
        button_remove_object_separation_radius,
        button_hatch_worker,
        button_hatch_queen,
    ]

# Declare mouse_held as a global variable
mouse_held = False
last_add_time = 0  # Initialize outside the function

def manage_UI(buttons, boids, movable_objects):
    global WIDTH, HEIGHT, MAX_SPEED, MAX_FORCE, NEIGHBOR_RADIUS, SEPARATION_RADIUS, OBJECT_SEPERATION_RADIUS, mouse_held, last_add_time, FOOD, LARVA, WORKERS, QUEENS
    dragging_object = False  # Flag to check if an object is being dragged

    button_add_boids = buttons[0]
    button_remove_boids = buttons[1]
    button_add_speed = buttons[2]
    button_remove_speed = buttons[3]
    button_add_force = buttons[4]
    button_remove_force = buttons[5]
    button_add_neighbor_radius = buttons[6]
    button_remove_neighbor_radius = buttons[7]
    button_add_separation_radius = buttons[8]
    button_remove_separation_radius = buttons[9]
    button_add_object_separation_radius = buttons[10]
    button_remove_object_separation_radius = buttons[11]
    button_hatch_worker = buttons[12]
    button_hatch_queen = buttons[13]
    
    dragging = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_held = True
            for obj in movable_objects:
                if (obj.position - pygame.Vector2(event.pos)).length() < obj.size:
                    obj.is_dragging = True
                    dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_held = False
            for obj in movable_objects:
                obj.is_dragging = False
                obj.velocity = pygame.Vector2(0, 0)
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            for obj in movable_objects:
                if obj.is_dragging:
                    obj.position = pygame.Vector2(event.pos)
                    dragging = True

    # Get the current time
    current_time = pygame.time.get_ticks()

    # Check if the mouse is held and throttle actions
    if not dragging and mouse_held and current_time - last_add_time > 50:  # 50ms delay
        mouse_pos = pygame.mouse.get_pos()

        if button_add_boids.collidepoint(mouse_pos):
            new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            boids.append(new_boid)
        elif button_remove_boids.collidepoint(mouse_pos):
            if boids:
                boids.pop()
        elif button_add_speed.collidepoint(mouse_pos):
            MAX_SPEED += 1
        elif button_remove_speed.collidepoint(mouse_pos):
            if MAX_SPEED > 1:
                MAX_SPEED -= 1
        elif button_add_force.collidepoint(mouse_pos):
            MAX_FORCE += 0.1
        elif button_remove_force.collidepoint(mouse_pos):
            if MAX_FORCE > 0.1:
                MAX_FORCE -= 0.1
        elif button_add_neighbor_radius.collidepoint(mouse_pos):
            NEIGHBOR_RADIUS += 10
        elif button_remove_neighbor_radius.collidepoint(mouse_pos):
            if NEIGHBOR_RADIUS > 10:
                NEIGHBOR_RADIUS -= 10
        elif button_add_separation_radius.collidepoint(mouse_pos):
            SEPARATION_RADIUS += 10
        elif button_remove_separation_radius.collidepoint(mouse_pos):
            if SEPARATION_RADIUS > 10:
                SEPARATION_RADIUS -= 10
        elif button_add_object_separation_radius.collidepoint(mouse_pos):
            OBJECT_SEPERATION_RADIUS += 10
        elif button_remove_object_separation_radius.collidepoint(mouse_pos):
            if OBJECT_SEPERATION_RADIUS > 10:
                OBJECT_SEPERATION_RADIUS -= 10
        elif button_hatch_worker.collidepoint(mouse_pos):
            if FOOD >= 10 and LARVA >= 1:
                FOOD -= 10
                LARVA -= 1
                WORKERS += 1
                new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                boids.append(new_boid)
        elif button_hatch_queen.collidepoint(mouse_pos):
            if FOOD >= 500 and LARVA >= 10:
                FOOD -= 500
                LARVA -= 10
                QUEENS += 1
                new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                boids.append(new_boid)

        # Update the last action time
        last_add_time = current_time

    return True

class MovableObject:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.size = 20  # radius for simplicity
        self.mass = 5
        self.is_dragging = False  # Flag to check if the object is being dragged
        self.held_in_goal = False
        self.last_goal_time = None
        self.object_remains_in_goal_time = None  # Flag to check if an object remains in the goal for too long
        #self.last_goal_time = None  # Track when the object was last in the goal

    def update(self, target_position):
        global TARGET_HOLD_TIME
        if not self.is_dragging:
            self.position += self.velocity
            self.velocity *= 0.95  # friction / damping
            if self.position.x <= 0 or self.position.x >= WIDTH:
                self.velocity.x *= -1
                # Clamp inside bounds
                self.position.x = max(0, min(self.position.x, WIDTH))

            if self.position.y <= 0 or self.position.y >= HEIGHT:
                self.velocity.y *= -1
                # Clamp inside bounds
                self.position.y = max(0, min(self.position.y, HEIGHT))
        # NOTE: avoid exact vector equality in float math; treat "in goal" as within a radius
        if self.position.distance_to(target_position) <= 30:  # ~goal radius check instead of equality
            if self.last_goal_time is None:
                self.last_goal_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.last_goal_time > TARGET_HOLD_TIME:
                self.held_in_goal = True
            # self.last_goal_time = pygame.time.get_ticks()  # (not needed each frame once set)
        else:
            self.held_in_goal = False
            self.last_goal_time = None

    def apply_force(self, force):
        if not self.is_dragging:
            self.velocity += force / self.mass

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.position.x), int(self.position.y)), self.size)

class Boid:
    ant_image = None
    ant_image_path = os.path.join(os.path.dirname(__file__), "ant.png")
    def __init__(self, x, y):
        # Initialize position and velocity
        self.position = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)
        self.color = (255, 0, 0)
        self.signal_time = pygame.time.get_ticks()
        self.goal_location = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.has_received = False  # Flag to check if boid has received a message
        # Load ant image once for all boids
        if Boid.ant_image is None:
            try:
                img = pygame.image.load(Boid.ant_image_path).convert_alpha()
                Boid.ant_image = pygame.transform.smoothscale(img, (32, 32))
            except Exception as e:
                print(f"Error loading ant.png: {e}")
                Boid.ant_image = None

    def update(self, blocks, WIDTH, HEIGHT):
        # Update velocity and position
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity
        self.acceleration *= 0
        
        if pygame.time.get_ticks() - self.signal_time > 100:
            self.color = (255, 255, 255)

        # Screen bouncing
        if self.position.x <= 0 or self.position.x >= WIDTH:
            self.velocity.x *= -1
            # Clamp inside bounds
            self.position.x = max(0, min(self.position.x, WIDTH))

        if self.position.y <= 0 or self.position.y >= HEIGHT:
            self.velocity.y *= -1
            # Clamp inside bounds
            self.position.y = max(0, min(self.position.y, HEIGHT))
        
        for block in blocks:
            block_rect = block.get_rect()
            boid_rect = pygame.Rect(self.position.x, self.position.y, 5, 5)  # A small rect for collision
            if boid_rect.colliderect(block_rect):
                # Simple bounce: reverse direction
                # You can get fancier with angle of incidence/reflection later
                if block_rect.left <= self.position.x <= block_rect.right:
                    self.velocity.y *= -1
                if block_rect.top <= self.position.y <= block_rect.bottom:
                    self.velocity.x *= -1

    def apply_force(self, force):
        self.acceleration += force

    def align(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        for boid in boids:
            if boid != self and self.position.distance_to(boid.position) < NEIGHBOR_RADIUS:
                steering += boid.velocity
                total += 1
        if total > 0:
            steering /= total
            # guard normalize on zero-length
            if steering.length() > 0:
                steering = (steering.normalize() * MAX_SPEED) - self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)
        return steering

    def cohesion(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        for boid in boids:
            if boid != self and self.position.distance_to(boid.position) < NEIGHBOR_RADIUS:
                steering += boid.position
                total += 1
        if total > 0:
            steering /= total
            # guard normalize on zero-length
            desired = steering - self.position
            if desired.length() > 0:
                desired = desired.normalize() * MAX_SPEED
                steering = desired - self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)
                return steering
        return pygame.Vector2(0, 0)

    def separation(self, boids, blocks):
        steering = pygame.Vector2(0, 0)
        total = 0
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if boid != self and distance < SEPARATION_RADIUS:
                diff = self.position - boid.position
                if distance != 0:
                    diff /= distance
                steering += diff
                total += 1
        # After self.position += self.velocity
        boid_rect = pygame.Rect(self.position.x, self.position.y, 5, 5)  # A small rect for collision
        
        for block in blocks:
            distance = self.position.distance_to(block.position)
            if distance < OBJECT_SEPERATION_RADIUS:
                diff = self.position - block.position
                if distance != 0:
                    diff /= distance
                steering += diff
                total += 1
            block = block.get_rect()
        
        if total > 0:
            steering /= total
        if steering.length() > 0:
            steering = steering.normalize() * MAX_SPEED - self.velocity
            if steering.length() > MAX_FORCE:
                steering.scale_to_length(MAX_FORCE)
        return steering

    def broadcast(self, boids, blocks, objects, goal_location):
        for boid in boids:
            if boid != self and not boid.has_received and self.position.distance_to(boid.position) < BROADCAST_RADIUS:
                boid.recieve(boids, blocks, objects, goal_location)

    def recieve(self, boids, blocks, objects, goal_location):
        if not self.has_received:
            self.has_received = True
            self.color = (0, 255, 0)
            self.broadcast(boids, blocks, objects, goal_location)
            self.goal_location = goal_location
            self.signal_time = pygame.time.get_ticks()
            self.attract_to_object(boids, blocks, objects, goal_location)
            self.apply_force(self.move_to_location(self.goal_location))
            self.flock(boids, blocks, objects, self.goal_location)

    def scatter(self, boids, blocks, objects, target_position):
        self.apply_force(pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * MAX_FORCE)
        self.push_object(objects, target_position)
        self.apply_force(self.attract_to_object(boids, blocks, objects, target_position))

    def push_object(self, objects, goal):
        for obj in objects:
            to_object = obj.position - self.position
            if to_object.length() < 30:
                # Modify this section in swarm-soccer.py
                if (goal - obj.position).length() != 0:
                    push_dir = (goal - obj.position).normalize()
                else:
                    push_dir = pygame.Vector2(0, 0)  # Fixed: Use pygame.Vector2 instead of Vector2
                force = push_dir * OBJECT_PUSH_FORCE
                obj.apply_force(force)
    
    def move_to_location(self, location):
        # guard normalize on zero-length
        direction = (location - self.position)
        if direction.length() > 0:
            direction = direction.normalize()
            steer = direction * MAX_SPEED - self.velocity
            if steer.length() > MAX_FORCE:
                steer.scale_to_length(MAX_FORCE)
            return steer
        return pygame.Vector2(0, 0)

    def attract_to_object(self, boids, blocks, objects, target_position):
        closest_object = None
        min_distance = float('inf')

        # Find the closest object
        for obj in objects:
            # Check if the object is in the goal
            if obj.position.distance_to(target_position) < 30:
                if obj.object_remains_in_goal_time is None:
                    #print(f"None")
                    obj.object_remains_in_goal_time = pygame.time.get_ticks()
                    print("Object entered the goal")
                elif pygame.time.get_ticks() - obj.object_remains_in_goal_time > 7000:
                    print(f"Skipping object {obj.position} because it remains in the goal for too long")
                    continue  # Permanently skip this object

            distance = self.position.distance_to(obj.position)
            if distance < min_distance:
                min_distance = distance
                closest_object = obj

        # If a closest object is found and within the attraction radius
        if closest_object and min_distance < ATTRACTION_RADIUS:
            self.broadcast(boids, blocks, objects, closest_object.position)
            return self.move_to_location(closest_object.position)

        return pygame.Vector2(0, 0)

    def resolve_collision_with_ball(self, objects):
        for ball in objects:
            distance = self.position.distance_to(ball.position)
            overlap = ball.size + 5 - distance  # 5 is boid "radius"

            if overlap > 0:
                # Push boid away from ball
                push_dir = (self.position - ball.position).normalize()
                self.position += push_dir * overlap  # move boid out
                self.velocity.reflect_ip(push_dir)  # reflect direction

                # Optional: also apply a force to the ball (Newton's Third Law)
                ball.apply_force(-push_dir * 0.5)  # tweak force amount


    def flock(self, boids, blocks, objects, target_position):
        # Apply the three main forces
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids, blocks)

        # Weigh the forces
        self.apply_force(alignment * 1.0)
        self.apply_force(cohesion * 1.0)
        self.apply_force(separation * 1.5)

    def draw(self, screen):
        # Draw the ant sprite, rotated to match velocity direction
        if Boid.ant_image:
            angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x)) - 90
            rotated = pygame.transform.rotate(Boid.ant_image, angle)
            rect = rotated.get_rect(center=(self.position.x, self.position.y))
            screen.blit(rotated, rect)
        else:
            # fallback: draw a red circle
            pygame.draw.circle(screen, (255,0,0), (int(self.position.x), int(self.position.y)), 8)

# ---- async pygbag entrypoint ----
async def main():
    global NUM_BOIDS, MAX_SPEED, MAX_FORCE, NEIGHBOR_RADIUS, SEPARATION_RADIUS, WIDTH, HEIGHT, OBJECT_SEPERATION_RADIUS, OBJECTS_IN_GOAL, LARVA, QUEENS, FOOD
    pygame.init()
    try:
        import pygame
        pygame.mixer.quit()
    except Exception:
        pass
    # Use SCALED for browser-friendly scaling; RESIZABLE kept off for stability in wasm
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)  # No RESIZABLE
    pygame.display.set_caption("Swarm Simulation")
    clock = pygame.time.Clock()
    last_add_time = pygame.time.get_ticks()
    init_goal_time = pygame.time.get_ticks()

    # Create boids
    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]
    movable_object_1 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    movable_object_2 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    movable_object_3 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))

    objects = [movable_object_1, movable_object_2, movable_object_3]
    blocks = []

    # Target position
    target_position = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    target_radius = 40

    one_second_ticker = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill((0, 100, 0))  # RGB for dark green
        
        # Draw a black filled circle in the middle of the screen as the base
        base_center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        base_radius = 40
        pygame.draw.circle(screen, (0, 0, 0), (int(base_center.x), int(base_center.y)), base_radius)  # filled black # Draw base
        
        buttons = render_UI(screen, boids)
        running = manage_UI(buttons, boids, objects)

        # Update and draw boids
        for boid in boids:
            boid.scatter(boids, blocks, objects, target_position)
            boid.update(blocks, WIDTH, HEIGHT)
            boid.resolve_collision_with_ball(objects)
            boid.draw(screen)
            boid.has_received = False  # Reset the flag after each update
        
        for block in blocks:
            block.draw(screen)
        
        for obj in objects:
            obj.update(target_position)
            obj.draw(screen)
        
        now = pygame.time.get_ticks()
        if now - one_second_ticker >= 1000:
            LARVA += QUEENS*2 # Each queen produces 2 larva per second
            FOOD += WORKERS # Each worker brings in 1 food per second
            one_second_ticker = now
    
        pygame.display.flip()
        clock.tick(30)

        # CRUCIAL for pygbag/browser: yield each frame
        await asyncio.sleep(0)

    pygame.quit()

async def _run():
    try:
        await main()
    except Exception:
        import traceback
        traceback.print_exc()  # will show a red Python traceback in the browser console
        raise

if __name__ == "__main__":
    asyncio.run(_run()) #asyncio.run(main())
