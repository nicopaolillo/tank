import pygame, time, sys, random
pygame.init()
pygame.mixer.init()
width = 1000
height = 700
white = (255,255,255)
black = (0,0,0)
sand_color = (195,169,139)
background = pygame.image.load("assets/background_2.png")
#este eje y trabaja con el background
y=700
#Crea la ventana/fps!!!
screen = pygame.display.set_mode((width,height))
fps = pygame.time.Clock()

#carga de efectos de sonido
engine = pygame.mixer.Sound("sound/engine.ogg")
explosion = pygame.mixer.Sound("sound/explosion.ogg")
shoot_sound = pygame.mixer.Sound("sound/shoot.ogg")
iron_sound = pygame.mixer.Sound("sound/iron_sound.ogg")

#clases......................................................................../

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  
        self.image = pygame.image.load("assets/red_tank.png").convert()     
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = width // 2
        self.rect.bottom = height -10
        self.speed_x = 0
        self.speed_y = 0   
    #sonido    no encontré la forma de que este sonido no me pise el de las explosiones (descomentar y probar)
    #def update(self):
    #   engine.play()      

class Death(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.sheet = pygame.image.load("assets/fire.png").convert()
        self.sheet.set_clip(pygame.Rect(0,0,180,200))
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.frame = 0  #buscar manera de crear una animación don los 9 recortes
        self.rect.x = x
        self.rect.y = y

class Shooting(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/bullet.png").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
  
    def update(self):
        self.rect.y -= 3    
        
class Box(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/asset_wood.png").convert()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200 , 700)
        self.rect.y = random.randrange(height - 350)
        self.speed_y = 1

   #funcionalidad para que se vuelva a generar la caja al salir del mapa
    def update (self):
        if self.rect.y > height:
            self.rect.y = -10
            self.rect.x = random.randrange(200,700) 
#clase hija
class Box_iron(Box):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/asset_iron.png").convert()

#clases.................................................................................................\

#creación de listas
box_wood_list = pygame.sprite.Group()
box_iron_list = pygame.sprite.Group()
shoot_list = pygame.sprite.Group()
crash_list = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

#instanciación del jugador con clase player
red_tank = Player()

#instanciación y guardado de cajas de acero
for i in range(1):
    box_iron = Box_iron()
    box_iron_list.add(box_iron)
    all_sprites.add(box_iron)

#instanciación y guardado de cajas de madera
for i in range(3):
    box_wood = Box()    
    box_wood_list.add(box_wood)
    all_sprites.add(box_wood)

#guardo el sprite del tanque una lista
all_sprites.add(red_tank)

#Condición para que corra el juego!!!
game_over = False

#Bucle principal...................................................................../
while not game_over :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
         game_over = True  
        #Eventos teclado
        if event.type == pygame.KEYDOWN:
            # tanque rojo!!!
           if event.key == pygame.K_LEFT:
               red_tank.speed_x = -3
               red_tank.image = pygame.image.load("assets/red_tank_left.png").convert()
               red_tank.image.set_colorkey(black)
           if event.key == pygame.K_RIGHT: 
               red_tank.speed_x = 3
               red_tank.image = pygame.image.load("assets/red_tank_rigth.png").convert()
               red_tank.image.set_colorkey(black)
           if event.key == pygame.K_UP:
               red_tank.speed_y = -3
               red_tank.image = pygame.image.load("assets/red_tank.png").convert()     
               red_tank.image.set_colorkey(black)
           if event.key == pygame.K_DOWN: 
               red_tank.speed_y = 3   
               red_tank.image = pygame.image.load("assets/red_tank_down.png").convert()     
               red_tank.image.set_colorkey(black)
           if event.key == pygame.K_SPACE:
                #creación del disparo
                 shoot = Shooting()   
                 shoot.rect.x = red_tank.rect.x +10
                 shoot.rect.y = red_tank.rect.y -20
                 all_sprites.add(shoot)
                 shoot_list.add(shoot)
                 shoot_sound.play() 

        if event.type == pygame.KEYUP:
            # tanque rojo!!!
            if event.key == pygame.K_LEFT:
               red_tank.speed_x = 0
            if event.key == pygame.K_RIGHT:
                red_tank.speed_x = 0
            if event.key == pygame.K_UP:
               red_tank.speed_y = 0
            if event.key == pygame.K_DOWN:
                red_tank.speed_y = 0    
            

   #control del jugador dentro del escenario
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
    y += 1

    #actualización del movimiento del tanque rojo
    red_tank.rect.x += red_tank.speed_x
    red_tank.rect.y += red_tank.speed_y
    
    #actualización del movimiento vertical de todas las cajas
    for i in box_wood_list:
        i.rect.y += i.speed_y
  
    for i in box_iron_list:
        i.rect.y += i.speed_y

    #colisiones del disparo con las cajas de madera
    for i in shoot_list:
        shoot_hits_list = pygame.sprite.spritecollide(shoot,box_wood_list,True)
        for i in shoot_hits_list:
            all_sprites.remove(shoot)
            shoot_list.remove(shoot)
        if shoot.rect.y < -10:
            all_sprites.remove(shoot)
            shoot_list.remove(shoot)

    #colisiones del disparo con las cajas de acero
    for i in shoot_list:
        shoot_hits_list = pygame.sprite.spritecollide(shoot,box_iron_list,False)
        for i in shoot_hits_list:
            all_sprites.remove(shoot)
            shoot_list.remove(shoot)
            iron_sound.play()

    #colisión del tanque con cajas    

    for i in box_wood_list:
        crash_list = pygame.sprite.spritecollide(red_tank,box_wood_list,True)  
        if len(crash_list) == 1:
            explosion.play()     
        for i in crash_list:   
           death = Death(red_tank.rect.x,red_tank.rect.y) 
           all_sprites.add(death)
           all_sprites.remove(red_tank)

    for i in box_iron_list:   #revisar como optimizar las dos listas!!!
        crash_list = pygame.sprite.spritecollide(red_tank,box_iron_list,True)  
        if len(crash_list) == 1:
            explosion.play()     
        for i in crash_list:   
           death = Death(red_tank.rect.x,red_tank.rect.y) 
           all_sprites.add(death)
           all_sprites.remove(red_tank)

    #todos los metodos update de los objetos de esta lista funcionando
    all_sprites.update()
    #dibujo en la pantalla
    all_sprites.draw(screen)

#Bucle principal.....................................................................................\
   
    #actualiza la pantalla
    pygame.display.flip()
    fps.tick(60)