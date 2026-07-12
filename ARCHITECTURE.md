# Tank Game — Documentación de Arquitectura

## 1. Descripción General

**Tank Game** es un videojuego de acción tipo arcade shooter desarrollado en **Python 3** con **Pygame**. El jugador controla un tanque, elimina oleadas de tanques enemigos rojos y verdes que caen desde arriba, acumula puntaje, sube de nivel, recolecta power-ups de escudo, enfrenta un jefe final (bombardero/barco) y accede a una tienda entre misiones para comprar mejoras (armadura, doble cañón, orugas).

---

## 2. Estructura del Proyecto

```
tank-master/
├── game.py                  # Punto de entrada principal
├── GameContext.py            # Estado global del juego
├── config/
│   └── Settings.py           # Constantes + clase GameConfig
├── entities/
│   ├── Player.py             # Tanque del jugador
│   ├── Tank.py               # Tanques enemigos (rojo y verde)
│   ├── Shooting.py           # Proyectiles del jugador
│   ├── AirSupport.py         # Apoyo aéreo (avión)
│   ├── Bombardier.py         # Jefe final (bombardero/barco)
│   ├── FinalBossBoat.py      # Variante del jefe final
│   ├── Death.py              # Animación de explosión
│   ├── SmokeTrail.py         # Estela de humo
│   └── ShieldPowerUp.py      # Power-up de escudo
├── gameplay/
│   ├── __init__.py
│   ├── player_controller.py  # Control del jugador (input, movimiento, disparo)
│   ├── enemy_manager.py      # Gestión de enemigos (spawn, actualización)
│   ├── collision_manager.py  # Detección de colisiones y daño
│   └── progression_manager.py # Progresión de niveles y recarga
├── sences/                   # Sistema de escenas (state)
│   ├── __init__.py
│   ├── Scene.py              # Clase base abstracta
│   ├── SceneManager.py       # Administrador de escenas (state machine)
│   ├── MenuScene.py          # Escena del menú principal
│   ├── OptionsScene.py       # Escena de opciones
│   ├── ControlsScene.py      # Escena de controles (entre tienda pre-partida y juego)
│   ├── ShopScene.py          # Escena de tienda (mejoras entre misiones)
│   └── GameScene.py          # Escena principal del juego
├── ui/
│   ├── __init__.py
│   └── hud.py                # HUD del juego
├── assets/                   # Sprites, fondos, animaciones
│   ├── background_menu.png
│   ├── background_lvl1_A.png ... D.png
│   ├── player_main.png, player_main_damaged.png, player_main_damaged_2.png
│   ├── player_armor.png, player_double_barrel.png, player_tank_track.png
│   ├── tank_red.png, tank_green.png, tank_green_damaged.png
│   ├── armor.png, double_barrel.png, tank_track.png
│   ├── avion.png, bullet.png, shieldArmy.png
│   ├── menu_shop.png
│   ├── TankExplosion/        # 15 frames de explosión (0001–0015)
│   ├── SmokeFrames/          # 24 frames de estela de humo
│   ├── bombardier_lvl1/      # Sprites del jefe bombardero
│   └── ...
└── sound/                    # 12 OGGs: engine, engine_2, explosion, gameover, iron_sound, main, options, plane, selection, shoot, shot_1, song
```

---

## 3. Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3 (type hints con `from __future__ import annotations`) |
| Framework gráfico | Pygame (SDL2 wrapper) |
| Sprites | PNG / JPG |
| Audio | OGG Vorbis (amplificados con ffmpeg para balancear niveles entre explosion / shoot / plane) |
| Entorno objetivo | Windows |

---

## 4. Patrones de Diseño

| Patrón | Ubicación |
|---|---|
| **State** | Sistema de escenas: `SceneManager` + `Scene` (MenuScene, GameScene, OptionsScene, ShopScene, ControlsScene) |
| **Singleton / Flyweight (caché)** | Atributos de clase `_frames_cache` en `Bombardier`, `FinalBossBoat`, `BoatProjectile`, `SmokeTrail`, `Death`, `HudManager` |
| **Game Loop** | `game.py`: eventos → update → render a 60 FPS |
| **Double Buffer** | Pygame: superficie virtual → escalado → ventana real |
| **Manager** | Controladores separados para input, enemigos, colisiones, progresión |
| **Componente** | `GameContext` como contenedor de estado global |

---

## 5. Flujo de Ejecución

### 5.1 Entry Point (`game.py`)

