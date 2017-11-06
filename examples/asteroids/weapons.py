# stdlib
import collections
import random

# local modules
import physics
import vector as v


class Weapon(object):
    rate = 15
    max_bullets = 15
    spread = 0.05

    def __init__(self, game):
        self._bullets = collections.deque(maxlen=self.max_bullets)
        self.game = game
        self.ms_since_fired = 0

    @property
    def bullets(self):
        return self._bullets

    def _add_bullet(self, position=None, angle=None):
        position = position or self.game.player.position
        angle = angle or self.game.player.angle

        perturbation = random.gauss(0, self.spread)
        angle = angle + perturbation
        bullet = physics.Bullet(position,
                                v.rotate([(0, 200)], angle, (0, 0))[0],
                                angle)
        self._bullets.append(bullet)

    def _do_fire(self):
        self._add_bullet()

    def fire(self, dt):
        if self.ms_since_fired > 1000.0 / self.rate:
            self._do_fire()
            self.ms_since_fired = 0

    def update(self, dt):
        self.ms_since_fired += dt

    def _post_collision(self, bullet):
        pass

    def do_collisions(self, physical):
        collided = False
        new_bullets = collections.deque(maxlen=self.max_bullets)
        for bullet in self._bullets:
            if not bullet.to_delete:
                if collided or not bullet.is_colliding(physical):
                    new_bullets.append(bullet)
                else:
                    self._post_collision(bullet)
                    collided = True
        self._bullets = new_bullets
        return collided


class MachineGun(Weapon):
    rate = 70
    max_bullets = 45
    pass


class Shotgun(Weapon):
    max_bullets = 70
    rate = 8
    spread = 0.2

    def _do_fire(self):
        for _ in xrange(20):
            self._add_bullet()


class Bomb(Weapon):
    rate = 1
    max_radius = 905

    def _add_bullet(self, position=None, angle=None):
        position = position or self.game.player.position
        bullet = physics.Explosion(position, max_radius=self.max_radius)
        self._bullets.append(bullet)

    def do_collisions(self, physical):
        collided = False
        new_bullets = collections.deque(maxlen=self.max_bullets)
        for bullet in self._bullets:
            if not bullet.to_delete:
                if bullet.is_colliding(physical):
                    collided = True
                new_bullets.append(bullet)
        self._bullets = new_bullets
        return collided


class Laser(object):
    def __init__(self, game):
        self.game = game

    def fire(self, dt):
        self.bullet = physics.LaserBeam(self.game.player.position,
                                        self.game.player.angle)

    def update(self, dt):
        try:
            del self.bullet
        except AttributeError:
            pass

    @property
    def bullets(self):
        try:
            return [self.bullet]
        except AttributeError:
            return []

    def do_collisions(self, physical):
        try:
            return self.bullet.is_colliding(physical)
        except AttributeError:
            pass


class MissileExplosionWeapon(Bomb):
    max_radius = 60

    def fire(self, position=None):
        explosion = physics.Explosion(position, max_radius=self.max_radius)
        self._bullets.append(explosion)


class Missile(Weapon):
    rate = 40
    max_bullets = 60
    spread = 0.1

    def __init__(self, game):
        super(Missile, self).__init__(game)
        self.explosion_weapon = MissileExplosionWeapon(game)

    def _post_collision(self, bullet):
        self.explosion_weapon.fire(bullet.position)

    def do_collisions(self, physical):
        collided = super(Missile, self).do_collisions(physical)
        collided |= self.explosion_weapon.do_collisions(physical)
        return collided

    @property
    def bullets(self):
        return list(self._bullets) + list(self.explosion_weapon.bullets)
