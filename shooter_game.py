#Создай собственный Шутер!
import pygame
from pygame import mixer
import random
import time

WINDOW_SIZE = (700, 500)
WIN_W, WIN_H = WINDOW_SIZE
FPS = 60

COUNTER_COLOR = (235, 235, 235)
WIN_TEXT_COLOR = (0, 178, 166)
LOSE_TEXT_COLOR = (178, 28, 60)
RELOAD_TEXT_COLOR = (118, 28, 178)

main_window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Шутер")
background = pygame.image.load("galaxy.jpg")
background = pygame.transform.scale(background, WINDOW_SIZE)
main_window.blit(background, (0, 0))
clock = pygame.time.Clock()

mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
pygame.font.init()

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed, image_filename):
        super().__init__()
        self.image = pygame.image.load(image_filename)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y, width, height, speed, image_filename, max_magazine_charge):
        super().__init__( x, y, width, height, speed, image_filename)
        self.fire_sound = mixer.Sound("fire.ogg")
        self.keys = None
        self.last_shoot_time = 0
        self.is_empty = False
        self.max_magazine_charge = max_magazine_charge
        self.magazine_charge = self.max_magazine_charge
        self.reload_start_time = 0
        self.bullets = pygame.sprite.Group()


        

    def set_control(self, key_left, key_right, make_shoot):
        self.keys = {
            "LEFT": key_left,
            "RIGHT": key_right,
            "FIRE": make_shoot
        }

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[self.keys["LEFT"]] and self.rect.x > 0:
            self.rect.x -= self.speed
        if pressed_keys[self.keys["RIGHT"]] and self.rect.x < WIN_W - self.rect.width:
            self.rect.x += self.speed
        if pressed_keys[self.keys["FIRE"]]:
            current_time = time.time()
            if not self.is_empty:
                if self.magazine_charge > 0:
                    if current_time - self.last_shoot_time > 0.4:
                        self.fire()
                        self.last_shoot_time = current_time
                        self.magazine_charge -= 1
                else:
                    self.is_empty = True
                    self.reload_start_time = current_time
            elif current_time - self.reload_start_time > 3:
                self.is_empty = True
                self.magazine_charge = self.max_magazine_charge

    def fire(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, 7, 10, 3, "bullet.png")
        self.bullets.add(bullet)
        self.fire_sound.play()

class Enemy(GameSprite):
    def __init__(self, pos_x, pos_y, step_size, sprite_weight, sprite_height, sprite_image_file):
        super().__init__(pos_x, pos_y, step_size, sprite_weight, sprite_height, sprite_image_file)
        self.x_start = None
        self.y_start = None
        self.x_end = None
        self.y_end = None

    def set_waypoint(self, x_start, y_start, x_end, y_end):
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end

    def update(self):
        if self.y_start > self.y_end and self.rect.y > self.y_end:
            self.rect.y -= self.speed
        elif self.y_start < self.y_end and self.rect.y < self.y_end:
            self.rect.y += self.speed
        from_top_to_bottom = self.y_start <= self.y_end and self.rect.y >= self.y_end
        from_bottom_to_top = self.y_start >= self.y_end and self.rect.y <= self.y_end

        if (from_top_to_bottom or from_bottom_to_top):
            self.rect.y = self.y_start
            self.rect.x = random.randint(50, WIN_W - self.rect.width - 50)
            global missed_counter
            missed_counter += 1


class Label():
    def __init__(self, x, y, text_color=(255, 255, 255), font_name="Arial", font_size = 20):
        self.x = x
        self.y = y
        self.color = text_color
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_size = font_size
        self.font_name = font_name
        self.text = None
        self.image = None

    def sent_font_style(self, font_name, text_color, font_size):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_size = font_size
        self.font_name = font_name
        self.color = text_color

    def set_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

def create_new_enemy(enemy_group, new_enemy_amount, image_file, is_rand_y=False):
    for i in range(new_enemy_amount):
        if is_rand_y:
            y = random.randint(-500, -100)
        else:
            y = -100
        rand_x = random.randint(50, WIN_W - 50)
        rand_speed = random.randint(1, 4)
        enemy = Enemy(rand_x, y, 50, 50, rand_speed, image_file)
        enemy.set_waypoint(rand_x, y, rand_x, WIN_H + 50)
        enemy_group.add(enemy)


player1 = Player(WIN_W // 2, WIN_H - 50, 40, 60, 5, "rocket.png", 7)
player1.set_control(pygame.K_a, pygame.K_d, pygame.K_SPACE)

asteroids = pygame.sprite.Group()
asteroids_amount = 3
create_new_enemy(asteroids, asteroids_amount, "asteroid.png", True)

enemies = pygame.sprite.Group()
enemy_amount = 5
create_new_enemy(enemies, enemy_amount, "ufo.png")



miss_label = Label(50, 10, COUNTER_COLOR)
miss_label.set_text("Пропущено: 0")
hit_counter_label = Label(50, 40, COUNTER_COLOR)
hit_counter_label.set_text("Уничтожено: 0")
result_text = Label(WIN_W // 2 - 125 , WIN_H // 2 - 50)

hit_counter = 0
missed_counter = 0
is_win = False
is_lose = False
is_running = True
while is_running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            is_running = False

    if is_win == is_lose:
        player1.update()
        player1.bullets.update()
        enemies.update()
        asteroids.update()
        miss_label.set_text("Пропущено: " + str(missed_counter))
        hit_amount = len(pygame.sprite.groupcollide(player1.bullets, enemies, True, True))
        if hit_amount > 0:
            hit_counter += hit_amount
            create_new_enemy(enemies, hit_amount, "ufo.png")
            hit_counter_label.set_text("Уничножено: " + str(hit_counter))
            if hit_amount >= 10:
                is_win = True
                result_text.sent_font_style("Arial", WIN_TEXT_COLOR, 60)
                result_text.set_text("YOU WIN")
        if pygame.sprite.spritecollide(player1, enemies, False) or \
            pygame.sprite.spritecollide(player1, asteroids, False) or \
                missed_counter > 5:
            is_lose = True
            result_text.sent_font_style("Arial", LOSE_TEXT_COLOR, 60)
            result_text.set_text("YOU LOSE")

    main_window.blit(background, (0, 0))

    miss_label.draw(main_window)
    hit_counter_label.draw(main_window)
    player1.reset(main_window)
    player1.bullets.draw(main_window)
    enemies.draw(main_window)
    asteroids.draw(main_window)

    if is_win or is_lose:
        result_text.draw(main_window)

    pygame.display.update()
    clock.tick(FPS)