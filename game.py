import pygame
import time
import sys
import random

from entities.Player import Player
from entities.Tank import Tank, Tank_green
from entities.Death import Death
from entities.AirSupport import AirSupport
from entities.Shooting import Shooting

from resources.Hud import Hud
from GameContext import GameContext
from config.Settings import (
    GameConfig, WIDTH, HEIGHT, BLACK, GREEN_TEXT, DARK_GREEN_TEXT, RED_TEXT,
    PLAYER_SPEED, PLAYER_BOUNDS_LEFT, PLAYER_BOUNDS_RIGHT,
    PLAYER_INITIAL_HP, PLAYER_INITIAL_LEVEL, PLAYER_INITIAL_MISSILES, PLAYER_INITIAL_SUPPORT,
    MISSILE_RECHARGE_TIME, MISSILE_SCORE_PENALTY_PER_SECOND, MISSILE_FIRE_COOLDOWN,
    TARGET_FPS, GAME_LOOP_DELAY, BACKGROUND_IMAGE,
    TANK_RED_HIT_DAMAGE, TANK_GREEN_HIT_DAMAGE, TANK_RED_KILL_POINTS, TANK_GREEN_KILL_POINTS,
    AIR_SUPPORT_RED_POINTS, AIR_SUPPORT_GREEN_POINTS
)


# Create global config instance (will be used throughout the game)
config: GameConfig = None


def simple_show_text(config, string, position1, position2):
    text1 = config.font_small.render(string, True, GREEN_TEXT)
    config.screen.blit(text1, (position1, position2))

def show_text(config, string, int_value, position1, position2, position3, position4):
    text1 = config.font_small.render(string, True, GREEN_TEXT)
    config.screen.blit(text1, (position1, position2))
    text2 = config.font_small.render(str(int_value), True, GREEN_TEXT)
    config.screen.blit(text2, (position3, position4))

def gameOver(config):
    config.gameover_channel.play(config.get_sound('gameover'), loops=0, fade_ms=0)
    text1 = config.font_large.render("GAME OVER", True, RED_TEXT)
    text_rect = text1.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    config.screen.blit(text1, text_rect)
    config.game_channel.stop()

def Pause(config):
    shape_surf = pygame.Surface(pygame.Rect((0, 0, WIDTH, HEIGHT)).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, (0, 0, 0, 127), shape_surf.get_rect())
    shape_surf.set_alpha(128)
    config.screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
    text1 = config.font_large.render("PAUSA", True, DARK_GREEN_TEXT)
    text2 = config.font_small.render("Pulse p para continuar", True, DARK_GREEN_TEXT)
    text_rect = text1.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    text_rect2 = text2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
    config.screen.blit(text1, text_rect)
    config.screen.blit(text2, text_rect2)



