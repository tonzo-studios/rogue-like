#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tdl
import textwrap

from misc import Singleton, Vector, Colors, get_abs_path
from dungeon import Dungeon


class DisplayManager(metaclass=Singleton):

    """
    Handles the display of entities and objects on the map.

    This class is a Singleton, and as such can be called from anywhere, its
    members and functions/methods can be accessed from anywhere.

    The main "feature" of this class is the refresh() method which will trigger
    a complete rendering of the game and the UI and blit them to the screen,
    effectively performing an update to the latest game state
    """
    # TODO: move these to an appropriate, globally-accessible place
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    MAP_WIDTH = 80
    MAP_HEIGHT = 44
    GAME_TITLE = "Tonzo Studios Roguelike"
    MAX_ROOMS = 30
    MIN_ROOM_SIZE = 6
    MAX_ROOM_SIZE = 10
    MAX_ENTITIES_PER_ROOM = 3
    FOV_ALGORITHM = "BASIC"
    FOV_LIGHT_WALLS = True
    FOV_RADIUS = 10

    BAR_WIDTH = 20
    PANEL_HEIGHT = 6
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

    MSG_X = BAR_WIDTH + 2
    MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MSG_HEIGHT = PANEL_HEIGHT - 1

    game_msgs = []

    # TODO: give consoles a better name
    tdl.set_font(get_abs_path('lucida10x10_gs_tc.png'), greyscale=True, altLayout=True)
    console = tdl.Console(MAP_WIDTH, MAP_HEIGHT)
    panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)
    root_console = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=GAME_TITLE,
                            fullscreen=False)

    cur_map = None
    fov_recompute = True

    # FIXME: move me to somewhere I belong
    def gen_map(cls, player):
        """
        Randomly generates a new dungeon to be explored by the player.

        The aspects of the dungeon are determined by the constants defined
        above.

        Args:
            player (Actor): The player object that will interact with the
                dungeon.
        """
        game_map = Dungeon(cls.MAP_WIDTH, cls.MAP_HEIGHT)
        game_map.generate(
            cls.MAX_ROOMS, cls.MIN_ROOM_SIZE, cls.MAX_ROOM_SIZE,
            cls.MAX_ENTITIES_PER_ROOM, player
        )
        cls.cur_map = game_map
        cls.player = player

    def add_message(cls, new_msg, color=Colors.WHITE):
        """
        Adds a text message to the UI log.

        Examples:
            * Damage dealt to enemy
            * Status effects applied
            * Items looted
            * Dialogues

        Messages are added to a queue and they will be rendered and discarded
        in a FIFO manner.

        Note:
            /!\ Attention, this method shouldn't be used through the
            DisplayManager itself, use misc.add_message instead which is a
            standalone function /!\

        Args:
            new_msg (str): Message to display in the UI log, no size limit
                for the string, and it will automatically be wrapped, however
                if the string is too big for the console it might get clipped.
            color (Colors): Color of the text to be displayed, white by
                default.
        """
        wrapped = textwrap.wrap(new_msg, cls.MSG_WIDTH)

        for line in wrapped:
            if len(cls.game_msgs) == cls.MSG_HEIGHT:
                del cls.game_msgs[0]

            cls.game_msgs.append((line, color))

    def _render_messages(cls):
        """
        Renders all messages found in the DisplayManager.game_msgs queue
        """
        for y, msg in enumerate(cls.game_msgs):
            line, color = msg
            cls.panel.draw_str(cls.MSG_X, y + 1, line, color, None)

    def add_bar(cls, x, y, total_w, name, val, maxi, fg_color, bg_color,
                text_color=Colors.WHITE):
        """
        Adds a bar to the UI in a chosen color with chosen text.

        Useful for displaying stuff like HP, MP, EXP and any other thing that
        the user might want to track through the UI in a min-max model.

        The bar's color depends on the ratio of val to maxi, effectively
        creating a visual representation of the stat.

        Note:
            If the fg/bg color are the same as the text color, the text
            won't be visible.

        Args:
            x (int): X coordinate relative to the container (panel console).
            y (int): Y coordinate relative to the container (panel console).
            total_w (int): Total width of the bar, in pixels.
            name (str): Name of the stat to track, to be displayed inside
                the bar in a format such as {name}: {val}/{maxi}.
            val (int): Current value of this stat.
            maxi (int): Max value of this stat.
            fg_color (Colors): Color of the bar when "full".
            bg_color (Colors): Color of the bar when "empty".
            text_color (Colors, optional): Color of the text inside the bar.
                Colors.WHITE by default.
        """
        bar_width = int(float(val) / maxi * total_w)
        cls.panel.draw_rect(x, y, total_w, 1, None, bg=bg_color)

        if bar_width > 0:
            cls.panel.draw_rect(x, y, bar_width, 1, None, bg=fg_color)

        # FIXME: make val be an int or a properly truncated float, don't coerce
        text = f"{name}: {int(val)}/{maxi}"
        x_centered = x + (total_w - len(text))//2
        cls.panel.draw_str(x_centered, y, text, fg=Colors.WHITE, bg=None)

    def _render_bars(cls):
        """
        Render all UI bars.
        """
        cls.add_bar(1, 1, cls.BAR_WIDTH, 'HP', cls.player.hp,
                    cls.player.max_hp, Colors.RED, (150, 0, 0))
        cls.add_bar(1, 3, cls.BAR_WIDTH, 'MP', cls.player.mp,
                    cls.player.max_mp, Colors.BLUE, (0, 0, 150))

    def _recompute_fov(cls):
        """
        Recompute the player's FOV.

        Usually needed whenever the player's representation on the map moves,
        so that the FOV is connected to the player's actual position.
        """
        if cls.fov_recompute:
            cls.cur_map.compute_fov(
                cls.player.pos, cls.FOV_ALGORITHM, cls.FOV_RADIUS,
                cls.FOV_LIGHT_WALLS
            )

    def _render_map(cls):
        """
        Renders the current game map if necessary.
        """
        if cls.fov_recompute:
            for x in range(cls.cur_map.width):
                for y in range(cls.cur_map.height):
                    pos = Vector(x, y)
                    wall = not cls.cur_map.transparent[pos]

                    # If position is visible, draw a bright tile
                    if cls.cur_map.fov[pos]:
                        if wall:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.WALL_VISIBLE
                            )
                        else:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.GROUND_VISIBLE
                            )
                        # Tiles in FOV will be remembered after they get out
                        # of sight, out of mind :^)
                        cls.cur_map.explored[pos] = True

                    # Position is not visible, but has been explored before
                    elif cls.cur_map.explored[pos]:
                        if wall:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.WALL_DARK
                            )
                        else:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.GROUND_DARK
                            )

    def _render_entities(cls):
        """
        Render visible entities by render layer to the buffer console.
        """
        entities_sorted = sorted(cls.cur_map.entities,
                                 key=lambda x: x.render_priority.value)
        for entity in entities_sorted:
            if cls.cur_map.fov[entity.pos]:
                cls.console.draw_char(
                    entity.pos.x, entity.pos.y, entity.char, entity.color,
                    bg=None
                )

    def _display_game(cls):
        """
        Renders the game world and displays it in the main screen.

        The game world consists of the current game map and the entities that
        are within it, player included.
        """
        cls._render_map()
        cls._render_entities()
        cls.root_console.blit(
            cls.console, 0, 0, cls.SCREEN_WIDTH, cls.SCREEN_HEIGHT, 0, 0
        )

    def _display_ui(cls):
        """
        Renders the UI and displays it in the main screen.

        The UI consists of stat bars (HP, MP, EXP, ...) and of messages
        (Dialog, Combat, ...).
        """
        cls._render_bars()
        cls._render_messages()
        cls.root_console.blit(
            cls.panel, 0, cls.PANEL_Y, cls.SCREEN_WIDTH, cls.PANEL_HEIGHT, 0, 0
        )

    def _clear_entities(cls):
        """
        Clears all of the entities in the current game map from the buffer console.
        """
        for entity in cls.cur_map.entities:
            cls.console.draw_char(
                entity.pos.x, entity.pos.y, ' ', entity.color, bg=None
            )

    def _clear_all(cls):
        """
        Clears the whole screen (Game and UI) from the buffer console.
        """
        cls._clear_entities()
        cls.panel.clear(fg=Colors.WHITE, bg=Colors.BLACK)

    def refresh(cls):
        """
        Refreshes the display after every "turn" (player action).

        This method will perform the following tasks in the following order:
            1. Recompute the player's FOV.
            2. Render the game map if necessary.
            3. Render any entities within the player's FOV.
            4. Render UI elements such as stat bars, logs, etc.
            5. Display everything that's been rendered to the screen.
            6. Prepare for the next call (flushing and clearing).
        """
        cls._recompute_fov()
        cls._display_game()
        cls._display_ui()
        tdl.flush()
        cls._clear_all()
        cls.fov_recompute = False
