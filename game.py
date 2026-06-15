import pygame, time, sys, random
from pygame import QUIT
from pygame.mixer import pre_init

from entities.Player import Player
from entities.Tank import Tank, Tank_green
from entities.Death import Death
from entities.AirSupport import AirSupport
from entities.Shooting import Shooting

from resources.Hud import Hud
from GameContext import GameContext

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
#creación de canales de música
game_channel = pygame.mixer.Channel(0)
options_channel = pygame.mixer.Channel(1)
main_channel = pygame.mixer.Channel(2)
gameover_channel = pygame.mixer.Channel(3)
#carga de efectos de sonido y música
game_channel_sound = pygame.mixer.Sound("sound/song.ogg")
options_channel_sound = pygame.mixer.Sound("sound/options.ogg")
main_channel_sound = pygame.mixer.Sound("sound/main.ogg")
gameover_channel_sound = pygame.mixer.Sound("sound/gameover.ogg")
engine = pygame.mixer.Sound("sound/engine.ogg")
explosion = pygame.mixer.Sound("sound/explosion.ogg")
shoot_sound = pygame.mixer.Sound("sound/shoot.ogg")
iron_sound = pygame.mixer.Sound("sound/iron_sound.ogg")
sonidoMenu = pygame.mixer.Sound('sound/selection.ogg')

#Fuente y tamaño de las letras
font = pygame.font.SysFont(None, 40)
font2 = pygame.font.SysFont(None, 100)



def simple_show_text(string,position1, position2):
    text1 = font.render(string, True, (173,255,47))
    screen.blit(text1, (position1,position2))

def show_text(string, int, position1, position2, position3, position4):
    text1 = font.render(string, True, (173,255,47))
    screen.blit(text1, (position1,position2))
    text2 = font.render(str(int), True, (173,255,47))
    screen.blit(text2, (position3,position4))

def gameOver():
    gameover_channel.play(gameover_channel_sound, loops=0, fade_ms=0)
    text1 = font2.render("GAME OVER", True, (255,0,0))
    text_rect = text1.get_rect(center=(width/2, height/2))
    screen.blit(text1, text_rect)
    game_channel.stop()

def Pause(surface): #Pausa dibuja un rectangulo negro con baja opacidad en la pantalla
    shape_surf = pygame.Surface(pygame.Rect((0, 0, width, height)).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, (0,0,0, 127), shape_surf.get_rect())
    shape_surf.set_alpha(128)
    surface.blit(shape_surf, (0, 0, width, height))
    text1 = font2.render("PAUSA", True, (0,143,57))
    text2 = font.render("Pulse p para continuar", True, (0,143,57))
    text_rect = text1.get_rect(center=(width/2, height/2))
    text_rect2 = text2.get_rect(center=(width/2, height/2+50))
    screen.blit(text1, text_rect)
    screen.blit(text2, text_rect2)