```python
config = GameConfig()
scene_manager = SceneManager(config)
menu_scene = MenuScene(config, scene_manager)
scene_manager.change_scene(menu_scene)

while True:
    events = pygame.event.get()
    scene_manager.handle_events(events)
    scene_manager.update(config.clock.get_time() / 1000.0)
    scene_manager.render()
    config.clock.tick(TARGET_FPS)  # 60 FPS
```

### 5.2 Ciclo por Frame

```
1. Eventos
   → SceneManager.handle_events(events)
      → GameScene.handle_events()
         → PlayerController.handle_keydown() / handle_keyup()
            → Modifica player.speed_x, .speed_y, .facing
            → Dispara proyectiles: Shooting() → shoot_list + all_sprites
            → Activa apoyo aéreo: AirSupport()
            → Activa escudo: player.activate_shield()

2. Update (dt)
   → GameScene.update(dt)
      → PlayerController.update() + clamp_bounds()
      → EnemyManager.update()            # mueve enemigos verticalmente, respawnea con separación
      → EnemyManager.try_enemy_shoot()   # disparo enemigo (nivel ≥ 4, 1-2 balas, cooldown 3s)
      → SmokeTrail generation            # estela detrás de entidades
      → CollisionManager.handle_*()      # 6 tipos de colisión
         → aplica daño (variable según tipo de bala/enemigo), suma puntaje, spawn Death(), reproduce sonidos
      → ProgressionManager.update()      # recarga misiles, sube nivel, spawn
      → Background scroll                # desplaza fondos en bucle
      → Bombardier spawn/update          # nivel >= 7 aparece el jefe

3. Render
   → GameScene.render()
      → Fondo (2 capas con scroll)
      → smoke_list.draw() + all_sprites.draw()
      → Escudo si activo
      → HudManager.draw_game_hud()       # HP, misiles, puntaje, HP jefe
      → config.present()                 # escala superficie virtual → ventana real
```

### 5.3 Transiciones de Escena

```
MenuScene (Jugar) → GameScene
MenuScene (Tienda) → ShopScene (pre-partida, sin player) → ControlsScene → GameScene (con mejora aplicada)
MenuScene (Opciones) → OptionsScene → (Atrás) → MenuScene
GameScene (Bombardier derrotado + 5s) → ShopScene (entre misiones, con player persistente)
ShopScene (mejora equipada + ENTER) → _render_selected() → ENTER → vuelve al menú
ShopScene (Atrás / DOWN + ENTER) → MenuScene
GameScene (Game Over + R) → GameScene (reinicio)
GameScene (ESC) → salir del juego
```

---

## 6. Componentes Principales

### 6.1 Config (`config/Settings.py`)

- **Constantes globales**: dimensiones (1000×700), colores, HP, velocidad, daño, puntajes, rutas de assets/sonidos. Constantes de disparo enemigo: `ENEMY_SHOOT_COOLDOWN=3.0`, `ENEMY_SHOOT_LEVEL_START=4`, `TANK_RED_SHOOT_DAMAGE=20`, `TANK_GREEN_SHOOT_DAMAGE=40`, `MAX_ENEMIES=6`.
- **Clase `GameConfig`**: inicializa Pygame, ventana, superficies de render, canales de audio, fuentes. Métodos auxiliares: `get_sound()`, `get_player_sprite()` (acepta `damage_state: str` para 3 niveles: normal, `'damaged'` ≤100 HP, `'damaged_2'` ≤50 HP), `present()` (escala y presenta el frame). Incluye sistema de volumen con tres niveles (master, música, efectos), más un dict `_sound_volumes` para ajustes finos por sonido (p.ej. `shoot` al 0.8).

### 6.2 Estado Global (`GameContext.py`)

Contenedor que inicializa:
- Grupos de sprites: `tank_red_list`, `tank_green_list`, `shoot_list`, `enemy_shoot_list`, `crash_list`, `apoyo_list`, `powerup_list`, `smoke_list`, `bombardier_list`, `all_sprites`
- Instancia del jugador (`Player`)
- `_preload_assets()`: fuerza la precarga de todos los assets pesados (frames de Bombardier, Death, SmokeTrail, proyectiles) para evitar micro-congelamientos durante la partida
- Método `reset_player_state()`: reinicia hp (`PLAYER_INITIAL_HP`), `max_hp`, `nivel`, `misiles`, `apoyo`, `puntaje` y resetea los flags de mejora (`double_barrel_active`, `armor_active`, `tank_track_active` a `False`)
- Los tanques iniciales NO se crean en el contexto; se spawnean desde `GameScene` tras un delay de 2 segundos

### 6.3 Sistema de Escenas (`sences/`)

