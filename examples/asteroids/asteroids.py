import logging
import math
import random
import collections

import pygame
import pygame.draw
import pygame.event
import pygame.gfxdraw
import pygame.surface
import pygame.time
import pygame.transform

import pygame.locals as l

import log_config  # noqa

logger = logging.getLogger()
logger.setLevel(500)

from instapy import reloader

import physics
import local_math as lm
import values
import vector as v
import weapons

#from instapy import reloader


class TextVar(object):
    def __init__(self, initial_text, font, colour, position):
        self.text = initial_text
        font_file = pygame.font.match_font(font)
        self.font = pygame.font.Font(font_file, 30)
        self.colour = colour
        self.x, self.y = position

    def set_text(self, text):
        self.text = text

    def draw(self, surface):
        t = self.font.render(self.text, True, self.colour)
        surface.blit(t, (self.x, self.y))


class Game(reloader.Looper):
    #__metaclass__ = reloader.Looper

    def __init_once__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

        self.player = physics.Player((320, 320))

        self.joystick_mode = pygame.joystick.get_count() > 0

        if self.joystick_mode:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.turn_speed = math.pi
        self.move_speed = 30

        self.mouse_rels = collections.deque(maxlen=120)

        self.relative_mouse = False

        self.asteroids = []
        self.asteroid_probability = 0.05

        self.weapons = [weapons.MachineGun(self), weapons.Shotgun(self),
                        weapons.Missile(self), weapons.Laser(self),
                        weapons.Bomb(self)]
        self.current_weapon = 0

        self.score = 0
        self.score_text = TextVar("0 points",
                                  'ubuntumono',
                                  values.white,
                                  (0, 0))

        self.done = False
        self.running = True
        self.debugger = False

    def __instapy_update__(self, old, new):
        for a in self.asteroids:
            del a._drawable

    def grab_mouse(self):
        if not self.joystick_mode:
            #pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)

    def ungrab_mouse(self):
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

    def die(self):
        print "Score: %d" % self.score
        self.__init__()

    def draw(self):
        self.screen.fill(values.black)

        self.player.draw(self.screen)

        self.draw_asteroids()
        self.draw_bullets()
        self.draw_mouse()
        self.draw_score()

        pygame.display.flip()

    def draw_asteroids(self):
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

    def draw_bullets(self):
        for weapon in self.weapons:
            for bullet in weapon.bullets:
                bullet.draw(self.screen)

    def draw_mouse(self):
        if not self.relative_mouse and not self.joystick_mode:
            (x, y) = pygame.mouse.get_pos() if self.running else self.mouse_pos
            (x, y) = v.vec_sub((x, y), (320, 320))
            (x, y) = v.vec_add((x, y), self.player.int_position)
            (x, y) = v.vec_mod((x, y), (640, 640))
            colour = (255, 10, 10)
            radius = 10

            pygame.draw.line(self.screen, colour, (x - radius, y),
                                                  (x + radius, y))
            pygame.draw.line(self.screen, colour, (x, y - radius),
                                                  (x, y + radius))

            pygame.gfxdraw.aacircle(self.screen, x, y, radius, colour)

    def draw_score(self):
        self.score_text.set_text("%d points" % lm.r(self.score))
        self.score_text.draw(self.screen)

    def check_collisions(self):
        asteroids_to_delete = []

        for n, asteroid in enumerate(self.asteroids):
            if asteroid.is_colliding(self.player):
                self.die()

            for weapon in self.weapons:
                if weapon.do_collisions(asteroid):
                    asteroids_to_delete.append(n)
                    self.add_score(asteroid.score())

        new_asteroids = []
        for n, a in enumerate(self.asteroids):
            if n not in asteroids_to_delete:
                new_asteroids.append(a)
            else:
                new_asteroids.extend(a.split())
        self.asteroids = new_asteroids

    def update_scene(self):
        self.player.update(self.dt_ratio)
        self.generate_asteroid()
        self.check_collisions()
        self.update_asteroids()
        self.update_bullets()
        self.update_weapons()

        self.asteroid_probability += 0.0001 * self.dt_ratio

    def update_asteroids(self):
        for asteroid in self.asteroids:
            asteroid.update(self.dt_ratio)

    def update_bullets(self):
        for weapon in self.weapons:
            for bullet in weapon.bullets:
                bullet.update(self.dt_ratio)

    def update_weapons(self):
        for weapon in self.weapons:
            weapon.update(self.dt)

    def generate_asteroid(self):
        if random.uniform(0, 1) < self.asteroid_probability:
            asteroid = physics.Asteroid.generate()
            while v.vec_distance(asteroid.position, self.player.position) < 107:
                logging.info("Killed by RNG")
                asteroid = physics.Asteroid.generate()
            self.asteroids.append(asteroid)

    def fire(self):
        self.weapons[self.current_weapon].fire(self.dt)

    def fire_bomb(self):
        self.weapons[-1].fire(self.dt)

    def add_score(self, score):
        self.score += score

    def pause(self):
        self.ungrab_mouse()
        self.mouse_pos = pygame.mouse.get_pos()
        self.running = False

    def unpause(self):
        self.grab_mouse()
        self.running = True

    def quit(self):
        self.ungrab_mouse()
        self.done = True

    def handle_events(self):
        if self.running:
            self._handle_running_events()
        else:
            self._handle_paused_events()

    def _handle_paused_events(self):
        for event in pygame.event.get():
            if event.type == l.KEYDOWN:
                if event.key == l.K_p:
                    self.unpause()
                elif event.key == l.K_q:
                    self.quit()
            elif event.type == l.JOYBUTTONDOWN:
                if event.button == 7:  # Start button
                    self.unpause()
                elif event.button == 6:  # Back button
                    self.quit()

    def _handle_running_events(self):
        for event in pygame.event.get():
            if event.type == l.KEYDOWN:
                if event.key == l.K_SPACE:
                    self.fire_bomb()
                elif event.key == l.K_r:
                    self.__init__()
                elif event.key == l.K_q:
                    self.quit()
                elif event.key == l.K_1:
                    self.current_weapon = 0
                elif event.key == l.K_2:
                    self.current_weapon = 1
                elif event.key == l.K_3:
                    self.current_weapon = 2
                elif event.key == l.K_4:
                    self.current_weapon = 3
                elif event.key == l.K_p:
                    self.pause()
                elif event.key == l.K_PAUSE:
                    self.debugger = not self.debugger
            elif event.type == l.KEYUP:
                pass
            elif event.type == l.MOUSEMOTION:
                pass
            elif event.type == l.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.next_weapon()
                elif event.button == 5:
                    self.previous_weapon()
            elif event.type == l.JOYBUTTONDOWN:
                if event.button == 4:  # left bumper
                    self.previous_weapon()
                elif event.button == 5:  # right bumper
                    self.next_weapon()
                elif event.button == 7:  # Start button
                    self.pause()
        keys = pygame.key.get_pressed()

        if keys[l.K_w]:
            self.player.vy = -self.move_speed
        if keys[l.K_s]:
            self.player.vy = self.move_speed

        if not (keys[l.K_w] or keys[l.K_s]):
            self.player.vy = 0

        if keys[l.K_d]:
            self.player.vx = self.move_speed
        if keys[l.K_a]:
            self.player.vx = -self.move_speed

        if not (keys[l.K_d] or keys[l.K_a]):
            self.player.vx = 0

        self.face_mouse()
        if self.joystick_mode:
            self.handle_joystick_motion()

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            self.fire()

    def handle_joystick_motion(self):
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        if v.vec_distance((x, y), (0, 0)) > 0.3:
            self.player.vx = x * self.move_speed
            self.player.vy = y * self.move_speed

        r_trigger = self.joystick.get_axis(5)
        if r_trigger > -0.8 and r_trigger != 0.0:
            self.fire_bomb()

    def face_mouse(self):
        if not self.joystick_mode:
            if self.relative_mouse:
                rel = pygame.mouse.get_rel()
                if rel != (0, 0):
                    self.mouse_rels.append(rel)
                    self.player.angle = v.vec_angle(
                        v.vec_mean(self.mouse_rels), (0, 0))
            else:
                self.player.angle = v.vec_angle(pygame.mouse.get_pos(),
                                                (320, 320))
        else:
            x = self.joystick.get_axis(3)
            y = self.joystick.get_axis(4)
            if v.vec_distance((x, y), (0, 0)) > 0.3:
                self.fire()
                self.player.angle = v.vec_angle((x, y), (0, 0))

    def next_weapon(self):
        self.current_weapon = ((self.current_weapon + 1)
                               % (len(self.weapons) - 1))

    def previous_weapon(self):
        self.current_weapon = ((self.current_weapon - 1)
                               % (len(self.weapons) - 1))

    def loop_body(self):
        if not self.done:
            self.dt = self.clock.tick(60)
            self.dt_ratio = 1.0 / self.dt
            self.handle_events()
            self.draw()
            if self.running:
                self.grab_mouse()
                self.update_scene()
            else:
                self.ungrab_mouse()

        return self.done

if __name__ == '__main__':
    looper = Game()
    while not looper.done:
        looper.loop_body()
