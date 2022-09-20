from ctypes import RTLD_GLOBAL
import pygame
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.color import Color
from pygame import font
import math
import random

pygame.init()

FPS = 240
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 960
MAX_POINTS = 1
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

    def draw(self, delta: float):
        pass


class Ball(GameObject):
    vel: Vector2
    bounds: Rect

    _can_bounce = True
    _paddle_bounce = True
    _hue: float
    _sleep: float = 0.0

    def __init__(self, pos: Vector2, vel: Vector2 = Vector2(0, 0), color: Color = Color(255, 255, 255), size: float = 15):
        super().__init__(pos, color)
        self._hue = color.hsla[0]
        self.vel = vel
        self.bounds = Rect(pos, (size, size))
        self._reset(random.choice([Paddle.LEFT, Paddle.RIGHT]))

    def _reset(self, dir: int):
        self.pos = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        xval = abs(self.vel.x)
        self.vel.y = random.randint(int(-xval), int(xval))
        self.vel.x = xval * (-1 if dir == Paddle.LEFT else 1) * 1.05

        self._sleep = 1.5

    def update(self, delta: float):
        if self._sleep > 0.0:
            self._sleep -= delta
            pygame.draw.line(screen, self.color, self.pos, self.pos + (self.vel))
            return

        # bounce off of wall:
        if self._can_bounce: # only bounce once, otherwise it could get stuck in the wall
            # if self.bounds.left < 0 or self.bounds.right > SCREEN_WIDTH:
            #     self.vel.x *= -1
            #     self._can_bounce = False
            if self.bounds.left < 0:
                score(2)
                self._reset(Paddle.RIGHT)
            if self.bounds.right > SCREEN_WIDTH:
                score(1)
                self._reset(Paddle.LEFT)
            if self.bounds.top < 0 or self.bounds.bottom > SCREEN_HEIGHT:
                self.vel.y *= -0.6 # slowly decay vertical motion, so it doesn't get out of hand
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

    def draw(self, delta: float):
        if self._sleep > 0.0:
            normvel = self.vel.normalize()
            pygame.draw.line(screen, self.color, Vector2(self.bounds.center) + (normvel * 15), Vector2(self.bounds.center) + (normvel * 20), 3)

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
        self.bounds = Rect(pos, (16, size))
        self._py = pos.y

    def move(self, amnt: float, delta):
        self.pos.y += amnt * delta

    def update(self, delta: float):
        self.pos.y = max(min(self.pos.y, SCREEN_HEIGHT), 0)
        # position is updated from input handling
        self.bounds.center = (int(self.pos.x), int(self.pos.y))

        # calculate vertical velocity (dy)
        self.dy = lerp((self.pos.y - self._py) / delta, self.dy, 0.9)
        self._py = self.pos.y

    def draw(self, delta: float):
        offset = round(self.dy * 0.005, 1) * (1 if self.facing == Paddle.LEFT else -1)
        pygame.draw.line(screen, self.color, (self.bounds.centerx - offset, self.bounds.top), (self.bounds.centerx + offset, self.bounds.bottom), 6)
        

class Score(GameObject):
    score: int = 0

    _time: float = 0.0

    def __init__(self, pos: Vector2, color: Color):
        super().__init__(pos, color)

    def update(self, delta: float):
        pass

    def draw(self, delta: float):
        self._time += delta * 0.3

        string = str(self.score)
        if len(string) == 1:
            string = "0" + string

        text = game_font.render(string, True, Color(255, 255, 255))
        screen.blit(text, self.pos + Vector2(-26, -22))

        d1 = 40
        d2 = d1 + 10

        for i in range(self.score):
            angle = (i / self.score) * math.tau + self._time
            p1 = Vector2(math.cos(angle) * d1, math.sin(angle) * d1)
            p2 = Vector2(math.cos(angle) * d2, math.sin(angle) * d2)
            pygame.draw.line(screen, self.color, p1 + self.pos, p2 + self.pos, 3)


class Victory(GameObject):
    color1: Color
    color2: Color
    text: str
    _hue: float = 0

    def __init__(self, text: str, pos: Vector2, color: Color, color1: Color = Color(100, 210, 240), color2: Color = Color(10, 15, 20)):
        super().__init__(pos, color)
        self.color1 = color1
        self.color2 = color2
        self.text = text

    def update(self, delta):
        pass

    def draw(self, delta: float):
        self._hue = (self._hue + 0.5) % 360
        #c = Color(0, 0, 0)
        #c.hsva = (self._hue, 40, 40, 100)
        c = self.color1.lerp(self.color2, ((math.sin(math.radians(self._hue)) + 1) * 0.5) ** 0.5)
        r = Rect(0, 0, game_font.size(self.text)[0] + 50, game_font.size(self.text)[1] + 50)
        r.center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.rect(screen, self.color, r)
        text = game_font.render(self.text, True, c)
        screen.blit(text, (r.topleft[0] + 25, r.topleft[1] + 25))




def score(player: int):
    global score_p1
    global score_p2
    if player == 1:
        score_p1 += 1
    if player == 2:
        score_p2 += 1


# initialize game:
PLAYER_SPEED = 1200.0

game_font = font.SysFont(["consolas", ""], 48)

bgcolor = Color(10, 15, 20)

p1 = Paddle(Vector2(50, SCREEN_HEIGHT / 2), Color(176, 255, 54))
p2 = Paddle(Vector2(SCREEN_WIDTH - 50, SCREEN_HEIGHT / 2), Color(255, 58, 100))
s1 = Score(Vector2(400, 100), Color(176, 255, 54))
s2 = Score(Vector2(SCREEN_WIDTH - 400, 100), Color(255, 58, 100))
gameobjects: list[GameObject] = [
    s1,
    s2,
    p1,
    p2,
    Ball(Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), Vector2(600, 0), Color(150, 255, 255))
]

score_p1: int = 0
score_p2: int = 0

# main loop
finished = False
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
    s1.score = score_p1
    s2.score = score_p2
    #p2.pos = Vector2(p2.pos.x, pygame.mouse.get_pos()[1])

    # draw:
    screen.fill(bgcolor)
    for obj in gameobjects:
        obj.draw(delta)
    #text = game_font.render(str(1 / delta), True, Color(255, 255, 255))
    #screen.blit(text, (300, 100))

    pygame.display.flip()

    if max(score_p1, score_p2) >= MAX_POINTS and not finished:
        finished = True
        victory = Victory("Player 1 wins!" if score_p1 > score_p2 else "Player 2 wins!", Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), Color(176, 255, 54) if score_p1 > score_p2 else Color(255, 58, 100))
        gameobjects = [victory]
    
pygame.quit()