- **`Scene`** — Abstract Base Class. Define interfaz: `handle_events()`, `update()`, `render()`, `on_activate()`, `on_deactivate()`.
- **`SceneManager`** — Mantiene la escena activa, delega eventos/update/render. `change_scene()` gestiona ciclo de vida.
- **`MenuScene`** — Menú con "Jugar", "Tienda", "Opciones", "Salir". Fondo con escalado cover, sonido de menú. "Tienda" abre `ShopScene` en modo pre-partida (sin estado de jugador).
- **`OptionsScene`** — Opciones principales ("Video", "Sonido", "Atrás"). Al seleccionar "Sonido" se despliega un submenú con controles de volumen: "general" (maestro), "música" (song.ogg, main.ogg, options.ogg, gameover.ogg), "efectos" (disparo, explosión, motor, avión, etc.) — cada uno con barra deslizadora ajustable con ←/→.
- **`ControlsScene`** — Pantalla de instrucciones/controles entre la tienda pre-partida y el juego. Acepta `pre_game_upgrade` opcional para aplicar la mejora comprada al nuevo `Player` al iniciar la partida.
- **`ShopScene`** — Tienda de mejoras (~260 líneas). Fondo `menu_shop.png` con escalado cover. 3 mejoras: Armadura (+200 HP, daño reducido 50%), Doble Cañón (2 proyectiles por disparo), Orugas (+50% velocidad). Navegación con ←/→, selector verde (`DARK_GREEN_TEXT`). Botón "Atrás" abajo a la derecha con ↓. Vista previa del tanque con mejora aplicada. Sonido engine.ogg en loop; al presionar ↑ suena `engine_2.ogg` y genera humo (SmokeTrail) detrás del tanque como preview visual. Al seleccionar una mejora, se aplica al `Player` y se muestra pantalla de confirmación.
- **`GameScene`** — Escena principal (~430 líneas). Orquesta todos los managers (PlayerController, EnemyManager, CollisionManager, ProgressionManager). Al inicio, espera 2 segundos antes de spawnear los primeros tanques (`_initial_spawn_timer`). Gestiona el sonido del motor en bucle según el movimiento del jugador (engine.ogg quieto / engine_2.ogg en movimiento). Llama `enemy_manager.try_enemy_shoot()` cada frame para el sistema de disparo enemigo. Al derrotar al Bombardier, inicia un contador de 5s mostrando "Misión 1 completada" y luego transiciona automáticamente a `ShopScene`.

### 6.4 Entidades (`entities/`)

Todas heredan de `pygame.sprite.Sprite`:

| Clase | Archivo | Propósito |
|---|---|---|
| `Player` | `Player.py` | Tanque del jugador: HP, `max_hp`, nivel, misiles, puntaje, escudos, movimiento, flags de mejora (`armor_active`, `double_barrel_active`, `tank_track_active`), `update_sprite()` elige sprite según mejora activa (prioridad: doble cañón > armadura > orugas > daño) |
| `Tank` | `Tank.py` | Tanque enemigo rojo. Se mueve verticalmente. Tiene `shoot_damage=20` y `last_fire_time` para el sistema de disparo enemigo |
| `Tank_green` | `Tank.py` | Tanque enemigo verde (hereda de Tank). Más daño al colisionar (40). Resiste 2 disparos: 1er impacto → sprite `tank_green_damaged.png` + sonido `iron_sound`, 2do impacto → explota. Tiene `shoot_damage=40` |
| `Shooting` | `Shooting.py` | Proyectil (del jugador o enemigo). Atributo `damage` para daño variable. Se destruye al salir de pantalla |
| `AirSupport` | `AirSupport.py` | Avión de apoyo aéreo que vuela hacia arriba |
| `Bombardier` | `Bombardier.py` | Jefe final (~730 líneas). Aparece desde arriba de la pantalla (`_entering`), desciende hasta su posición y luego comienza navegación horizontal + disparos. Escudo periódico (10 s entre activaciones, 3 s de duración) que lo vuelve inmune y se visualiza como óvalo naranja; al recibir impacto estando protegido suena `iron_sound` |
| `FinalBossBoat` | `FinalBossBoat.py` | Variante casi idéntica al Bombardier |
| `BoatProjectile` | `Bombardier.py` / `FinalBossBoat.py` | Proyectil del jefe. Animado, persigue al jugador |
| `BombardierSinkingEffect` | `Bombardier.py` | Efecto de hundimiento al derrotar al jefe |
| `Death` | `Death.py` | Animación de explosión (16 frames) |
| `SmokeTrail` | `SmokeTrail.py` | Estela de humo animada (24 frames) |
| `ShieldPowerUp` | `ShieldPowerUp.py` | Power-up de escudo que cae desde arriba |

