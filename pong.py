import pygame
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.color import Color
from pygame import font
import math
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
    _paddle_bounce = True
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
            if self._paddle_bounce and isinstance(o, Paddle) and self.bounds.colliderect(o.bounds): # only bounce once, otherwise it could get stuck in the paddle
                self.vel.x *= -1
                self.vel.y += o.dy * 0.5
                self._paddle_bounce = False
            else:
                self._paddle_bounce = True

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
    LEFT = False
    RIGHT = True

    bounds: Rect
    facing: bool
    dy: float = 0.0

    _py: float

    def __init__(self, pos: Vector2, color: Color = Color(255, 255, 255), size: float = 150):
        super().__init__(pos, color)
        self.base_color = color
        self.facing = Paddle.RIGHT if pos.x < SCREEN_WIDTH / 2 else Paddle.LEFT
        self.bounds = Rect(pos, (6, size))
        self._py = pos.y

    def move(self, amnt: float, delta: float = 1):
        self.pos.y += amnt * delta

    def update(self, delta: float):
        self.pos.y = max(min(self.pos.y, SCREEN_HEIGHT), 0)
        # position is updated from input handling
        self.bounds.center = (int(self.pos.x), int(self.pos.y))

        # calculate vertical velocity (dy)
        self.dy = lerp((self.pos.y - self._py) / delta, self.dy, 0.9)
        self._py = self.pos.y

    def draw(self):
        offset = round(self.dy * 0.005, 1) * (1 if self.facing == Paddle.LEFT else -1)
        pygame.draw.line(screen, self.color, (self.bounds.centerx - offset, self.bounds.top), (self.bounds.centerx + offset, self.bounds.bottom), 6)
        

# initialize game:
PLAYER_SPEED = 1200.0

game_font = font.SysFont(["consolas", ""], 48)

bgcolor = Color(10, 15, 20)

pygame.mouse.set_visible(False)

p1 = Paddle(Vector2(50, SCREEN_HEIGHT / 2), Color(176, 255, 54))
p2 = Paddle(Vector2(SCREEN_WIDTH - 50, SCREEN_HEIGHT / 2), Color(255, 58, 100))
gameobjects: list[GameObject] = [
    p1,
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
            if event.axis == pygame.CONTROLLER_AXIS_LEFTY:
                print(event.value)
    
    keys = pygame.key.get_pressed()
    # player 1 movement
    if keys[pygame.K_w]:
        p1.move(-PLAYER_SPEED, delta)
    if keys[pygame.K_s]:
        p1.move(PLAYER_SPEED, delta)
    # player 2 movement
    if keys[pygame.K_UP]:
        p2.move(-PLAYER_SPEED, delta)
    if keys[pygame.K_DOWN]:
        p2.move(PLAYER_SPEED, delta)
    
    # process:
    for obj in gameobjects:
        obj.update(delta)
    #p2.pos = Vector2(p2.pos.x, pygame.mouse.get_pos()[1])

    # draw:
    screen.fill(bgcolor)
    for obj in gameobjects:
        obj.draw()
    #text = game_font.render("07", True, Color(255, 255, 255))
    #screen.blit(text, (300, 100))

    pygame.display.flip()

pygame.quit()