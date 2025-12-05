from re import fullmatch
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

    
# Fluid particles move towards the attractor up until a certain point
# So move towards attractor until at a minimum distance to it
# Then move with the attractor


class FluidParticle:
    def __init__(self, x, y, attractor):
        self.x = x
        self.y = y
        self.attractor = attractor
        return

    def move(self):
        if distance_between(self.x, self.y, self.attractor.x, self.attractor.y) > min_distance:
            # move towards attractor, [TODO]
            self.x += (self.attractor.x - self.x) / 10
            self.y += (self.attractor.y - self.y) / 10
        else:
            # move with attractor
            self.x += self.attractor.dx
            self.y += self.attractor.dy
        return


simulation = [Attractor(512, 512, 2, 1)]

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
