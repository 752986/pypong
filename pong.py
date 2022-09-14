import pygame
from pygame.rect import Rect
from pygame.math import Vector2

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class GameObject:
    pos: Vector2

    def __init__(self, pos: Vector2):
        self.pos = pos

    def update(self, delta: float):
        pass

    def draw(self):
        pass

class Ball(GameObject):
    vel: Vector2
    bounds: Rect

    def __init__(self, pos: Vector2, vel: Vector2 = Vector2(0, 0), size: float = 20):
        super().__init__(pos)
        self.vel = vel
        self.bounds = Rect(pos, (size, size))

    def update(self, delta: float):
        self.pos += self.vel * delta
        self.bounds.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), self.bounds.center, self.bounds.width / 2)


gameobjects: list[GameObject] = [
    Ball(Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), Vector2(100, -50))
]


# main loop
running = True
prevtime = 0
while running:
    # find time in seconds since last frame
    delta = (pygame.time.get_ticks() - prevtime) / 1000
    prevtime = pygame.time.get_ticks()

    # input:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # process:
    for obj in gameobjects:
        obj.update(delta)

    # draw:
    screen.fill((0, 0, 0))
    for obj in gameobjects:
        obj.draw()

    pygame.display.flip()

pygame.quit()