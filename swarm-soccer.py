import pygame
import random
import math

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
# Boid settings
NUM_BOIDS = 0
MAX_SPEED = 10
MAX_FORCE = 1
OBJECT_PUSH_FORCE = 0.2
NEIGHBOR_RADIUS = 200
SEPARATION_RADIUS = 30
OBJECT_SEPERATION_RADIUS = 50
TRIANGLE_SIZE = 5
ATTRACTION_RADIUS = 100
OBJECTS_IN_GOAL = False  # Flag to check if all objects are in the goal
BROADCAST_RADIUS = 300

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

    boid_count_text = font.render(f"Boids: {len(boids)}", True, (255, 255, 255))  # White text
    max_speed_text = font.render(f"Max Speed: {MAX_SPEED}", True, (255, 255, 255))
    max_force_text = font.render(f"Max Force: {round(MAX_FORCE, 2)}", True, (255, 255, 255))
    neighbor_radius_text = font.render(f"Neighbor Radius: {NEIGHBOR_RADIUS}", True, (255, 255, 255))
    separation_radius_text = font.render(f"Separation Radius: {SEPARATION_RADIUS}", True, (255, 255, 255))
    width_text = font.render(f"Window Width: {WIDTH}", True, (255, 255, 255))
    height_text = font.render(f"Window Height: {HEIGHT}", True, (255, 255, 255))
    object_separation_radius_text = font.render(f"Object Separation: {OBJECT_SEPERATION_RADIUS}", True, (255, 255, 255))

    # Draw it on screen at top-left
    screen.blit(boid_count_text, (10, 10))  # Position: (x=10, y=10)
    screen.blit(max_speed_text, (10, 30))
    screen.blit(max_force_text, (10, 50))
    screen.blit(neighbor_radius_text, (10, 70))
    screen.blit(separation_radius_text, (10, 90))
    screen.blit(object_separation_radius_text, (10, 110))
    screen.blit(width_text, (10, 130))
    screen.blit(height_text, (10, 150))

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
        button_remove_object_separation_radius
    ]

# Declare mouse_held as a global variable
mouse_held = False
last_add_time = 0  # Initialize outside the function

def manage_UI(buttons, boids, movable_objects):
    global WIDTH, HEIGHT, MAX_SPEED, MAX_FORCE, NEIGHBOR_RADIUS, SEPARATION_RADIUS, OBJECT_SEPERATION_RADIUS, mouse_held, last_add_time
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

    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         return False
    #     if event.type == pygame.VIDEORESIZE:
    #         WIDTH, HEIGHT = event.w, event.h
    #     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
    #         mouse_held = True
    #     elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
    #         mouse_held = False
    #         dragging_object = False  # Stop dragging when mouse button is released
    #     for movable_object in movable_objects:
    #         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #             if (movable_object.position - pygame.Vector2(event.pos)).length() < movable_object.size:
    #                 dragging_object = True
    #         elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
    #             dragging_object = False
    #             movable_object.velocity = pygame.Vector2(0, 0)  # Stop the object when mouse is released
    #         elif event.type == pygame.MOUSEMOTION and dragging_object:
    #             # Move the object with the mouse
    #             movable_object.position = pygame.Vector2(event.pos)
    
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

    def update(self):
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

    def apply_force(self, force):
        if not self.is_dragging:
            self.velocity += force / self.mass

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), self.position, self.size)

class Boid:
    def __init__(self, x, y):
        # Initialize position and velocity
        self.position = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)
        self.color = (255, 0, 0)
        self.signal_time = pygame.time.get_ticks()
        self.goal_location = ()
        self.has_received = False  # Flag to check if boid has received a message

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
            steering = (steering - self.position).normalize() * MAX_SPEED - self.velocity
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
                push_dir = (goal - obj.position).normalize()
                force = push_dir * OBJECT_PUSH_FORCE
                obj.apply_force(force)
    
    def move_to_location(self, location):
        direction = (location - self.position).normalize()
        steer = direction * MAX_SPEED - self.velocity
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def attract_to_object(self, boids, blocks, objects, target_position):
        closest_object = None
        min_distance = float('inf')

        # Find the closest object
        for obj in objects:
            # Check if the object is in the goal
            if obj.position.distance_to(target_position) < 30:
                continue  # Skip objects already in the goal

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
        
        #self.push_object(objects, target_position)
        #self.apply_force(self.attract_to_object(boids, objects, target_position))


    def draw(self, screen):
        # Draw a simple triangle for the boid
        angle = math.atan2(self.velocity.y, self.velocity.x)
        points = [
            self.position + pygame.Vector2(math.cos(angle) * TRIANGLE_SIZE, math.sin(angle) * TRIANGLE_SIZE),
            self.position + pygame.Vector2(math.cos(angle + 2.5) * TRIANGLE_SIZE, math.sin(angle + 2.5) * TRIANGLE_SIZE),
            self.position + pygame.Vector2(math.cos(angle - 2.5) * TRIANGLE_SIZE, math.sin(angle - 2.5) * TRIANGLE_SIZE),
        ]

        pygame.draw.polygon(screen, self.color, points)

def main():
    global NUM_BOIDS, MAX_SPEED, MAX_FORCE, NEIGHBOR_RADIUS, SEPARATION_RADIUS, WIDTH, HEIGHT, OBJECT_SEPERATION_RADIUS, OBJECTS_IN_GOAL
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Swarm Simulation")
    clock = pygame.time.Clock()
    last_add_time = pygame.time.get_ticks()

    # Create boids
    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]
    movable_object_1 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    movable_object_2 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    movable_object_3 = MovableObject(random.randint(0, WIDTH), random.randint(0, HEIGHT))

    objects = [movable_object_1, movable_object_2, movable_object_3]
    blocks = []

    # Target position and radius for the movable object
    target_position = pygame.Vector2(WIDTH - 100, HEIGHT - 100)
    target_radius = 40

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background
        pygame.draw.circle(screen, (0, 255, 0), target_position, target_radius, 3)  # Draw target circle
        
        buttons = render_UI(screen, boids)
        running = manage_UI(buttons, boids, objects)

        # Update and draw boids
        for boid in boids:
            #boid.flock(boids, blocks, objects, target_position)
            boid.scatter(boids, blocks, objects, target_position)
            boid.update(blocks, WIDTH, HEIGHT)
            boid.resolve_collision_with_ball(objects)
            boid.draw(screen)
            boid.has_received = False  # Reset the flag after each update
        
        for block in blocks:
            block.draw(screen)
        
        for object in objects:
            object.update()
            object.draw(screen)
        
        truths = []
        for object in objects:
            if object.position.distance_to(target_position) < target_radius:
                truths.append(True)
            else:
                truths.append(False)
        if truths == [True, True, True]:
            pygame.draw.circle(screen, (0, 255, 0), target_position, target_radius)
            OBJECTS_IN_GOAL = True  # filled goal
            # Maybe show text: “Success!”
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()