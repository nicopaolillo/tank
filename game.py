import pygame, time, sys, random
pygame.init()
pygame.mixer.init()
width = 1000
height = 700
white = (255,255,255)
black = (0,0,0)
sand_color = (195,169,139)
background = pygame.image.load("assets/background_2.png")
clock = pygame.time.Clock()
#Crea la ventana/fps!!!
screen = pygame.display.set_mode((width,height))
fps = pygame.time.Clock()

#carga de efectos de sonido
engine = pygame.mixer.Sound("sound/engine.ogg")
explosion = pygame.mixer.Sound("sound/explosion.ogg")
shoot_sound = pygame.mixer.Sound("sound/shoot.ogg")
iron_sound = pygame.mixer.Sound("sound/iron_sound.ogg")
music = pygame.mixer.music.load('sound/song.ogg')
pygame.mixer.music.play(-1)
hp=100
font = pygame.font.SysFont(None, 40)

#clases......................................................................../

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  
        self.image = pygame.image.load("assets/player.png").convert()     
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = width // 2
        self.rect.bottom = height -10
        self.speed_x = 0
        self.speed_y = 0   
          

class Death(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()             
        self.sprites = []
        self.is_animating = False
        self.sprites.append(pygame.image.load("assets/Explosion1/0001.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0002.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0003.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0004.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0005.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0006.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0007.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0008.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0009.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0010.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0011.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0012.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0013.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0014.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0015.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0016.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0017.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0018.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0019.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0020.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0021.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0022.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0023.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0024.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0025.png"))
        self.sprites.append(pygame.image.load("assets/Explosion1/0026.png"))
        self.current_sprite=0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def animate(self):
        self.is_animating = True
    
    def update(self):
        if self.is_animating == True:
            self.current_sprite+=1
            if self.current_sprite >= len(self.sprites):
                self.current_sprite=0
                self.is_animating = False
            self.image = self.sprites[self.current_sprite]


class Shooting(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/bullet.png").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
  
    def update(self):
        self.rect.y -= 3    
        
class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/red_tank.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200 , 700)
        self.rect.y = random.randrange(height - 600)
        self.speed_y = 1

   #funcionalidad para que se vuelva a generar un tanque al salir del mapa
    def update (self):
        if self.rect.y > height:
            self.rect.y = -10
            self.rect.x = random.randrange(200,700) 
#clase hija
class Tank_green(Tank):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/green_tank.png").convert_alpha()

#clases.................................................................................................\

def init():
    #creación de listas
    global box_wood_list
    global box_iron_list
    global shoot_list
    global crash_list
    global all_sprites
    global red_tank
    global game_over
    box_wood_list = pygame.sprite.Group()
    box_iron_list = pygame.sprite.Group()
    shoot_list = pygame.sprite.Group()
    crash_list = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    #instanciación del jugador con clase player
    
    red_tank = Player()

    #instanciación y guardado de los tanques verdes
    for i in range(1):
        box_iron = Tank_green()
        box_iron_list.add(box_iron)
        all_sprites.add(box_iron)

    #instanciación y guardado de los tanques rojos
    for i in range(3):
        box_wood = Tank()    
        box_wood_list.add(box_wood)
        all_sprites.add(box_wood)

    #guardo el sprite del tanque una lista
    all_sprites.add(red_tank)

    #Condición para que corra el juego!!!
    nivelCompletado=False
    game_over = False

#Bucle principal...................................................................../

def game():
    hp=200
    y=700
    misiles=1
    misilNuevo=0
    all_sprites.add(red_tank)
    game_over=False
    nivel=0
    completado=False
    
    while not game_over :
        tiempoTranscurrido=int(pygame.time.get_ticks())/400
        for event in pygame.event.get():
            #Eventos teclado
            if event.type == pygame.KEYDOWN:
                # player!!!
                if event.key == pygame.K_LEFT:
                    red_tank.speed_x = -3
                    red_tank.image = pygame.image.load("assets/player_left.png").convert()
                    red_tank.image.set_colorkey(black)
                if event.key == pygame.K_RIGHT: 
                    red_tank.speed_x = 3
                    red_tank.image = pygame.image.load("assets/player_rigth.png").convert()
                    red_tank.image.set_colorkey(black)
                if event.key == pygame.K_UP:
                    red_tank.speed_y = -3
                    red_tank.image = pygame.image.load("assets/player.png").convert()     
                    red_tank.image.set_colorkey(black)
                if event.key == pygame.K_DOWN: 
                    red_tank.speed_y = 3   
                    red_tank.image = pygame.image.load("assets/player_down.png").convert()     
                    red_tank.image.set_colorkey(black)
                if event.key == pygame.K_SPACE:
                        #creación del disparo
                        if(misiles>0):
                            shoot = Shooting()   
                            shoot.rect.x = red_tank.rect.x +10
                            shoot.rect.y = red_tank.rect.y -20
                            all_sprites.add(shoot)
                            shoot_list.add(shoot)
                            shoot_sound.play() 
                            misiles=misiles-1
                            misilNuevo=tiempoTranscurrido

            if event.type == pygame.KEYUP:
                # player!!!
                if event.key == pygame.K_LEFT:
                    red_tank.speed_x = 0
                if event.key == pygame.K_RIGHT:
                    red_tank.speed_x = 0
                if event.key == pygame.K_UP:
                    red_tank.speed_y = 0
                if event.key == pygame.K_DOWN:
                    red_tank.speed_y = 0    
                

    #control del player dentro del escenario
        if red_tank.rect.right > 800:
            red_tank.rect.right = 800
        if red_tank.rect.left < 200:
            red_tank.rect.left = 200  
        if red_tank.rect.top < 0:
            red_tank.rect.top = 0
        if red_tank.rect.bottom > height:
            red_tank.rect.bottom = height    

        #fondo y movimiento de la imagen de fondo
        y_relativa = y % background.get_rect().height
        screen.blit(background,(0,y_relativa-background.get_rect().height))
        if y_relativa < height: 
            screen.blit(background,(0,y_relativa))
        y += 1*3

        #actualización del movimiento del player
        red_tank.rect.x += red_tank.speed_x
        red_tank.rect.y += red_tank.speed_y
        
        #actualización del movimiento vertical de todos los tanques
        for i in box_wood_list:
            i.rect.y += i.speed_y*3
    
        for i in box_iron_list:
            i.rect.y += i.speed_y*3

        #colisiones del disparo con los tanques rojos
        for i in shoot_list:
            shoot_hits_list = pygame.sprite.spritecollide(shoot,box_wood_list,True)
            for i in shoot_hits_list:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)
                explosion.play() 
            if shoot.rect.y < -10:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)

        #colisiones del disparo con los tanques verdes
        for i in shoot_list:
            shoot_hits_list = pygame.sprite.spritecollide(shoot,box_iron_list,len(box_wood_list)==0)
            for i in shoot_hits_list:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)
                iron_sound.play()
                if(len(box_wood_list)==0):
                 explosion.play() 


        #colisión del player con los tanques    
        for i in box_wood_list:
            crash_list = pygame.sprite.spritecollide(red_tank,box_wood_list,True)  
            if len(crash_list) == 1:
                explosion.play()     
            for i in crash_list:   
                hp=hp-20              
                death = Death(red_tank.rect.x,red_tank.rect.y)
                death.animate()
                all_sprites.add(death)
                if(hp<=0): 
                    all_sprites.remove(red_tank)
                    game_over=True
                    if(game_over):
                        font2 = pygame.font.SysFont(None, 100)
                        text1 = font2.render("GAME OVER", False, (255,0,0))
                        text_rect = text1.get_rect(center=(width/2, height/2))
                        screen.blit(text1, text_rect)
            

        for i in box_iron_list:   #revisar como optimizar las dos listas!!!
            crash_list = pygame.sprite.spritecollide(red_tank,box_iron_list,True)  
            if len(crash_list) == 1:
                explosion.play()     
            for i in crash_list: 
                hp=hp-40 
                death = Death(red_tank.rect.x,red_tank.rect.y)
                death.animate()
                all_sprites.add(death)
                if(hp<=0):   
                    all_sprites.remove(red_tank)
                    game_over=True
                    if(game_over):
                        font2 = pygame.font.SysFont(None, 100)
                        text1 = font2.render("GAME OVER", False, (255,0,0))
                        text_rect = text1.get_rect(center=(width/2, height/2))
                        screen.blit(text1, text_rect)
                        
        #todos los metodos update de los objetos de esta lista funcionando
        all_sprites.update()
        #dibujo en la pantalla
        all_sprites.draw(screen)
        pygame.display.flip()


        if(tiempoTranscurrido-misilNuevo>5):
            misiles=misiles+1
            misilNuevo=tiempoTranscurrido
        if(len(box_iron_list)==0 and len(box_wood_list)==0):
            nivel=nivel+1
            completado=True
        if(nivel>1 and completado):
            completado=False
            screen.blit(text2, (140,60))
            for i in range(nivel+2):
                box_iron = Tank_green()
                box_iron_list.add(box_iron)
                all_sprites.add(box_iron)
            for i in range(nivel+4):
                box_wood = Tank()    
                box_wood_list.add(box_wood)
                all_sprites.add(box_wood)
    
        text1 = font.render("Energia: ", False, (173,255,47))
        screen.blit(text1, (0,60))
        text2 = font.render(str(hp), False, (173,255,47))
        screen.blit(text2, (140,60))
        text3 = font.render("Misiles: ", False, (173,255,47))
        screen.blit(text3, (0,120))
        text4 = font.render(str(misiles), False, (173,255,47))
        screen.blit(text4, (140,120))
        text5 = font.render("Nivel: ", False, (173,255,47))
        screen.blit(text5, (0,180))
        text6 = font.render(str(nivel), False, (173,255,47))
        screen.blit(text6, (140,180))
        #actualiza la pantalla
        pygame.display.flip()
        fps.tick(60) 
    #Bucle principal.....................................................................................\
    
while(True):
    pygame.time.wait(3000)
    init()
    game()

