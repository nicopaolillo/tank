import pygame, time, sys, random
pygame.init()
pygame.mixer.init()
width = 1000
height = 700
white = (255,255,255)
black = (0,0,0)
sand_color = (195,169,139)
#Crea la ventana/fps!!!
screen = pygame.display.set_mode((width,height))
fps = pygame.time.Clock()

#carga de efectos de sonido
engine = pygame.mixer.Sound("sound/engine.ogg")
explosion = pygame.mixer.Sound("sound/explosion.ogg")
shoot_sound = pygame.mixer.Sound("sound/shoot.ogg")

#clases......................................................................../

class player(pygame.sprite.Sprite):
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
  #  def update(self):
  #     engine.play()      

class shooting(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/bullet.png").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
  
    def update(self):
        self.rect.y -= 3    
        
class box(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/asset_wood.png").convert()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(height - 350)
        self.speed_y = 3

   #funcionalidad para que se vuelva a generar la caja al salir del mapa
    def update (self):
        if self.rect.y > height:
            self.rect.y = -10
            self.rect.x = random.randrange(width)     
#clases.................................................................................................\

#creación de listas
box_list = pygame.sprite.Group()
shoot_list = pygame.sprite.Group()
crash_list = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

#creación del jugador con clase player
red_tank = player()

#creación cajas de madera
for i in range(10):
    box_wood = box()

#guardo las cajas en una lista
    box_list.add(box_wood)
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
                 shoot = shooting()   
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
    if red_tank.rect.right > width:
        red_tank.rect.right = width
    if red_tank.rect.left < 0:
        red_tank.rect.left = 0  
    if red_tank.rect.top < 0:
        red_tank.rect.top = 0
    if red_tank.rect.bottom > height:
        red_tank.rect.bottom = height    
         
    #pinto la pantalla   
    screen.fill(sand_color)

    #actualización del movimiento del tanque rojo
    red_tank.rect.x += red_tank.speed_x
    red_tank.rect.y += red_tank.speed_y
    
    #actualización del movimiento vertical de todas las cajas
    for i in box_list:
        i.rect.y += i.speed_y
  
    #colisiones del disparo con las cajas
    for i in shoot_list:
        shoot_hits_list = pygame.sprite.spritecollide(shoot,box_list,True)
        for i in shoot_hits_list:
            all_sprites.remove(shoot)
            shoot_list.remove(shoot)
        if shoot.rect.y < -10:
            all_sprites.remove(shoot)
            shoot_list.remove(shoot)
   
    #colisión del tanque con cajas    

    for i in box_list:
        crash_list = pygame.sprite.spritecollide(red_tank,box_list,True)  
        if len(crash_list) == 1:
            explosion.play()      
        for i in crash_list: 
           all_sprites.remove(red_tank) 
          # red_tank.image = pygame.image.load("explosion_5.png").convert()  
           
     
    #todos los metodos update de los objetos de esta lista funcionando
    all_sprites.update()
    #dibujo en la pantalla
    all_sprites.draw(screen)

#Bucle principal.....................................................................................\
   
    #actualiza la pantalla
    pygame.display.flip()
    fps.tick(60)