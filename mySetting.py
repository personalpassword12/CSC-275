import pygame
import os
pygame.init()
vec = pygame.math.Vector2

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.7)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Dungeon Explorer')

#FRAMERATE
clock = pygame.time.Clock()
FPS = 60

#game Variables
GRAVITY = 0.60

moving_left = False
moving_right = False
shoot = False
attack = False
#define COLORS
#load images

#kunai

bullet_img = pygame.image.load('img/Ninja/bullet.png').convert_alpha()

BG = (100,10,150)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0,800), (SCREEN_WIDTH, 800))

class Ninja(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
#load all images for the players
        animation_types = [ 'Idle', 'run', 'jump', 'death', 'throw', 'climb', 'jumpThrow', 'Attack']

        for animation in animation_types:
            #reset animation append list 
            temp_list = []
            #count nnumber of files
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Player Attacking
        self.attacking = False
        self.attack_frame = 0
        self.attack_counter = 0
        self.attack_range = pygame.Rect(0, 0, 0, 0)
        self.pos = vec(x, y)
        
    def attack(self):
        if self.attacking == True:
            if self.direction == -1:
                self.attack_range = pygame.Rect(self.rect.x + self.rect.width,self.pos.y, 30, self.rect.height)
            elif self.direction == 1:
                self.attack_range = pygame.Rect(self.pos.x, self.pos.y, 30, self.rect.height)
                
            if self.attack_frame > 6:
                self.attack_frame = 0
                self.attacking = False
                self.attack_range = pygame.Rect(0, 0, 0, 0)
                return
            self.attack_counter += 1
            if self.attack_counter >= 2:
                self.attack_frame += 1
                self.attack_counter = 0


        
    def update(self):
        self.update_animation()
        self.check_alive()
        self.attack()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        
        #assign movement if left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
            ##jump

        if self.jump == True and self.in_air == False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y


        # check collision with floor
        if self.rect.bottom + dy > 800:
            dy = 800 - self.rect.bottom
            self.in_air = False
            
    #Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1


    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0



    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


 
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()


#sprite group for bullet/kunai
bullet_group = pygame.sprite.Group()

        
player = Ninja('Ninja',100,800,0.2,5,10)
enemy = Ninja('enemy',100,750,0.2,5,10)
run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.update()
    player.draw()

    enemy.update()
    enemy.draw()

    #update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)


    #update player actions
    if player.alive:
        #shoot bullets
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2)#2: jump
        elif moving_left or moving_right:
            player.update_action(1)#1: run
        else:
            player.update_action(0)#0: idle
        player.move(moving_left, moving_right)
        if attack:
            player.update_action(6)
            player.attack()
            
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                player.update_action(4)
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_t:
                player.update_action(7)
                player.attacking = True
                player.attack()

        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_t:
                player.attacking = False




    pygame.display.update()

pygame.quit()
