import pygame
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.color import Color
from pygame import font
import random

pygame.init()

FPS = 60
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong!")


def lerp(a: float, b: float, t: float):
    return (1 - t) * a + t * b


class GameObject:
    pos: Vector2
    color: Color

    def __init__(self, pos: Vector2, color: Color):
        self.pos = pos
        self.color = color

    def update(self, delta: float):
        pass

    def draw(self):
        pass


class Ball(GameObject):
    vel: Vector2
    bounds: Rect

    _can_bounce = True
    _hue: float

    def __init__(self, pos: Vector2, vel: Vector2 = Vector2(0, 0), color: Color = Color(255, 255, 255), size: float = 15):
        super().__init__(pos, color)
        self._hue = color.hsla[0]
        self.vel = vel
        self.bounds = Rect(pos, (size, size))

    def update(self, delta: float):
        # bounce off of wall:
        if self._can_bounce: # only bounce once, otherwise it could get stuck in the wall
            if self.bounds.left < 0 or self.bounds.right > SCREEN_WIDTH:
                self.vel.x *= -1
                self._can_bounce = False
            if self.bounds.top < 0 or self.bounds.bottom > SCREEN_HEIGHT:
                self.vel.y *= -0.95 # slowly decay vertical motion, so it doesn't get out of hand
                self._can_bounce = False

        # bounce off of paddles:
        for o in gameobjects:
            if isinstance(o, Paddle):
                if self._can_bounce: # only bounce once, otherwise it could get stuck in the paddle
                    if self.bounds.colliderect(o.bounds):
                        self.vel.x *= -1
                        self.vel.y += o.dy * 0.5
                        self._can_bounce = False

        # update position
        self.pos += self.vel * delta
        self.bounds.topleft = (int(self.pos.x), int(self.pos.y))

        if screen.get_clip().contains(self.bounds):
            self._can_bounce = True

    def draw(self):
        self._hue = (self._hue + 0.1) % 360
        self.color.hsla = (self._hue, self.color.hsla[1], self.color.hsla[2], self.color.hsla[3])
        pygame.draw.circle(screen, self.color, self.bounds.center, self.bounds.width / 2) 


class Paddle(GameObject):
    bounds: Rect
    base_color: Color
    player_color: Color
    dy: float = 0.0

    _py: float

    def __init__(self, pos: Vector2, color: Color = Color(255, 255, 255), color2: Color = Color(255, 255, 255), size: float = 150):
        super().__init__(pos, color)
        self.base_color = color
        self.player_color = color2
        self.bounds = Rect(pos, (6, size))
        self.py = pos.y

    def update(self, delta: float):
        # position is updated from input handling
        self.bounds.topleft = (int(self.pos.x), int(self.pos.y))

        # calculate vertical velocity (dy)
        self.dy = lerp((self.pos.y - self.py) / delta, self.dy, 0.9)
        self.py = self.pos.y

    def draw(self):
        pygame.draw.line(screen, self.color, (self.bounds.centerx, self.bounds.top), (self.bounds.centerx, self.bounds.bottom), 6)
        

# initialize game:
game_font = font.Font("C:\\Users\\cheet\\AppData\\Local\\Microsoft\\Windows\\Fonts\\RobotoMono-Light.ttf", 64)

pygame.mouse.set_visible(False)

p2 = Paddle(Vector2(SCREEN_WIDTH - 50, 200), Color(255, 58, 100), Color(255, 58, 100))# Color(255, 100, 200))
gameobjects: list[GameObject] = [
    p2,
    Ball(Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), Vector2(1000, 0), Color(150, 255, 255))
]

# main loop
running = True
prevtime = 0
while running:
    # find time in seconds since last frame
    delta = (pygame.time.get_ticks() - prevtime) / 1000
    prevtime = pygame.time.get_ticks()

    pygame.time.delay(int(1000 / FPS ))

    # input:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYAXISMOTION:
            print("aaa")
            if event.axis == pygame.CONTROLLER_AXIS_LEFTY:
                print(event.value)
    
    # process:
    for obj in gameobjects:
        obj.update(delta)
    p2.pos = Vector2(p2.pos.x, pygame.mouse.get_pos()[1])

    # draw:
    screen.fill((10, 15, 20))
    for obj in gameobjects:
        obj.draw()
    text = game_font.render("07", True, Color(255, 255, 255))
    screen.blit(text, (300, 100))

    pygame.display.flip()

pygame.quit()