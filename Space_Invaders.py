import pygame
import random
import os
import time

pygame.font.init()  # mandatory initialization of the font used later in the program
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')

# Load images

# enemy ships
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))

# Lasers
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))

# Bonus
BONUS_IMG = pygame.image.load(os.path.join('assets', 'bonus_green_cross .png'))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (WIDTH, HEIGHT))

# Music and Sounds
pygame.mixer.music.load('sounds/Space Heroes.ogg')
pygame.mixer.music.play(-1)
LASER_SOUND = pygame.mixer.Sound('sounds/laser.wav')
EXPLOSION_SOUND = pygame.mixer.Sound('sounds/explosion.wav')
LIFE_LOST_SOUND = pygame.mixer.Sound('sounds/life_lost.wav')

# The image is scaled to the size of the window


class Ship:  # Abstract class that is the parent to all other types of ships
    COOL_DOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None  # general class so no image set yet
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0  # prevents spamming lasers
        self.score = 0

    def draw(self, window):
        # Draw an empty rectangle of the given color at the given position in the given window
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 25
                LIFE_LOST_SOUND.play()
                self.lasers.remove(laser)

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
            LASER_SOUND.play()

    def cooldown(self):
        if self.cooldown_counter >= self.COOL_DOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def get_width(self):  # returns the width of the ship's image, used for collisions
        return self.ship_img.get_width()

    def get_height(self):  # returns the height of the ship's image, used for collisions
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)  # call the init method from the parent class
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)  # creates mask : defines where pixels are and are not
        self.max_health = health
        self.health = health

    def move_lasers(self, vel, objects, scb):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objects:
                    if laser.collision(obj):
                        scb.enemy_destroyed(obj)
                        objects.remove(obj)
                        EXPLOSION_SOUND.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10,
                          self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10,
                          self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {  # Dictionary which associates ship images to their color
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[
            color]  # Give the right images to ships using a string 'color'
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Bonus(Laser):
    def __init__(self, x, y, img):
        super().__init__(x, y, img)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class scoreboard:
    def __init__(self):
        self.score = 0
        f = open('scores.txt', 'a+')

        f.close()

    def high_score_read(self):
        with open('scores.txt', 'r+') as f:
            try:
                lst = f.read().splitlines()
                return max(lst)
            except ValueError:
                return 0

    def write(self):
        with open('scores.txt', 'a+') as f:
            f.write(str(self.score)+'\n')

    def enemy_destroyed(self, obj):
        self.score += int(100 * (HEIGHT - obj.y) / HEIGHT)

    def bonus_picked(self):
        self.score += 200


def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    score = scoreboard()

    main_font = pygame.font.SysFont("calibri", 35)  # Name of the system font and size
    lost_font = pygame.font.SysFont("calibri", 50)  # Name of the system font and size

    player_velocity = 5
    enemy_velocity = 2 + level
    laser_velocity = 10
    bonus_velocity = 3

    player = Player(300, 630)

    enemies = []
    bonuses = []
    wave_lenght = 3

    lost = False
    writen = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():  # Function inside a function so we don't have to pass it as a parameter of the main() function
        # each new item is drew on top of the others, so Background is first and player ship is last
        WINDOW.blit(BACKGROUND, (0, 0))  # we apply the background on the window, at coordinates (0,0) upper left
        # Draw text

        lives_label = main_font.render(f'Lives : {lives}', 1, (255, 255, 255))  # text, antilias, RGB color
        level_label = main_font.render(f'Level : {level}', 1, (255, 255, 255))
        score_label = main_font.render(f'Score : {score.score}', 1, (255, 255, 255))
        high_score_label = main_font.render(f'Highscore : {score.high_score_read()}', 1, (255, 255, 255))

        WINDOW.blit(lives_label, (10, 10))  # Upper left corner
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))  # Upper right corner
        WINDOW.blit(score_label, (WIDTH - score_label.get_width() - 10, 50))

        for enemy in enemies:  # draw every enemy in the list of enemies
            enemy.draw(WINDOW)  # inherited function from class Ship

        for bonus in bonuses:
            bonus.draw(WINDOW)

        player.draw(WINDOW)  # inherited function from class Ship

        if lost:
            lost_label = lost_font.render('SpaceShip destroyed !', 1, (255, 255, 255))
            WINDOW.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 300))  # Display the lost label
            WINDOW.blit(score_label, (WIDTH / 2 - score_label.get_width() / 2, 350))
            WINDOW.blit(high_score_label, (WIDTH / 2 - high_score_label.get_width() / 2, 400))

        pygame.display.update()

    while run:
        clock.tick(FPS)  # Sets the speed of the game so it runs at the same speed on different computers
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if not writen:
                score.write()
                writen = True
            if lost_count > FPS * 3:
                run = False
            else:
                continue  # Skips the next lines to "pause" the game

        if len(enemies) == 0:
            level += 1
            wave_lenght += 3
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(
                                  ['red', 'blue', 'green']), 10)  # Spawn enemies randomly outside of the screen
                enemies.append(enemy)
            if level > 1:
                bonus = Bonus(random.randrange(25, WIDTH-50), random.randrange(-100, 0), BONUS_IMG)
                bonuses.append(bonus)

        for event in pygame.event.get():  # gets all the possible events happening in the window
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()  # Return a dictionary of all keys and their state
        if keys[pygame.K_a] and (player.x - player_velocity > 0):  # Left
            player.x -= player_velocity
        if keys[pygame.K_d] and (player.x + player_velocity + player.get_width() < WIDTH):  # Right
            player.x += player_velocity
        if keys[pygame.K_w] and (player.y - player_velocity > 0):  # up
            player.y -= player_velocity
        if keys[pygame.K_s] and (player.y + player_velocity + player.get_height() + 10 < HEIGHT):  # down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:  # copy of the list enemies
            enemy.move(enemy_velocity)  # move every enemy
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 3 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 25
                score.enemy_destroyed(enemy)
                EXPLOSION_SOUND.play()
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:  # Condition to loose a life
                lives -= 1
                LIFE_LOST_SOUND.play()
                enemies.remove(enemy)

        for bonus in bonuses[:]:
            bonus.move(bonus_velocity)
            if collide(bonus, player):
                score.bonus_picked()
                bonuses.remove(bonus)
                if player.health <= 75:
                    player.health += 25
            elif bonus.y > HEIGHT:
                bonuses.remove(bonus)

        player.move_lasers(-laser_velocity, enemies, score)


def menu():
    title_font = pygame.font.SysFont('calibri', 40)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("press the mouse to begin", 1, (255, 255, 255))
        WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


menu()
