```python
import asyncio
import pygame
import random
import math

####################################################################
# INITIATION

pygame.init()

screen_width, screen_height = 960, 640

# Tile size keeps the original 29 * 16 grid layout
tile_size = int(screen_width // (screen_width / (screen_width / 30)))

grid_x, grid_y, grid_id = 0, 0, 0
cam = [0 - tile_size // 2, 0 - tile_size * 3.5]

# mouse = [grid_x, grid_y, grid_id]
mouse = [0, 0, 0]

screen = pygame.display.set_mode(
    (screen_width, screen_height),
    pygame.RESIZABLE
)

pygame.display.set_caption("Minesweeper")

offset_for_hud = screen_height // 5

grid_length = int(screen_width // tile_size - 1)
grid_height = int((screen_height - offset_for_hud) // tile_size)

clock = pygame.time.Clock()

tiles_to_check = []
checked_tiles = []

# repeat[0] = flag input
# repeat[1] = reveal/input
repeat = [False, False]

gamestate = "Playing"

# Mobile flag mode
flag_mode = False

# Timer
timer = 0.0

####################################################################
# LOAD TEXTURES

raw_tile = [
    pygame.image.load("Tiles/Closed_Tile.png"),   # 0
    pygame.image.load("Tiles/Bomb.png"),          # 1
    pygame.image.load("Tiles/Empty_Tile.png"),    # 2
    pygame.image.load("Tiles/Tile_1.png"),        # 3
    pygame.image.load("Tiles/Tile_2.png"),        # 4
    pygame.image.load("Tiles/Tile_3.png"),        # 5
    pygame.image.load("Tiles/Tile_4.png"),        # 6
    pygame.image.load("Tiles/Tile_5.png"),        # 7
    pygame.image.load("Tiles/Tile_6.png"),        # 8
    pygame.image.load("Tiles/Tile_7.png"),        # 9
    pygame.image.load("Tiles/Tile_8.png"),        # 10
    pygame.image.load("Tiles/Flag_Tile.png"),     # 11
    pygame.image.load("Tiles/Background.png"),    # 12
    pygame.image.load("Tiles/Neutral.jpg"),       # 13
    pygame.image.load("Tiles/Angry.png"),         # 14
    pygame.image.load("Tiles/Happy.jpg"),         # 15
]

tile = []

for img in raw_tile:
    tile.append(
        pygame.transform.scale(
            img,
            (tile_size, tile_size)
        )
    )

tile[12] = pygame.transform.scale(
    raw_tile[12],
    (screen_width, screen_height)
)

for i in range(13, 16):
    tile[i] = pygame.transform.scale(
        raw_tile[i],
        (tile_size * 2, tile_size * 2)
    )

####################################################################
# FUNCTIONS

def make_grid():
    global bombs, grid, bomb_amount, flag_amount, timer

    grid = []
    bombs = []
    bomb_amount = 0

    # Create closed tiles
    for _ in range(grid_length * grid_height):
        grid.append(0)

    # Randomly assign bombs
    for _ in range(len(grid)):
        bombs.append(random.randint(0, 4))

    bomb_amount = bombs.count(1)

    # Available flags
    flag_amount = bomb_amount

    timer = 0.0


def render_play_grid():
    grid_id = 0
    grid_y = 0
    grid_x = 0

    for y in range(grid_height):
        for x in range(grid_length):

            if 0 <= grid_id < len(grid):

                tile_type = grid[grid_id]
                block = tile[tile_type]

                blit_x = grid_x * tile_size - cam[0]
                blit_y = grid_y * tile_size - cam[1]

                screen.blit(block, (blit_x, blit_y))

            grid_id += 1
            grid_x += 1

        grid_y += 1
        grid_x = 0


def render_gui():
    global flag_amount

    cam_x = 0 - cam[0]
    cam_y = 0 - cam[1]

    # Background
    x = cam_x - tile_size / 2
    y = cam_y - tile_size * 3.5

    screen.blit(tile[12], (x, y))

    # Center button
    x = cam_x + screen_width / 2 - tile_size * 1.5
    y = cam_y - screen_height // 7

    if gamestate == "Playing":
        face_id = 13
    elif gamestate == "Lost":
        face_id = 14
    else:
        face_id = 15

    screen.blit(tile[face_id], (x, y))

    return x, y, tile_size * 2


def render_mobile_controls():
    """
    Draws touchscreen-friendly controls.

    The flag button is intentionally outside the main grid area.
    """

    button_width = tile_size * 5
    button_height = tile_size * 1.5

    x = screen_width / 2 - button_width / 2
    y = screen_height - button_height - tile_size / 2

    # Simple button background
    pygame.draw.rect(
        screen,
        (180, 180, 180),
        (x, y, button_width, button_height)
    )

    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (x, y, button_width, button_height),
        3
    )

    if flag_mode:
        label = "FLAG MODE"
    else:
        label = "REVEAL MODE"

    mobile_font = pygame.font.Font(
        "freesansbold.ttf",
        max(16, tile_size // 2)
    )

    text = mobile_font.render(
        label,
        True,
        (0, 0, 0)
    )

    text_rect = text.get_rect(
        center=(x + button_width / 2, y + button_height / 2)
    )

    screen.blit(text, text_rect)

    return x, y, button_width, button_height


def render():
    screen.fill((0, 0, 0))

    button = render_gui()

    render_play_grid()

    mobile_button = render_mobile_controls()

    return button, mobile_button


def camera_limits():
    cam[0] = max(
        0 - screen_width / 2,
        min(cam[0], screen_width / 2)
    )

    cam[1] = max(
        0 - screen_height / 2,
        min(cam[1], screen_height / 2)
    )


def camera_movement(keys):
    """
    Original WASD camera movement.
    """

    if keys[pygame.K_a]:
        cam[0] -= tile_size // 10

    if keys[pygame.K_d]:
        cam[0] += tile_size // 10

    if keys[pygame.K_w]:
        cam[1] -= tile_size // 10

    if keys[pygame.K_s]:
        cam[1] += tile_size // 10


def mouse_position():
    """
    Converts the mouse/touch position into a grid position.
    """

    mouse_x, mouse_y = pygame.mouse.get_pos()

    mouse[0] = int((mouse_x + cam[0]) // tile_size)
    mouse[1] = int((mouse_y + cam[1]) // tile_size)

    mouse[2] = int(
        mouse[1] * grid_length + mouse[0]
    )


def camera(keys):
    camera_movement(keys)
    camera_limits()


def lost_game():
    global gamestate

    # Reveal all bombs
    for i in range(len(grid)):
        if bombs[i] == 1:
            grid[i] = 1

    gamestate = "Lost"


def check_win():
    global gamestate

    correctly_flagged_bombs = 0
    uncheck_boxes_remaining = 0

    for i in range(len(grid)):

        if grid[i] == 11 and bombs[i] == 1:
            correctly_flagged_bombs += 1

        if grid[i] == 0:
            uncheck_boxes_remaining += 1

    if (
        correctly_flagged_bombs == bomb_amount
        and uncheck_boxes_remaining == 0
    ):
        gamestate = "Won"


def flag_tile(x, y):
    """
    Flags or unflags a tile.
    """

    global flag_amount

    if not (0 <= x < grid_length and 0 <= y < grid_height):
        return

    tile_id = int(y * grid_length + x)

    if grid[tile_id] == 0:

        if flag_amount > 0:
            grid[tile_id] = 11
            flag_amount -= 1

    elif grid[tile_id] == 11:

        grid[tile_id] = 0
        flag_amount += 1


def reveal_tile(x, y):
    """
    Reveals a tile and handles the empty-tile flood fill.
    """

    global tiles_to_check
    global checked_tiles

    if not (0 <= x < grid_length and 0 <= y < grid_height):
        return

    tile_id = int(y * grid_length + x)

    # Don't reveal flags or already revealed empty tiles
    if grid[tile_id] == 11 or grid[tile_id] == 2:
        return

    bombs_at_point = get_bombs_at_point(x, y)

    # Bomb
    if bombs[tile_id] == 1:
        lost_game()
        return

    # Empty tile - flood fill
    if bombs_at_point == 0:

        tiles_to_check = []
        checked_tiles = []

        startxy = [x, y]
        tiles_to_check.append(startxy)

        while len(tiles_to_check) > 0:

            current = tiles_to_check.pop(0)

            cx = current[0]
            cy = current[1]

            if current in checked_tiles:
                continue

            checked_tiles.append(current)

            current_id = int(
                cy * grid_length + cx
            )

            if grid[current_id] == 11:
                continue

            grid[current_id] = 2

            for dx in range(-1, 2):
                for dy in range(-1, 2):

                    nx = cx + dx
                    ny = cy + dy

                    if not (
                        0 <= nx < grid_length
                        and 0 <= ny < grid_height
                    ):
                        continue

                    neighbor_id = int(
                        ny * grid_length + nx
                    )

                    if grid[neighbor_id] == 11:
                        continue

                    neighbor_bombs = get_bombs_at_point(
                        nx,
                        ny
                    )

                    if neighbor_bombs == 0:

                        xy = [nx, ny]

                        if (
                            xy not in checked_tiles
                            and xy not in tiles_to_check
                        ):
                            tiles_to_check.append(xy)

                    else:

                        grid[neighbor_id] = neighbor_bombs + 2

        return

    # Numbered tile
    if bombs_at_point >= 1:
        grid[tile_id] = bombs_at_point + 2


def game_actions(keys, mouse_clicked, right_clicked, button, mobile_button):
    global cam
    global tiles_to_check
    global checked_tiles
    global gamestate
    global flag_mode

    # Center camera
    if keys[pygame.K_c]:
        cam = [
            0 - tile_size // 2,
            0 - tile_size * 3.5
        ]

    ################################################################
    # KEYBOARD FLAGGING

    if gamestate == "Playing":

        if keys[pygame.K_SPACE] and not repeat[0]:

            repeat[0] = True

            flag_tile(
                mouse[0],
                mouse[1]
            )

        ################################################################
        # RIGHT MOUSE BUTTON = FLAG

        if right_clicked and not repeat[0]:

            repeat[0] = True

            flag_tile(
                mouse[0],
                mouse[1]
            )

        ################################################################
        # LEFT MOUSE / TOUCH = REVEAL

        if mouse_clicked and not repeat[1]:

            repeat[1] = True

            if flag_mode:
                flag_tile(
                    mouse[0],
                    mouse[1]
                )
            else:
                reveal_tile(
                    mouse[0],
                    mouse[1]
                )

    ################################################################
    # RESTART / FACE BUTTON

    mouse_x, mouse_y = pygame.mouse.get_pos()

    if (
        button[0] < mouse_x < button[0] + button[2]
        and
        button[1] < mouse_y < button[1] + button[2]
    ):

        if mouse_clicked and not repeat[1]:

            repeat[1] = True

            tiles_to_check = []
            checked_tiles = []

            make_grid()

            gamestate = "Playing"

    ################################################################
    # MOBILE FLAG MODE BUTTON

    if (
        mobile_button[0] < mouse_x <
        mobile_button[0] + mobile_button[2]
        and
        mobile_button[1] < mouse_y <
        mobile_button[1] + mobile_button[3]
    ):

        if mouse_clicked and not repeat[1]:

            repeat[1] = True

            flag_mode = not flag_mode


def get_bombs_at_point(x, y):

    bombs_at_point = 0

    for dx in range(-1, 2):
        for dy in range(-1, 2):

            nx = x + dx
            ny = y + dy

            if (
                0 <= nx < grid_length
                and
                0 <= ny < grid_height
            ):

                tile_id = int(
                    ny * grid_length + nx
                )

                if bombs[tile_id] == 1:
                    bombs_at_point += 1

    return bombs_at_point


def handle_repeated_inputs(keys):
    global repeat

    if (
        repeat[0]
        and not keys[pygame.K_SPACE]
        and not pygame.mouse.get_pressed()[2]
    ):
        repeat[0] = False

    if (
        repeat[1]
        and not pygame.mouse.get_pressed()[0]
    ):
        repeat[1] = False


def tick_timer(dt):
    global timer

    if gamestate == "Playing":

        if timer > 999:
            timer = 0

        timer += dt


####################################################################
# MAIN GAME LOOP
#
# pygbag/browser-compatible version
####################################################################

async def main():

    global repeat

    make_grid()

    RUN = True

    while RUN:

        # Delta time in seconds
        dt = clock.tick(60) / 1000.0

        mouse_clicked = False
        right_clicked = False

        # ----------------------------------------------------------
        # PYGAME EVENTS
        # ----------------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                RUN = False

            # Mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    mouse_clicked = True

                elif event.button == 3:
                    right_clicked = True

            # Touch input is reported as mouse input by many
            # Pygame browser builds, but this also handles FINGERDOWN.
            elif event.type == pygame.FINGERDOWN:

                mouse_x = int(event.x * screen.get_width())
                mouse_y = int(event.y * screen.get_height())

                pygame.mouse.set_pos(
                    (mouse_x, mouse_y)
                )

                mouse_clicked = True

        # ----------------------------------------------------------
        # CURRENT KEYBOARD STATE
        # ----------------------------------------------------------

        keys = pygame.key.get_pressed()

        # ----------------------------------------------------------
        # GAME UPDATE
        # ----------------------------------------------------------

        tick_timer(dt)

        button, mobile_button = render()

        mouse_position()

        camera(keys)

        game_actions(
            keys,
            mouse_clicked,
            right_clicked,
            button,
            mobile_button
        )

        check_win()

        handle_repeated_inputs(keys)

        pygame.display.flip()

        # Give the browser control back.
        await asyncio.sleep(0)

    pygame.quit()


####################################################################
# START
####################################################################

asyncio.run(main())
```