#Menu del juego....................................................................../
"""Texto en la mitad mas 50 para arriba y 50 para abajo.Posicion de los cuadrados que marcan que
opcion estas eligiendo va a ser lo mismo, para tener una referencia y despues un event
que vaya manejando la variable
width = 1000
height = 700"""
def menu():
    main_channel.play(main_channel_sound, loops=-1, fade_ms=100)
    sigueEnMenu= True
    cuadradoEnX = int(width/2)
    cuadradoEnY = int((height/2)-50)
    jugar=int((height/2)-50)
    salir= int((height/2)+50)
    negro= pygame.image.load("assets/main.png")
    #cuadrado = pygame.Rect(cuadradoEnX, cuadradoEnY, 150, 30)
    while(sigueEnMenu):
        pygame.draw.rect(screen, (255, 0, 0), (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        # Texto
        Hud.simpleShowText(screen,font,"Jugar",width / 2,(height / 2) - 50)
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
                if event.key == pygame.K_RETURN:
                    sonidoMenu.play()
                    if cuadradoEnY == ((height/2)-50) :
                        main_channel.stop()
                        game_channel.play(game_channel_sound, loops=-1, fade_ms=100)
                        sigueEnMenu = False
                    elif cuadradoEnY == ((height / 2)):
                        opciones(cuadradoEnX,cuadradoEnY)
                    elif cuadradoEnY == ((height / 2)+50):
                        pygame.quit()
        # actualiza la pantalla
        pygame.display.update()
        screen.blit(negro, (0,0))
def opciones(cuadradoEnX,cuadradoEnY):
    sigueEnOpciones=True
    opcionesFondo = pygame.image.load("assets/options.png")
    main_channel.stop()
    options_channel.play(options_channel_sound, loops=-1, fade_ms=100)
    Video = int((height / 2) - 50)
    Atras = int((height / 2) + 50)
    while (sigueEnOpciones):
        pygame.draw.rect(screen, (255, 0, 0), (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        # Texto
        simple_show_text("Video", width / 2, (height / 2) - 50)
        simple_show_text("Sonido", width / 2, (height / 2))
        simple_show_text("Atrás", width / 2, (height / 2) + 50)

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
                if event.key == pygame.K_RETURN:
                    sonidoMenu.play()
                    if cuadradoEnY == ((height / 2) - 50):
                        sigueEnOpciones = True
                    elif cuadradoEnY == ((height / 2)):
                        sigueEnOpciones = True
                    elif cuadradoEnY == ((height / 2) + 50):
                        options_channel.stop()
                        main_channel.play(main_channel_sound, loops=-1, fade_ms=100)
                        sigueEnOpciones = False
        # actualiza la pantalla
        pygame.display.update()
        screen.blit(opcionesFondo, (0,0))


#Extracciones de game()
def handlePlayerBounds(player, height):

    if player.rect.right > 800:
        player.rect.right = 800

    if player.rect.left < 200:
        player.rect.left = 200

    if player.rect.top < 0:
        player.rect.top = 0

    if player.rect.bottom > height:
        player.rect.bottom = height

def updateEnemyMovement(tank_red_list, tank_green_list):

    for tank in tank_red_list:
        tank.rect.y += tank.speed_y * 3.8

    for tank in tank_green_list:
        tank.rect.y += tank.speed_y * 3.8

def rechargeMissiles(player, tiempoTranscurrido, misilNuevo):

    if tiempoTranscurrido - misilNuevo > 3:
        player.misiles += 1
        misilNuevo = tiempoTranscurrido

    return misilNuevo

def checkLevelCompleted(
        player,
        tank_red_list,
        tank_green_list):

    if len(tank_green_list) == 0 and len(tank_red_list) == 0:

        player.nivel += 1
        player.hp += 100
        player.misiles += 3
        player.apoyo += 1

        return True

    return False

def spawnNextLevel(
        player,
        completado,
        tank_green_list,
        tank_red_list,
        all_sprites):

    if player.nivel > 1 and completado:

        completado = False

        for _ in range(player.nivel + 2):
            tank_green = Tank_green()
            tank_green_list.add(tank_green)
            all_sprites.add(tank_green)

        for _ in range(player.nivel + 4):
            tank_red = Tank()
            tank_red_list.add(tank_red)
            all_sprites.add(tank_red)

    return completado

def updatePlayerMovement(player):

    player.rect.x += player.speed_x
    player.rect.y += player.speed_y

def handleRedTankCrash(
        player,
        tank_red_list,
        all_sprites,
        explosion):

    crash_list = pygame.sprite.spritecollide(
        player,
        tank_red_list,
        True)

    if len(crash_list) == 1:
        explosion.play()

    for tank in crash_list:

        player.hp -= 20

        death = Death(
            player.rect.x,
            player.rect.y)

        death.animate()

        all_sprites.add(death)

    return player.hp <= 0

def handleGreenTankCollision(
        player,
        tank_green_list,
        all_sprites):

    game_over = False

    crash_list = pygame.sprite.spritecollide(
        player,
        tank_green_list,
        True)

    if len(crash_list) == 1:
        explosion.play()

    for tank in crash_list:

        player.hp -= 40

        death = Death(
            player.rect.x,
            player.rect.y)

        death.animate()
        all_sprites.add(death)

        if player.hp <= 0:

            all_sprites.remove(player)
            game_over = True
            gameOver()

    return game_over

def handleRedTankShots(
        shoot_list,
        tank_red_list,
        all_sprites,
        player):

    for shoot in list(shoot_list):

        shoot_hits_list = pygame.sprite.spritecollide(
            shoot,
            tank_red_list,
            True)

        for tank in shoot_hits_list:

            all_sprites.remove(shoot)
            shoot_list.remove(shoot)

            explosion.play()

            death = Death(
                tank.rect.x,
                tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += 200

        if shoot.rect.y < -10:

            if shoot in all_sprites:
             all_sprites.remove(shoot)

            if shoot in shoot_list:
             shoot_list.remove(shoot)

def handleAirSupportCollisions(
        apoyo_list,
        tank_red_list,
        tank_green_list,
        all_sprites,
        player):

    for apoyo in list(apoyo_list):

        apoyo_hits_list = pygame.sprite.spritecollide(
            apoyo,
            tank_red_list,
            True)

        apoyo_hits_list2 = pygame.sprite.spritecollide(
            apoyo,
            tank_green_list,
            True)

        for tank in apoyo_hits_list:

            explosion.play()

            death = Death(
                tank.rect.x,
                tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += 200

        for tank in apoyo_hits_list2:

            explosion.play()

            death = Death(
                tank.rect.x,
                tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += 300

        if apoyo.rect.y < -200:

            if apoyo in all_sprites:
                all_sprites.remove(apoyo)

            if apoyo in apoyo_list:
                apoyo_list.remove(apoyo)

#Bucle principal...................................................................../
enProceso = True
def game():
    player = context.player

    all_sprites = context.all_sprites

    tank_red_list = context.tank_red_list
    tank_green_list = context.tank_green_list

    shoot_list = context.shoot_list
    apoyo_list = context.apoyo_list
    crash_list = context.crash_list

    player.hp=200
    player.nivel=1
    player.misiles=3
    player.apoyo=1
    misilNuevo=0
    player.puntaje=0
    ultimoMisil=0   
    y=700
    all_sprites.add(player)
    game_over=False
    completado=False
    tiempoFinal=int(pygame.time.get_ticks())/500
    pause=False
  
    while not game_over :
        if not pause:
            tiempoTranscurrido=int(pygame.time.get_ticks())/500-tiempoFinal
        for event in pygame.event.get():
            #Eventos teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_p:
                    pause=not pause
                    Hud.pause(screen, font, font2, width, height)
                # tanque rojo!!!
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
                if event.key == pygame.K_q: 
                    if(player.apoyo>0):
                            apoyo = AirSupport()   
                            apoyo.rect.x = player.rect.x +10
                            apoyo.rect.y = height
                            all_sprites.add(apoyo)
                            apoyo_list.add(apoyo)
                            player.apoyo=player.apoyo-1

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
        handlePlayerBounds(player, height)    

        #fondo y movimiento de la imagen de fondo
        #se encapsula todas las actualizaciones de sprites condicionados por el estado de "pause"
        if not pause:
            y_relativa = y % background.get_rect().height
            screen.blit(background,(0,y_relativa-background.get_rect().height))
            if y_relativa < height: 
                screen.blit(background,(0,y_relativa))
            y += 1*(2.8)

            #actualización del movimiento del tanque rojo
            updatePlayerMovement(player)
        
            #actualización del movimiento vertical de todos los tanques
            updateEnemyMovement( tank_red_list,tank_green_list)

            #colisiones del disparo con los tanques rojos
            handleRedTankShots(shoot_list,tank_red_list,all_sprites,player)

            #Colisiones del apoyo con tanques
            handleAirSupportCollisions(apoyo_list,tank_red_list,tank_green_list,all_sprites,player) 

            #colisiones del disparo con las tanques verdes
            for shoot in list(shoot_list):
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
            if handleRedTankCrash(player,tank_red_list,all_sprites,explosion):
             all_sprites.remove(player)
             game_over = True
             gameOver()
                
            if handleGreenTankCollision(player,tank_green_list,all_sprites):
                game_over = True

            #todos los metodos update de los objetos de esta lista funcionando
            if(not game_over):
                all_sprites.update()
                #dibujo en la pantalla
                all_sprites.draw(screen)
            #Texto
            Hud.showText(screen,font,"Energía: ",player.hp, 0,60,140,60)
            show_text("Misiles: ", player.misiles, 0,120,140,120)
            show_text("Nivel: ", player.nivel,0,180,140,180)
            show_text("Puntaje: ", player.puntaje,0,240,140,240)
            show_text("Apoyos: ", player.apoyo,0,300,140,300)
            pygame.display.flip()

    #Bucle principal.....................................................................................\

    #Los misiles se incrementan cada 3 segundos
        misilNuevo = rechargeMissiles(player,tiempoTranscurrido,misilNuevo)

    #Cuando se eliminen todos los tanques se incrementa el nivel 
    #se hace un bonus de misiles,energia y apoyos.
        if checkLevelCompleted(player,tank_red_list,tank_green_list): 
            completado = True

    #Cada vez que se incrementa el nivel se crean más tanques
        completado = spawnNextLevel(player,completado,tank_green_list,tank_red_list,all_sprites)
            
    #actualiza la pantalla
        pygame.display.flip()
        fps.tick(60) 
        
while(enProceso):
    pygame.time.wait(3200)
    context = GameContext()
    menu()
    game()