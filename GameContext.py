import pygame

from entities.Player import Player
from entities.Tank import Tank
from entities.Tank import Tank_green

def init():
    global tank_red_list
    global tank_green_list
    global shoot_list
    global crash_list
    global apoyo_list
    global all_sprites
    global player
    global game_over
    global pause
    #creación de listas
    tank_red_list = pygame.sprite.Group()
    tank_green_list = pygame.sprite.Group()
    shoot_list = pygame.sprite.Group()
    crash_list = pygame.sprite.Group()
    apoyo_list=pygame.sprite.Group()
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