#Menu del juego....................................................................../
def menu(config):
    config.main_channel.play(config.get_sound('menu'), loops=-1, fade_ms=100)
    sigueEnMenu = True
    cuadradoEnX = int(WIDTH / 2)
    cuadradoEnY = int((HEIGHT / 2) - 50)
    jugar = int((HEIGHT / 2) - 50)
    salir = int((HEIGHT / 2) + 50)
    negro = pygame.image.load("assets/main.png")
    
    while sigueEnMenu:
        pygame.draw.rect(config.screen, RED_TEXT, (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        Hud.simpleShowText(config.screen, config.font_small, "Jugar", WIDTH / 2, (HEIGHT / 2) - 50)
        simple_show_text(config, "Opciones", WIDTH / 2, (HEIGHT / 2))
        simple_show_text(config, "Salir", WIDTH / 2, (HEIGHT / 2) + 50)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    config.get_sound('select').play()
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_UP:
                    config.get_sound('select').play()
                    cuadradoEnY -= 50
                    if cuadradoEnY < jugar:
                        cuadradoEnY = ((HEIGHT / 2) + 50)
                if event.key == pygame.K_DOWN:
                    config.get_sound('select').play()
                    cuadradoEnY = cuadradoEnY + 50
                    if cuadradoEnY > salir:
                        cuadradoEnY = ((HEIGHT / 2) - 50)
                if event.key == pygame.K_RETURN:
                    config.get_sound('select').play()
                    if cuadradoEnY == ((HEIGHT / 2) - 50):
                        config.main_channel.stop()
                        config.game_channel.play(config.get_sound('game'), loops=-1, fade_ms=100)
                        sigueEnMenu = False
                    elif cuadradoEnY == ((HEIGHT / 2)):
                        opciones(config, cuadradoEnX, cuadradoEnY)
                    elif cuadradoEnY == ((HEIGHT / 2) + 50):
                        pygame.quit()
                        sys.exit()
        
        config.screen.blit(negro, (0, 0))
        pygame.draw.rect(config.screen, RED_TEXT, (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        Hud.simpleShowText(config.screen, config.font_small, "Jugar", WIDTH / 2, (HEIGHT / 2) - 50)
        simple_show_text(config, "Opciones", WIDTH / 2, (HEIGHT / 2))
        simple_show_text(config, "Salir", WIDTH / 2, (HEIGHT / 2) + 50)
        pygame.display.update()

def opciones(config, cuadradoEnX, cuadradoEnY):
    sigueEnOpciones = True
    opcionesFondo = pygame.image.load("assets/options.png")
    config.main_channel.stop()
    config.options_channel.play(config.get_sound('options'), loops=-1, fade_ms=100)
    Video = int((HEIGHT / 2) - 50)
    Atras = int((HEIGHT / 2) + 50)
    
    while sigueEnOpciones:
        config.screen.blit(opcionesFondo, (0, 0))
        pygame.draw.rect(config.screen, RED_TEXT, (cuadradoEnX, cuadradoEnY, 150, 30), 1)
        simple_show_text(config, "Video", WIDTH / 2, (HEIGHT / 2) - 50)
        simple_show_text(config, "Sonido", WIDTH / 2, (HEIGHT / 2))
        simple_show_text(config, "Atrás", WIDTH / 2, (HEIGHT / 2) + 50)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    config.get_sound('select').play()
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_UP:
                    config.get_sound('select').play()
                    cuadradoEnY -= 50
                    if cuadradoEnY < Video:
                        cuadradoEnY = ((HEIGHT / 2) + 50)
                if event.key == pygame.K_DOWN:
                    config.get_sound('select').play()
                    cuadradoEnY = cuadradoEnY + 50
                    if cuadradoEnY > Atras:
                        cuadradoEnY = ((HEIGHT / 2) - 50)
                if event.key == pygame.K_RETURN:
                    config.get_sound('select').play()
                    if cuadradoEnY == ((HEIGHT / 2) - 50):
                        sigueEnOpciones = True
                    elif cuadradoEnY == ((HEIGHT / 2)):
                        sigueEnOpciones = True
                    elif cuadradoEnY == ((HEIGHT / 2) + 50):
                        config.options_channel.stop()
                        config.main_channel.play(config.get_sound('menu'), loops=-1, fade_ms=100)
                        sigueEnOpciones = False
        
        pygame.display.update()


#Extracciones de game()
def handlePlayerBounds(player):
    if player.rect.right > PLAYER_BOUNDS_RIGHT:
        player.rect.right = PLAYER_BOUNDS_RIGHT

    if player.rect.left < PLAYER_BOUNDS_LEFT:
        player.rect.left = PLAYER_BOUNDS_LEFT

    if player.rect.top < 0:
        player.rect.top = 0

    if player.rect.bottom > HEIGHT:
        player.rect.bottom = HEIGHT

def updateEnemyMovement(tank_red_list, tank_green_list):
    for tank in tank_red_list:
        tank.rect.y += tank.speed_y * 3.8

    for tank in tank_green_list:
        tank.rect.y += tank.speed_y * 3.8

def rechargeMissiles(player, tiempoTranscurrido, misilNuevo):
    if tiempoTranscurrido - misilNuevo > MISSILE_RECHARGE_TIME:
        player.misiles += 1
        misilNuevo = tiempoTranscurrido

    return misilNuevo

def checkLevelCompleted(player, tank_red_list, tank_green_list):
    if len(tank_green_list) == 0 and len(tank_red_list) == 0:

        player.nivel += 1
        player.hp += 100
        player.misiles += 3
        player.apoyo += 1

        return True

    return False

def spawnNextLevel(player, completado, tank_green_list, tank_red_list, all_sprites):
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

def handleRedTankCrash(config, player, tank_red_list, all_sprites):

    crash_list = pygame.sprite.spritecollide(
        player,
        tank_red_list,
        True)

    if len(crash_list) == 1:
        config.get_sound('explosion').play()

    for tank in crash_list:

        player.hp -= TANK_RED_HIT_DAMAGE

        death = Death(player.rect.x, player.rect.y)

        death.animate()

        all_sprites.add(death)

    return player.hp <= 0

def handleGreenTankCollision(config, player, tank_green_list, all_sprites):

    game_over = False

    crash_list = pygame.sprite.spritecollide(player, tank_green_list, True)

    if len(crash_list) == 1:
        config.get_sound('explosion').play()

    for tank in crash_list:

        player.hp -= TANK_GREEN_HIT_DAMAGE

        death = Death(player.rect.x, player.rect.y)

        death.animate()
        all_sprites.add(death)

        if player.hp <= 0:

            all_sprites.remove(player)
            game_over = True
            gameOver(config)

    return game_over

def handleRedTankShots(config, shoot_list, tank_red_list, all_sprites, player):

    for shoot in list(shoot_list):

        shoot_hits_list = pygame.sprite.spritecollide(shoot, tank_red_list, True)

        for tank in shoot_hits_list:

            all_sprites.remove(shoot)
            shoot_list.remove(shoot)

            config.get_sound('explosion').play()

            death = Death(tank.rect.x, tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += TANK_RED_KILL_POINTS

        if shoot.rect.y < -10:

            if shoot in all_sprites:
                all_sprites.remove(shoot)

            if shoot in shoot_list:
                shoot_list.remove(shoot)

def handleAirSupportCollisions(config, apoyo_list, tank_red_list, tank_green_list, all_sprites, player):

    for apoyo in list(apoyo_list):

        apoyo_hits_list = pygame.sprite.spritecollide(apoyo, tank_red_list, True)

        apoyo_hits_list2 = pygame.sprite.spritecollide(apoyo, tank_green_list, True)

        for tank in apoyo_hits_list:

            config.get_sound('explosion').play()

            death = Death(tank.rect.x, tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += AIR_SUPPORT_RED_POINTS

        for tank in apoyo_hits_list2:

            config.get_sound('explosion').play()

            death = Death(tank.rect.x, tank.rect.y)

            death.animate()

            all_sprites.add(death)

            player.puntaje += AIR_SUPPORT_GREEN_POINTS

        if apoyo.rect.y < -200:

            if apoyo in all_sprites:
                all_sprites.remove(apoyo)

            if apoyo in apoyo_list:
                apoyo_list.remove(apoyo)

def handleGreenTankShots(config, shoot_list, tank_green_list, tank_red_list, all_sprites, player):

    for shoot in list(shoot_list):

        shoot_hits_list = pygame.sprite.spritecollide(shoot, tank_green_list, len(tank_red_list) == 0)

        for tank in shoot_hits_list:

            if shoot in all_sprites:
                all_sprites.remove(shoot)

            if shoot in shoot_list:
                shoot_list.remove(shoot)

            if len(tank_red_list) > 0:

                config.get_sound('iron').play()

            else:

                player.puntaje += TANK_GREEN_KILL_POINTS

                death = Death(tank.rect.x, tank.rect.y)

                death.animate()

                all_sprites.add(death)

                config.get_sound('explosion').play()

def renderGame(config, player, all_sprites, game_over):

    if not game_over:

        all_sprites.update()
        all_sprites.draw(config.screen)

    Hud.showText(config.screen, config.font_small, "Energía: ", player.hp, 0, 60, 140, 60)

    show_text(config, "Misiles: ", player.misiles, 0, 120, 140, 120)

    show_text(config, "Nivel: ", player.nivel, 0, 180, 140, 180)

    show_text(config, "Puntaje: ", player.puntaje, 0, 240, 140, 240)

    show_text(config, "Apoyos: ", player.apoyo, 0, 300, 140, 300)

    pygame.display.flip()

def renderBackground(config, y):

    background = pygame.image.load(BACKGROUND_IMAGE).convert()
    y_relativa = y % background.get_rect().height

    config.screen.blit(
        background,
        (0, y_relativa - background.get_rect().height)
    )

    if y_relativa < HEIGHT:

        config.screen.blit(
            background,
            (0, y_relativa)
        )

    y += 1 * 2.8

    return y

def handlePlayerCollisions(config, player, tank_red_list, tank_green_list, all_sprites):

    if handleRedTankCrash(config, player, tank_red_list, all_sprites):

        all_sprites.remove(player)
        gameOver(config)

        return True

    if handleGreenTankCollision(config, player, tank_green_list, all_sprites):

        return True

    return False

def handleGameProgression(player, tiempoTranscurrido, misilNuevo, completado, tank_green_list, tank_red_list, all_sprites):

    misilNuevo = rechargeMissiles(player, tiempoTranscurrido, misilNuevo)

    if checkLevelCompleted(player, tank_red_list, tank_green_list):

        completado = True

    completado = spawnNextLevel(player, completado, tank_green_list, tank_red_list, all_sprites)

    return misilNuevo, completado


def handleKeyboardEvents(config, events, player, all_sprites, apoyo_list, shoot_list, tiempoTranscurrido, misilNuevo, ultimoMisil, pause):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_p:
                pause = not pause
                if pause:
                    Pause(config)
                    pygame.display.flip()
            elif event.key == pygame.K_LEFT:
                player.speed_x = -PLAYER_SPEED
                player.image = config.get_player_sprite('left')
            elif event.key == pygame.K_RIGHT:
                player.speed_x = PLAYER_SPEED
                player.image = config.get_player_sprite('right')
            elif event.key == pygame.K_UP:
                player.speed_y = -PLAYER_SPEED
                player.image = config.get_player_sprite('default')
            elif event.key == pygame.K_DOWN:
                player.speed_y = PLAYER_SPEED
                player.image = config.get_player_sprite('down')
            elif event.key == pygame.K_q:
                if player.apoyo > 0:
                    apoyo = AirSupport()
                    apoyo.rect.x = player.rect.x + 10
                    apoyo.rect.y = HEIGHT
                    all_sprites.add(apoyo)
                    apoyo_list.add(apoyo)
                    player.apoyo -= 1
            elif event.key == pygame.K_SPACE:
                if player.misiles > 0:
                    if int(tiempoTranscurrido) - int(ultimoMisil) > MISSILE_FIRE_COOLDOWN:
                        player.puntaje = player.puntaje - ((int(tiempoTranscurrido) - int(ultimoMisil)) * MISSILE_SCORE_PENALTY_PER_SECOND)
                    shoot = Shooting()
                    shoot.rect.x = player.rect.x + 10
                    shoot.rect.y = player.rect.y - 20
                    all_sprites.add(shoot)
                    shoot_list.add(shoot)
                    config.get_sound('shoot').play()
                    player.misiles -= 1
                    misilNuevo = tiempoTranscurrido
                    ultimoMisil = tiempoTranscurrido
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player.speed_x = 0
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                player.speed_y = 0

    return misilNuevo, ultimoMisil, pause

#Bucle principal...................................................................../
enProceso = True
def game(config):
    context = GameContext(config)
    player = context.player

    all_sprites = context.all_sprites

    tank_red_list = context.tank_red_list
    tank_green_list = context.tank_green_list

    shoot_list = context.shoot_list
    apoyo_list = context.apoyo_list
    crash_list = context.crash_list

    context.reset_player_state()
    misilNuevo = 0
    ultimoMisil = 0   
    y = 700
    game_over = False
    completado = False
    tiempoFinal = int(pygame.time.get_ticks()) / 500
    pause = False
  
    while not game_over:
        if not pause:
            tiempoTranscurrido = int(pygame.time.get_ticks()) / 500 - tiempoFinal
        events = pygame.event.get()
        misilNuevo, ultimoMisil, pause = handleKeyboardEvents(
            config,
            events,
            player,
            all_sprites,
            apoyo_list,
            shoot_list,
            tiempoTranscurrido,
            misilNuevo,
            ultimoMisil,
            pause,
        )

        #control del jugador dentro del escenario
        handlePlayerBounds(player)    

        #fondo y movimiento de la imagen de fondo
        #se encapsula todas las actualizaciones de sprites condicionados por el estado de "pause"
        if not pause:
            #renderizado del fondo y movimiento del mismo
            y = renderBackground(config, y)

            #actualización del movimiento del tanque rojo
            updatePlayerMovement(player)
        
            #actualización del movimiento vertical de todos los tanques
            updateEnemyMovement(tank_red_list, tank_green_list)

            #colisiones del disparo con los tanques rojos
            handleRedTankShots(config, shoot_list, tank_red_list, all_sprites, player)

            #Colisiones del apoyo con tanques
            handleAirSupportCollisions(config, apoyo_list, tank_red_list, tank_green_list, all_sprites, player) 

            #colisiones del disparo con las tanques verdes
            handleGreenTankShots(config, shoot_list, tank_green_list, tank_red_list, all_sprites, player)
            
            #colisión del player con los tanques
            game_over = handlePlayerCollisions(config, player, tank_red_list, tank_green_list, all_sprites)

            #todos los metodos update de los objetos de esta lista funcionando
            renderGame(config, player, all_sprites, game_over)

    #Bucle principal.....................................................................................\

    #Los misiles se incrementan cada 3 segundos
        misilNuevo, completado = handleGameProgression(player, tiempoTranscurrido, misilNuevo, completado, tank_green_list, tank_red_list, all_sprites)
            
    #actualiza la pantalla
        config.clock.tick(TARGET_FPS) 
        
while enProceso:
    pygame.time.wait(GAME_LOOP_DELAY)
    config = GameConfig()
    menu(config)
    game(config)