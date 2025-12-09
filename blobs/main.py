import pygame
import math
import random
from array import array

import moderngl

# pygame setup
pygame.init()
screen_buffer = pygame.Surface((1280, 720))
lines_buffer = pygame.Surface((1280, 720))
screen = pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
running = True

# moderngl stuff

ctx = moderngl.create_context()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]))

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;
uniform float time;
uniform float width;
uniform float height;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec2 pixelSize = vec2(1.0/ width, 1.0 / height);
    
    float lsum = 0;
    float rsum = 0;
    float usum = 0;
    float dsum = 0;

    vec4 one = vec4(1.0, 1.0, 1.0, 1.0);

    lsum += dot(one, texture(tex, uvs + vec2(-1, -1) * pixelSize)) * -1;
    lsum += dot(one, texture(tex, uvs + vec2(-1,  0) * pixelSize)) * -2;
    lsum += dot(one, texture(tex, uvs + vec2(-1,  1) * pixelSize)) * -1;

    rsum += dot(one, texture(tex, uvs + vec2( 1, -1) * pixelSize)) *  1;
    rsum += dot(one, texture(tex, uvs + vec2( 1,  0) * pixelSize)) *  2;
    rsum += dot(one, texture(tex, uvs + vec2( 1,  1) * pixelSize)) *  1;

    usum += dot(one, texture(tex, uvs + vec2(-1, -1) * pixelSize)) * -1;
    usum += dot(one, texture(tex, uvs + vec2( 0, -1) * pixelSize)) * -2;
    usum += dot(one, texture(tex, uvs + vec2( 1, -1) * pixelSize)) * -1;

    dsum += dot(one, texture(tex, uvs + vec2(-1,  1) * pixelSize)) *  1;
    dsum += dot(one, texture(tex, uvs + vec2( 0,  1) * pixelSize)) *  2;
    dsum += dot(one, texture(tex, uvs + vec2( 1,  1) * pixelSize)) *  1;

    float sobel = sqrt(abs(rsum + lsum) + abs(usum + dsum));
    sobel = step(0.8, sobel);

    f_color = vec4(sobel, sobel, sobel, 1.0);
}

'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

# Simulation parameters
min_distance = 10 # min distance between attractor and fluid particles
particle_size = 20 # radius of particle size
particle_repel_range = 20 # The range in which particles repel
minimum_movement_magnitude = 0.15 # The minimum magnitude required to be added to a particle's velocity
movement_multiplier = 0.125 # The amount the particles movement is multiplied by before being added
velocity_falloff_rate = 0.75 # velocity falls off at this rate
max_particle_size = 30



def distance_between(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

class Attractor:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.particle_size = 0
        self.particles = []
        self.max_particle_size = max_particle_size + random.randint(-10, 10)
        return

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.particle_size < self.max_particle_size : self.particle_size += 0.5

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

        if (movement.magnitude() * movement_multiplier) > minimum_movement_magnitude:
            self.velocity += movement * movement_multiplier

        self.velocity *= velocity_falloff_rate

        self.x += self.velocity.x * 0.5
        self.y += self.velocity.y * 0.5

        return


ticks = 0
simulation = [Attractor(512, 512, 0.001, 0.2)]

for i in range(15):
    att = simulation[0]
    simulation[0].particles.append(FluidParticle(
        att.x + random.randint(-200, 200),
        att.y + random.randint(-200, 200),
        att
        ))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen_buffer with a color to wipe away anything from last frame
    screen_buffer.fill("black")

    # RENDER YOUR GAME HERE

    for attractor in simulation:
        attractor.move()
        for fp in attractor.particles:
            fp.move()
            pygame.draw.circle(screen_buffer, "white", (fp.x, fp.y), attractor.particle_size)

    # Add new things
    if ticks % 60 == 0:
        # Create attractor
        simulation.append(Attractor(
            screen_buffer.get_width() // 2 + random.randint(-200, 200), screen_buffer.get_height() // 2 + random.randint(-200, 200),
            random.randint(-10, 10) * 0.1,
            random.randint(-10, 10) * 0.1,
            ))
        # Create particles 
        for i in range(random.randint(3, 50)):
            att = simulation[-1]
            simulation[-1].particles.append(FluidParticle(
                att.x + random.randint(-200, 200),
                att.y + random.randint(-200, 200),
                att
                ))

        # Remove the particles 
        
        j = 0
        while j < len(simulation):
            if screen_buffer.get_width() * 2 < simulation[j].x or simulation[j].x < screen_buffer.get_width() * -2:
                del simulation[j]
                print("removed")
            elif screen_buffer.get_height() * 2 < simulation[j].y or simulation[j].y < screen_buffer.get_height() * -2:
                del simulation[j]
                print("removed")
            else:
                j += 1

    ticks += 1

    frame_tex = surf_to_texture(screen_buffer)
    frame_tex.use(0)
    program['tex'] = 0
    program['width'] = screen_buffer.get_width()
    program['height'] = screen_buffer.get_height()


    render_object.render(mode=moderngl.TRIANGLE_STRIP)


            
    # flip() the display to put your work on screen_buffer
    pygame.display.flip()

    frame_tex.release()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
