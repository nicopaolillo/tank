import pygame, time, sys, random
from pygame import QUIT
from pygame.mixer import pre_init

pygame.init()
pygame.mixer.init()
width = 1000
height = 700
white = (255,255,255)
black = (0,0,0)
sand_color = (195,169,139)
background = pygame.image.load("assets/background_2.png")
#Crea la ventana/fps!!!
screen = pygame.display.set_mode((width,height))
fps = pygame.time.Clock()
#carga de efectos de sonido
engine = pygame.mixer.Sound("sound/engine.ogg")
explosion = pygame.mixer.Sound("sound/explosion.ogg")
shoot_sound = pygame.mixer.Sound("sound/shoot.ogg")
iron_sound = pygame.mixer.Sound("sound/iron_sound.ogg")
music = pygame.mixer.music.load('sound/song.ogg')
sonidoMenu = pygame.mixer.Sound('sound/seleccion.mp3')
#Repite la música
pygame.mixer.music.play(-1)
#Fuente y tamaño de las letras
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
        self.hp=200
        self.nivel=1
        self.misiles=0
        self.puntaje=0  

class Death(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()             
        self.sprites = []
        self.is_animating = False
        self.sprites.append(pygame.image.load("assets/TankExplosion/0001.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0002.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0003.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0004.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0005.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0006.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0007.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0008.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0009.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0010.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0011.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0012.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0013.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0014.png"))
        self.sprites.append(pygame.image.load("assets/TankExplosion/0015.png"))
        self.current_sprite=0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x-30
        self.rect.y = y-30
    def animate(self):
        self.is_animating = True
    
    def update(self):
        if self.is_animating == True:
            self.current_sprite+=1
            if self.current_sprite >= len(self.sprites):
                self.current_sprite=-1
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
        self.image = pygame.image.load("assets/tank_red.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200 , 700)
        self.rect.y = random.randrange(height - 350)
        self.speed_y = 1

   #funcionalidad para que se vuelva a generar un tanque al salir del mapa
    def update (self):
        if self.rect.y > height:
            self.rect.y = -10
            self.rect.x = random.randrange(150,750) 
#clase hija
class Tank_green(Tank):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/tank_green.png").convert_alpha()

def simple_show_text(string,position1, position2):
    text1 = font.render(string, True, (173,255,47))
    screen.blit(text1, (position1,position2))

def show_text(string, int, position1, position2, position3, position4):
    text1 = font.render(string, True, (173,255,47))
    screen.blit(text1, (position1,position2))
    text2 = font.render(str(int), True, (173,255,47))
    screen.blit(text2, (position3,position4))

#clases.................................................................................................\

def init():
    global tank_red_list
    global tank_green_list
    global shoot_list
    global crash_list
    global all_sprites
    global player
    global game_over
    #creación de listas
    tank_red_list = pygame.sprite.Group()
    tank_green_list = pygame.sprite.Group()
    shoot_list = pygame.sprite.Group()
    crash_list = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    #instanciación del jugador con clase player
    player = Player()

    #instanciación y guardado de tanques verdes
    for i in range(3):
        tank_green = Tank_green()
        tank_green_list.add(tank_green)
        all_sprites.add(tank_green)

    #instanciación y guardado de tanques rojos
    for i in range(5):
        tank_red = Tank()    
        tank_red_list.add(tank_red)
        all_sprites.add(tank_red)

    #guardo el sprite del tanque una lista
    all_sprites.add(player)

    #Condición para que corra el juego!!!
    game_over = False
#Menu del juego....................................................................../
"""Texto en la mitad mas 50 para arriba y 50 para abajo.Posicion de los cuadrados que marcan que
opcion estas eligiendo va a ser lo mismo, para tener una referencia y despues un event
que vaya manejando la variable
width = 1000
height = 700"""
def menu():
    sigueEnMenu= True
    cuadradoEnX = int(width/2)
    cuadradoEnY = int((height/2)-50)
    jugar=int((height/2)-50)
    salir= int((height/2)+50)
    negro= (0,0,0)
    #cuadrado = pygame.Rect(cuadradoEnX, cuadradoEnY, 150, 30)
    while(sigueEnMenu):
        pygame.draw.rect(screen, (255, 0, 0), (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        # Texto
        simple_show_text("Jugar", width/2, (height/2)-50)
        simple_show_text("Opciones", width/2, (height/2))
        simple_show_text("Salir", width/2, (height/2)+50)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sonidoMenu.play()
                    pygame.quit()
                if event.key == pygame.K_UP:
                    sonidoMenu.play()
                    cuadradoEnY -= 50
                    if cuadradoEnY < jugar:
                        cuadradoEnY=((height/2)+50)
                if event.key == pygame.K_DOWN:
                    sonidoMenu.play()
                    cuadradoEnY = cuadradoEnY + 50
                    if cuadradoEnY > salir:
                        cuadradoEnY = ((height/2)-50)
                if event.key == pygame.K_KP_ENTER:
                    sonidoMenu.play()
                    if cuadradoEnY == ((height/2)-50) :
                        sigueEnMenu = False
                    elif cuadradoEnY == ((height / 2)):
                        opciones(cuadradoEnX,cuadradoEnY,negro)
                    elif cuadradoEnY == ((height / 2)+50):
                        pygame.quit()
        # actualiza la pantalla
        pygame.display.update()
        screen.fill(negro)
def opciones(cuadradoEnX,cuadradoEnY,negro):
    sigueEnOpciones=True
    Video = int((height / 2) - 50)
    Atras = int((height / 2) + 50)
    while (sigueEnOpciones):
        pygame.draw.rect(screen, (255, 0, 0), (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        # Texto
        simple_show_text("Video", width / 2, (height / 2) - 50)
        simple_show_text("Sonido", width / 2, (height / 2))
        simple_show_text("Atras", width / 2, (height / 2) + 50)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sonidoMenu.play()
                    pygame.quit()
                if event.key == pygame.K_UP:
                    sonidoMenu.play()
                    cuadradoEnY -= 50
                    if cuadradoEnY < Video:
                        cuadradoEnY = ((height / 2) + 50)
                if event.key == pygame.K_DOWN:
                    sonidoMenu.play()
                    cuadradoEnY = cuadradoEnY + 50
                    if cuadradoEnY > Atras:
                        cuadradoEnY = ((height / 2) - 50)
                if event.key == pygame.K_KP_ENTER:
                    sonidoMenu.play()
                    if cuadradoEnY == ((height / 2) - 50):
                        sigueEnOpciones = False
                    elif cuadradoEnY == ((height / 2)):
                        cuadradoEnY = (height / 2) - 50

                    elif cuadradoEnY == ((height / 2) + 50):
                        sigueEnOpciones = False
        # actualiza la pantalla
        pygame.display.update()
        screen.fill(negro)
#Bucle principal...................................................................../
enProceso = True
def game():
    player.hp=200
    player.nivel=1
    player.misiles=3
    misilNuevo=0
    player.puntaje=0
    ultimoMisil=0   
    y=700
    all_sprites.add(player)
    game_over=False
    completado=False
    tiempoFinal=int(pygame.time.get_ticks())/500
  
    while not game_over :
        tiempoTranscurrido=int(pygame.time.get_ticks())/500-tiempoFinal


        for event in pygame.event.get():
            #Eventos teclado
            if event.type == pygame.KEYDOWN:
                # tanque rojo!!!
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_LEFT:
                    player.speed_x = -3
                    player.image = pygame.image.load("assets/player_left.png").convert()
                    player.image.set_colorkey(black)
                if event.key == pygame.K_RIGHT: 
                    player.speed_x = 3
                    player.image = pygame.image.load("assets/player_right.png").convert()
                    player.image.set_colorkey(black)
                if event.key == pygame.K_UP:
                    player.speed_y = -3
                    player.image = pygame.image.load("assets/player.png").convert()     
                    player.image.set_colorkey(black)
                if event.key == pygame.K_DOWN: 
                    player.speed_y = 3   
                    player.image = pygame.image.load("assets/player_down.png").convert()     
                    player.image.set_colorkey(black)
                if event.key == pygame.K_SPACE:
                        #creación del disparo
                        if(player.misiles>0):
                            if(int(tiempoTranscurrido)-int(ultimoMisil)>15):
                                player.puntaje=player.puntaje-((int(tiempoTranscurrido)-int(ultimoMisil))*300)
                            shoot = Shooting()   
                            shoot.rect.x = player.rect.x +10
                            shoot.rect.y = player.rect.y -20
                            all_sprites.add(shoot)
                            shoot_list.add(shoot)
                            shoot_sound.play() 
                            player.misiles=player.misiles-1
                            misilNuevo=tiempoTranscurrido
                            ultimoMisil=tiempoTranscurrido
                            
            if event.type == pygame.KEYUP:
                # tanque rojo!!!
                if event.key == pygame.K_LEFT:
                    player.speed_x = 0
                if event.key == pygame.K_RIGHT:
                    player.speed_x = 0
                if event.key == pygame.K_UP:
                    player.speed_y = 0
                if event.key == pygame.K_DOWN:
                    player.speed_y = 0    
                
    #control del jugador dentro del escenario
        if player.rect.right > 800:
            player.rect.right = 800
        if player.rect.left < 200:
            player.rect.left = 200  
        if player.rect.top < 0:
            player.rect.top = 0
        if player.rect.bottom > height:
            player.rect.bottom = height    

        #fondo y movimiento de la imagen de fondo
        y_relativa = y % background.get_rect().height
        screen.blit(background,(0,y_relativa-background.get_rect().height))
        if y_relativa < height: 
            screen.blit(background,(0,y_relativa))
        y += 1*3

        #actualización del movimiento del tanque rojo
        player.rect.x += player.speed_x
        player.rect.y += player.speed_y
        
        #actualización del movimiento vertical de todos los tanques
        for i in tank_red_list:
            i.rect.y += i.speed_y*4
    
        for i in tank_green_list:
            i.rect.y += i.speed_y*4

        #colisiones del disparo con los tanques rojos
        for i in shoot_list:
            shoot_hits_list = pygame.sprite.spritecollide(shoot,tank_red_list,True)
            for i in shoot_hits_list:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)
                explosion.play() 
                death = Death(i.rect.x,i.rect.y)
                death.animate()
                all_sprites.add(death)
                player.puntaje=player.puntaje+200
            if shoot.rect.y < -10:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)

        #colisiones del disparo con las tanques verdes
        for i in shoot_list:
            shoot_hits_list = pygame.sprite.spritecollide(shoot,tank_green_list,len(tank_red_list)==0)
            for i in shoot_hits_list:
                all_sprites.remove(shoot)
                shoot_list.remove(shoot)
                if(len(tank_red_list)>0):
                    iron_sound.play()
                if(len(tank_red_list)==0):
                    player.puntaje=player.puntaje+500
                    death = Death(i.rect.x,i.rect.y)
                    death.animate()
                    all_sprites.add(death)
                    explosion.play() 

        #colisión del player con los tanques
        for i in tank_red_list:
            crash_list = pygame.sprite.spritecollide(player,tank_red_list,True)  
            if len(crash_list) == 1:
                explosion.play()     
            for i in crash_list:   
                player.hp=player.hp-20         
                death = Death(player.rect.x,player.rect.y)
                death.animate()
                all_sprites.add(death)
                if(player.hp<=0): 
                    all_sprites.remove(player)
                    game_over=True
                    if(game_over):
                        font2 = pygame.font.SysFont(None, 100)
                        text1 = font2.render("GAME OVER", False, (255,0,0))
                        text_rect = text1.get_rect(center=(width/2, height/2))
                        screen.blit(text1, text_rect)
            
        for i in tank_green_list:   #revisar como optimizar las dos listas!!!
            crash_list = pygame.sprite.spritecollide(player,tank_green_list,True)  
            if len(crash_list) == 1:
                explosion.play()     
            for i in crash_list: 
                player.hp=player.hp-40 
                death = Death(player.rect.x,player.rect.y)
                death.animate()
                all_sprites.add(death)
                if(player.hp<=0):   
                    all_sprites.remove(player)
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

    #Bucle principal.....................................................................................\

    #Los misiles se incrementan cada 3 segundos
        if(tiempoTranscurrido-misilNuevo>3):
            player.misiles=player.misiles+1
            misilNuevo=tiempoTranscurrido
    #Cuando se eliminen todos los tanques se incrementa el nivel 
    #y se hace un bonus de misiles y energía.
        if(len(tank_green_list)==0 and len(tank_red_list)==0):
            player.nivel=player.nivel+1
            completado=True
            player.hp=player.hp+100
            player.misiles=player.misiles+3
    #Cada vez que se incrementa el nivel se crean más tanques
        if(player.nivel>1 and completado):
            completado=False
            for i in range(player.nivel+2):
                tank_green = Tank_green()
                tank_green_list.add(tank_green)
                all_sprites.add(tank_green)
            for i in range(player.nivel+4):
                tank_red = Tank()    
                tank_red_list.add(tank_red)
                all_sprites.add(tank_red)
        #Texto
        show_text("Energia: ", player.hp,0,60,140,60)
        show_text("Misiles: ", player.misiles, 0,120,140,120)
        show_text("Nivel: ", player.nivel,0,180,140,180)
        show_text("Puntaje: ", player.puntaje,0,240,140,240)
        #actualiza la pantalla
        pygame.display.flip()
        
        fps.tick(60)



while(enProceso):
    pygame.time.wait(3000)
    init()
    menu()
    game()