### 6.5 Lógica de Juego (`gameplay/`)

| Clase | Archivo | Responsabilidad |
|---|---|---|
| `PlayerController` | `player_controller.py` | Input del teclado (movimiento, disparo, apoyo aéreo con sonido plane.ogg, escudo). `_get_speed()` aplica 1.5x si `tank_track_active`. Dispara 2 proyectiles si `double_barrel_active`. Restringe límites |
| `EnemyManager` | `enemy_manager.py` | Actualiza posición de enemigos. `spawn_level(level)` crea oleadas con tope de 6 tanques (min(level, 3) por color). Separa tanques horizontalmente al spawnear y al respawnear para evitar superposición. `try_enemy_shoot()` genera disparos enemigos desde nivel 4 (1 bala simultánea) y nivel 6+ (2 balas simultáneas), con cooldown de 3s entre ráfagas. `clear_all_enemies()` limpia tanques antes de spawnear nueva oleada |
| `CollisionManager` | `collision_manager.py` | Centraliza TODAS las colisiones (proyectiles vs enemigos, jugador vs enemigos, proyectiles enemigos vs jugador, power-ups, etc.). Los proyectiles enemigos (`Shooting`) usan daño por tipo (rojo=20, verde=40). Los `BoatProjectile` del bombardero mantienen `BOMBARDIER_PROJECTILE_DAMAGE=12`. Si `player.armor_active`, divide el daño recibido por 2 |
| `ProgressionManager` | `progression_manager.py` | Recarga misiles cada 3s. Detecta oleadas limpiadas, sube nivel, cura, spawn |

### 6.6 Interfaz de Usuario (`ui/hud.py`)

**`HudManager`** (métodos estáticos con caché de iconos):
- Dibuja: vida, misiles, apoyo aéreo, escudos, puntaje
- Barra de HP del bombardero
- Overlay de pausa y "Game Over"

---

## 7. Flujo de Datos (Data Flow)

### Combate / Colisiones

```
Player dispara → Shooting(damage=0) agregado a shoot_list + all_sprites
                     ↓
CollisionManager.handle_red_tank_shots() / handle_green_tank_shots()
  → detecta colisión shoot vs tank_red/tank_green
  → tank_red: destrucción inmediata (200 pts)
  → tank_green: 2 impactos necesarios
      → 1er impacto: sprite → tank_green_damaged.png + sonido iron_sound
      → 2do impacto: explota (puntaje 300, Death(), explosion.ogg)
  → elimina proyectil

Tanque enemigo dispara (nivel ≥ 4) →
EnemyManager.try_enemy_shoot()
  → nivel 4-5: 1 bala simultánea, cooldown 3s
  → nivel 6+: 2 balas simultáneas, cooldown 3s
  → Shooting("down", damage=tank.shoot_damage) → enemy_shoot_list
  → sonido shoot.ogg
                     ↓
CollisionManager._handle_enemy_projectile_collision()
  → daño según tipo: rojo=20, verde=40 (misma proporción que colisión física)
  → armor reduce daño 50%, escudo bloquea

Tanque enemigo colisiona con jugador →
CollisionManager.handle_player_vs_enemy()
  → tanque rojo: 20 de daño (40 sin armor)
  → tanque verde: 40 de daño (80 sin armor)
  → tanque destruido al colisionar
```

### Separación de Tanques

```
EnemyManager._find_non_overlapping_x()
  → al spawnear: cada tanque busca posición X con ≥130px de distancia a otros
  → al respawnear: tanque que sale por abajo reaparece arriba con X separada
  → fallback determinístico: si no encuentra posición tras 30 intentos,
     elige la con mayor separación mínima
```

### Inicio de Partida

```
GameScene.update() — primeros 2 segundos:
  → _initial_spawn_timer cuenta desde 2.0 hasta 0
  → durante este período: sin tanques en pantalla, sin progresión de nivel
  → al expirar: enemy_manager.spawn_level(1) → 1 verde + 1 rojo
  → a partir de ahí el flujo normal (progresión, oleadas, disparo enemigo)
```

### Progresión

```
ProgressionManager.update()
  → recarga 1 misil cada 3s si no está al máximo
  → si all_enemies_cleared():
      → incrementa nivel
      → otorga +3 misiles
      → EnemyManager.clear_all_enemies() + spawn_level(level)
      → tope: min(level, 3) por color → máximo 6 tanques desde nivel 3

Escalado de dificultad:
  → nivel 1: 1+1=2 tanques, sin disparo
  → nivel 2: 2+2=4 tanques, sin disparo
  → nivel 3+: 3+3=6 tanques (tope permanente)
  → nivel 4+: tanques disparan (1 bala, cooldown 3s)
  → nivel 6+: 2 balas simultáneas
  → nivel 7+: aparece Bombardier (jefe final)
```

