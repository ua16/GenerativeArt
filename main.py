import pygame
import math
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


# Simulation parameters
min_distance = 10 # min distance between attractor and fluid particles
particle_size = 20 # radius of particle size
particle_repel_range = 20

def distance_between(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

class Attractor:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.particles = []
        return
    def move(self):
        self.x += self.dx
        self.y += self.dy

    def getVector(self):
        return pygame.Vector2(self.x, self.y)

    
# Fluid particles move towards the attractor up until a certain point
# So move towards attractor until at a minimum distance to it
# Then move with the attractor


class FluidParticle:
    def __init__(self, x, y, attractor):
        self.x = x
        self.y = y
        self.attractor = attractor
        self.velocity = pygame.Vector2()
        return

    def move(self):
        # let's have weighted vectors for each 
        # one for the others
        # also have a spring that connects to the avg position

        ax = sum(p.x for p in self.attractor.particles) / len(self.attractor.particles)
        ay = sum(p.y for p in self.attractor.particles) / len(self.attractor.particles)
        
        movement = pygame.Vector2()

        for p in self.attractor.particles:
            if distance_between(self.x, self.y, p.x, p.y) < particle_repel_range:
                movement += pygame.Vector2(self.x - p.x, self.y - p.y) / 10
        attractor_distance = distance_between(self.x, self.y, self.attractor.x, self.attractor.y)
        if 20 < attractor_distance:
            movement += (self.attractor.getVector() - pygame.Vector2(self.x, self.y)) / 20

        # repel if it's close

        if movement.magnitude() * 0.125 > 0.15:
            self.velocity += movement * 0.125

        self.velocity *= 0.75

        self.x += self.velocity.x * 0.5
        self.y += self.velocity.y * 0.5

        return


simulation = [Attractor(512, 512, 0.001, 0.2)]

for i in range(15):
    att = simulation[0]
    simulation[0].particles.append(FluidParticle(
        att.x + random.randint(-500, 500),
        att.y + random.randint(-500, 500),
        att
        ))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE

    pygame.draw.circle(screen, "yellow", (512, 512), 5)

    for attractor in simulation:
        attractor.move()
        pygame.draw.circle(screen, "red", (attractor.x, attractor.y), 5)
        for fp in attractor.particles:
            fp.move()
            pygame.draw.circle(screen, "white", (fp.x, fp.y), 2)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
