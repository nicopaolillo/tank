import pygame

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