### Jefe Final

```
Si nivel ≥ 7 y no hay jefe activo:
  → spawn Bombardier() en bombardier_list (comienza en y = -150)
  → mientras _entering: desciende verticalmente (speed 1.0), inmune al daño
  → al alcanzar _target_y: transiciona a comportamiento normal
     → se mueve horizontalmente, dispara BoatProjectile
     → escudo cíclico: 3 s activo / 7 s inactivo, visualizado como óvalo naranja
     → si escudo activo: disparos rebotan con sonido iron_sound, sin daño
   → CollisionManager.handle_shoot_vs_bombardier()
   → CollisionManager.handle_enemy_bullets()
   → al morir: BombardierSinkingEffect → animación de hundimiento
   → se activa _mission_complete_timer (5s), se muestra "Misión 1 completada"
   → al cumplirse el timer: transición a ShopScene (con el Player persistente)
```

---

## 8. Assets y Recursos

- **Sprites del jugador**: 4 orientaciones + 2 variantes dañadas (`player_main_damaged.png` ≤100 HP, `player_main_damaged_2.png` ≤50 HP) + 3 sprites de mejora (`player_armor.png`, `player_double_barrel.png`, `player_tank_track.png` con 4 orientaciones cada uno)
- **Tanques enemigos**: rojo (estándar, daño=20) y verde (más daño=40, sprite `tank_green_damaged.png` tras 1er impacto). Disparan desde nivel 4 usando el mismo asset `bullet.png` que el jugador
- **Fondos de nivel**: 4 variantes (lvl1_A .. D) con scroll en bucle
- **Animaciones**:
  - Explosión de tanque: 16 frames (`TankExplosion/`)
  - Estela de humo: 24 frames (`SmokeFrames/`)
  - Proyectil del jefe: 5 frames (`BoatShot/`)
  - Muerte del bombardero: animación en `BombardierDeathAnimation/`
- **Fondo de tienda**: `menu_shop.png` con escalado cover
- **Iconos de mejora**: `armor.png`, `double_barrel.png`, `tank_track.png`
- **Spritesheet del jefe**: JPG con procesamiento de eliminación de fondo (flood-fill via `pygame.surfarray`)
- **Sonido**: 12 OGGs — música (menu/song/options/gameover), motores (engine/engine_2 según movimiento), SFX (disparo para jugador y enemigos, explosión, escudo, selección, avión de apoyo aéreo, derrota). Volumen segmentado en 3 categorías (general, música, efectos) configurable desde el submenú de opciones.

---

## 9. Escalado y Renderizado

El juego utiliza **doble buffer**:
1. Se dibuja todo sobre `self.config.screen` (superficie virtual de 1000×700)
2. `config.present()` escala la superficie virtual para que encaje en la ventana real manteniendo relación de aspecto (`pygame.transform.scale`)
3. La ventana puede estar en modo ventana o fullscreen según la configuración

---

## 10. Mapa de Archivos Clave

| Archivo | Líneas | Rol |
|---|---|---|---|
| `game.py` | ~30 | Entry point, bucle principal |
| `config/Settings.py` | ~221 | Constantes + clase GameConfig + sistema de volumen (con `_sound_volumes` por sonido) + sprites dañados del jugador |
| `GameContext.py` | ~75 | Estado global, sprite groups, precarga de assets (`_preload_assets`) |
| `sences/GameScene.py` | ~475 | Escena principal, orquesta managers + motor según movimiento + escudo del Bombardier + misión completa → shop |
| `sences/SceneManager.py` | ~50 | Máquina de estados de escenas |
| `sences/ShopScene.py` | ~260 | Tienda de mejoras, selector verde, preview de tanque, humo, sonido motor |
| `sences/ControlsScene.py` | ~80 | Pantalla de controles, acepta `pre_game_upgrade` |
| `entities/Bombardier.py` | ~730 | Jefe final (entidad más compleja): entrada desde arriba, escudo periódico |
| `gameplay/collision_manager.py` | ~210 | Lógica central de combate (incluye daño de tanques verdes en 2 golpes + sprites dañados del jugador) |
| `gameplay/player_controller.py` | ~130 | Input del jugador |
| `ui/hud.py` | ~156 | Interfaz en pantalla |
