# Sprite classes for Doodle Jump
import pygame as pg
from settings import *
from random import choice, randrange
vec = pg.math.Vector2       # 2 for 2-dimensional

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))        # Double slash divides and truncates the fraction into an integer (avoid floats)
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Animations
        self.walking = False    # For walking animation
        self.jumping = False    # For jumping animation
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        # self.image = self.game.spritesheet.get_image(614, 1063, 120, 191)       # Bunny ready 1 image, no animations
        # self.image.set_colorkey(BLACK)                                           # Bunny ready 1 image, remove black excess pixels
        self.rect = self.image.get_rect()           # Center Player
        self.rect.center = (40, HEIGHT - 100)       # Spawn location of player
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)                # Player velocity
        self.acc = vec(0, 0)                # Player acceleration

    def load_images(self):
        # Loading images for different animations
        self.standing_frames = [self.game.spritesheet.get_image(614,1063,120,191),      # bunny1_ready.png
                                self.game.spritesheet.get_image(690, 406, 120, 201)]    # bunny1_stand.png
        # Remove excess black pixels in standing frames
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        
        # Walking Frames
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),         # bunny1_walk1.png
                            self.game.spritesheet.get_image(692, 1458, 120, 207)]           # bunny1_walk2.png
        
        self.walk_frames_l  = []
        # Remove excess black frames and flip it
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))        # True = flip horizontally, False = don't flip vertically

        # Jumping Frames
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)       # bunny1_jump.png
        self.jump_frame.set_colorkey(BLACK)

    def jump_cut(self):
        if self.jumping:                # If we're jumping
            if self.vel.y < -3:         # If we're moving upwards (negative) at a speed of -3
                self.vel.y = -3

    def jump(self):
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)        # Detect collision with a platform
        self.rect.x -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP    # Jump only if standing on a platform

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)                        # Acceleration should be 0 unless a key is pressed
        keys = pg.key.get_pressed()                 # Get which keys are down
        if keys[pg.K_LEFT]:                         # Player presses left key
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:                        # Player presses right key
            self.acc.x = PLAYER_ACC

        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION      # Acceleration changes with velocity * friction where friction is negative

        # Equations of Motion
        self.vel += self.acc                        # Add acceleration to velocity

        # When stop running, velocity will become 0 such that the idle animation is played instead of walking
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
    
        self.pos += self.vel + 0.5 * self.acc       # Position is velocity + half of acceleration

        # Wrap around sides of screen with smoother animations
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos                 # New mid bottom is now our new position

    def animate(self):
        # Animations
        now = pg.time.get_ticks()                   # Get current time

        # Check if we're walking
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Animation of walking
        if self.walking:
            if now - self.last_update > 200:        # 100 is for faster animation w/ more frames, 300 is for slower
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # Animation of standing still or idle
        if not self.jumping and not self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom                               # Prevent feet from sinking into ground
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()                       # Prevent feet from sinking into ground
                self.rect.bottom = bottom                               # Prevent feet from sinking into ground

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = choice(images)                                     # Use randomizer choice
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Powerup(self.game, self)

class Powerup(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice ([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()