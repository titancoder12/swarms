import pygame
import random
import math

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
# Boid settings
NUM_BOIDS = 0
MAX_SPEED = 10
MAX_FORCE = 1
NEIGHBOR_RADIUS = 200
SEPARATION_RADIUS = 30

class Block:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.color = (255, 255, 255)  # White color for the block
        self.size = 20  # Size of the block

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.position.x, self.position.y, self.size, self.size))

class Boid:
    def __init__(self, x, y):
        # Initialize position and velocity
        self.position = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)
        self.color = (255, 0, 0)
        spwan_time = pygame.time.get_ticks()
        self.spawn_time = spwan_time 

    def update(self):
        # Update velocity and position
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity
        self.acceleration *= 0
        
        if pygame.time.get_ticks() - self.spawn_time > 100:
            self.color = (255, 255, 255)

        # Screen wrapping
        # Screen bouncing
        if self.position.x <= 0 or self.position.x >= WIDTH:
            self.velocity.x *= -1
            # Clamp inside bounds
            self.position.x = max(0, min(self.position.x, WIDTH))

        if self.position.y <= 0 or self.position.y >= HEIGHT:
            self.velocity.y *= -1
            # Clamp inside bounds
            self.position.y = max(0, min(self.position.y, HEIGHT))


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
        
        for block in blocks:
            distance = self.position.distance_to(block.position)
            if distance < SEPARATION_RADIUS:
                diff = self.position - block.position
                if distance != 0:
                    diff /= distance
                steering += diff
                total += 1
        
        if total > 0:
            steering /= total
        if steering.length() > 0:
            steering = steering.normalize() * MAX_SPEED - self.velocity
            if steering.length() > MAX_FORCE:
                steering.scale_to_length(MAX_FORCE)
        return steering

    def flock(self, boids, blocks):
        # Apply the three main forces
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids, blocks)

        # Weigh the forces
        self.apply_force(alignment * 1.0)
        self.apply_force(cohesion * 1.0)
        self.apply_force(separation * 1.5)


    def draw(self, screen):
        # Draw a simple triangle for the boid
        angle = math.atan2(self.velocity.y, self.velocity.x)
        points = [
            self.position + pygame.Vector2(math.cos(angle) * 10, math.sin(angle) * 10),
            self.position + pygame.Vector2(math.cos(angle + 2.5) * 10, math.sin(angle + 2.5) * 10),
            self.position + pygame.Vector2(math.cos(angle - 2.5) * 10, math.sin(angle - 2.5) * 10),
        ]
        #bird_points = [
        #    (400, 300),  # Beak (front)
        #    (420, 320),  # Bottom wing tip
        #    (400, 340),  # Tail
        #    (380, 320),  # Top wing tip
        #]
        pygame.draw.polygon(screen, self.color, points)

def main():
    pygame.init()
    font = pygame.font.SysFont(None, 30)  # You can change font size or type
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Swarm Simulation")
    clock = pygame.time.Clock()

    # Create boids
    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]
    blocks = []

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background

        button_add = pygame.Rect(10, 30, 100, 30)  # Button to add boids
        button_remove = pygame.Rect(120, 30, 100, 30)  # Button to remove boids
        
        pygame.draw.rect(screen, (255, 255, 255), button_add)
        pygame.draw.rect(screen, (255, 255, 255), button_remove)

        plus_text = font.render("+", True, (0, 0 , 0))  # Black text for plus button
        minus_text = font.render("-", True, (0, 0, 0))  # Black text for minus button

        plus_rect = plus_text.get_rect(center=button_add.center)
        minus_rect = minus_text.get_rect(center=button_remove.center)

        screen.blit(plus_text, plus_rect)
        screen.blit(minus_text, minus_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                boids.append(new_boid)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if button_add.collidepoint(event.pos):
                    new_boid = Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT))
                    boids.append(new_boid)

                elif button_remove.collidepoint(event.pos):
                    if boids:
                        boids.pop()
                
                else:
                    Block(event.pos[0], event.pos[1]).draw(screen)
                    blocks.append(Block(event.pos[0], event.pos[1]))
        
        # Update and draw boids
        for boid in boids:
            boid.flock(boids, blocks)
            boid.update()
            boid.draw(screen)
        
        for block in blocks:
            block.draw(screen)

        # Display the number of boids
        # Render the text
        boid_count_text = font.render(f"Birds: {len(boids)}", True, (255, 255, 255))  # White text

        # Draw it on screen at top-left
        screen.blit(boid_count_text, (10, 10))  # Position: (x=10, y=10)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()