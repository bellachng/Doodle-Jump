# Base Template for Main Class

import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        # Initialize game window
        pg.init()
        pg.mixer.init()                                     # for sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True                                 # Used for loop
        self.font_name = pg.font.match_font(FONT_NAME)      # Match closest font to system's font
        self.load_data()

    def load_data(self):
        # Load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'w') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        # Load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        # Load sound files
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump.wav'))
        self.jump_sound.set_volume(VOLUME_JUMP)
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'cartoon-jump.ogg'))
        self.boost_sound.set_volume(VOLUME_BOOST)
        

    def new(self):
        # Resets/starts a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.player = Player(self)          # Add Player
        for plat in PLATFORM_LIST:      # Loop through platform list
            Platform(self, *plat)         # Where *plat splits it into its 4 componetns of plat[0], plat[1], plat[2], plat[3]
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'happytune.ogg'))
        pg.mixer.music.set_volume(VOLUME)
        self.run()                      # Whenever new game starts, run it

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)       # Infinitely repeat the music
        pg.mixer.music.set_volume(VOLUME)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)        # keep loop running at the right speed
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(FADEOUT)

    def update(self):
        # Game Loop update
        self.all_sprites.update()

        # Spawn a mob
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)

        # Collision check - check if player hits a mob
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False
 
        # Collision check - check if player hits a platform only when falling
        if self.player.vel.y > 0:   # Can jump through a platform instead of teleporting onto the top
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)      # False to not delete platforms upon hitting
            if hits:
                lowest = hits[0] # Lowest platform
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < hits[0].rect.centery:     # Only snap to platform is feet hits the center of platform
                        self.player.pos.y = hits[0].rect.top    # Detect hitting a platform
                        self.player.vel.y = 0                   # Don't fall through platform
                        self.player.jumping = False            # Set back to false
        
        # Check if player reaches top 1/4 of the screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)     # Move player
            for mob in self.mobs:                                   # Move mobs downwards
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:                             # Move platform downwards
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:                         # Remove platform if it goes off the screen
                    plat.kill()
                    self.score += 10

        # Collision - If player hits a powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # Player death
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:                     # Player falls past platforms
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # Spawn new platforms at top to keep same average number of platforms
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH-width), random.randrange(-75, -30))

            # For loop: If a platform is on top of another, kill it
            on_top = pg.sprite.spritecollide(p, self.platforms, False)
            for plat in on_top:
                if plat != p:
                    p.kill()

    def events(self):
        # Game Loop events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:               # Event: Quit
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:            # Event: Player Jump
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:              # Event: Player Jump; longer jump with arrow ket
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text("SCORE: " + str(self.score), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(VOLUME)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(FADEOUT)

    def show_go_screen(self):
        # game over/continue
        if not self.running:        # If exiting the game using the 'X' key
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(VOLUME)
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)

        # Update high score
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)

        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(FADEOUT)

    def wait_for_key(self):
        # To allow start and end game screens to show
        waiting = True
        while waiting:
            self.clock.tick(FPS / 2)
            for event in pg.event.get():
                if event.type == pg.QUIT:       # If Player presses quit
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:      # If Player presses any key
                    waiting = False

    def draw_text(self, text, size, colour, x, y):
        # Show text on screen
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()