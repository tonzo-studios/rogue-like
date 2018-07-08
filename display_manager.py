#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap
import pygame

from entities import Stairs
from misc import Singleton, Vector, Colors, get_abs_path


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
    SCREEN_WIDTH = 100
    SCREEN_HEIGHT = 50
    GAME_TITLE = "Tonzo Studios Roguelike"

    BAR_WIDTH = 20
    PANEL_HEIGHT = 6
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

    MSG_X = BAR_WIDTH + 2
    MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MSG_HEIGHT = PANEL_HEIGHT - 1

    BACKPACK_WIDTH = 20

    game_msgs = []

    def __init__(self, player, dungeon):
        pygame.init()
        pygame.display.set_caption(self.GAME_TITLE)
        self.screen = pygame.display.set_mode((1600, 900), pygame.DOUBLEBUF)
        self.screen.set_alpha(None)

        self.player = player
        self.dungeon = dungeon

    @classmethod
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

    def _render_backpack(cls):
        for y, item in enumerate(cls.player.backpack.contents):
            cls.backpack.draw_str(
                2, y + 1,
                f"{cls.player.backpack.contents[item]} of {item.name}",
                Colors.WHITE, None
            )

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
        x_centered = x + (total_w - len(text)) // 2
        cls.panel.draw_str(x_centered, y, text, fg=text_color, bg=None)

    def _render_bars(cls):
        """
        Render all UI bars.
        """
        cls.add_bar(1, 1, cls.BAR_WIDTH, 'HP', cls.player.hp,
                    cls.player.max_hp, Colors.RED, (150, 0, 0))
        cls.add_bar(1, 3, cls.BAR_WIDTH, 'MP', cls.player.mp,
                    cls.player.max_mp, Colors.BLUE, (0, 0, 150))

    def _render_map(cls):
        """
        Renders the current game map if necessary.
        """
        import registry

        sprites = pygame.sprite.Group()

        cur_map = cls.dungeon.current_level
        # if cls.dungeon.fov_recomputed:
            # cls.dungeon.fov_recomputed = False

        for x in range(cur_map.width):
            for y in range(cur_map.height):
                pos = Vector(x, y)
                wall = not cur_map.transparent[pos]

                # If position is visible, draw a bright tile
                if cur_map.fov[pos]:
                    if wall:
                        sprites.add(Sprite(registry.registry.sprites['wall_light'], x*16, y*16))
                    else:
                        sprites.add(Sprite(registry.registry.sprites['floor_light'], x*16, y*16))
                    # Tiles in FOV will be remembered after they get out
                    # of sight, out of mind :^)
                    cur_map.explored[pos] = True

                # Position is not visible, but has been explored before
                elif cur_map.explored[pos]:
                    if wall:
                        sprites.add(Sprite(registry.registry.sprites['wall_dark'], x*16, y*16))
                    else:
                        sprites.add(Sprite(registry.registry.sprites['floor_dark'], x*16, y*16))
        sprites.draw(cls.screen)

    def _render_entities(cls):
        """
        Render visible entities by render layer to the buffer console.
        """
        sprites = pygame.sprite.Group()

        entities_sorted = sorted(cls.dungeon.current_level.entities,
                                 key=lambda x: x.render_priority.value)

        for entity in entities_sorted:
            # Draw visible entities
            if cls.dungeon.current_level.fov[entity.pos] and not isinstance(entity.sprite, str):
                sprites.add(Sprite(entity.sprite, entity.pos.x*16, entity.pos.y*16))
            # Remember stairs location
            if isinstance(entity, Stairs) and cls.dungeon.current_level.explored[entity.pos]:
                sprites.add(Sprite(entity.sprite, entity.pos.x*16, entity.pos.y*16))

        sprites.draw(cls.screen)

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
        cls._render_backpack()
        cls.root_console.blit(
            cls.panel, 0, cls.PANEL_Y, cls.SCREEN_WIDTH, cls.PANEL_HEIGHT, 0, 0
        )
        # TODO: Instead of using the level width, use views with fixed width
        cls.root_console.blit(
            cls.backpack, cls.dungeon.LEVEL_WIDTH, 0, cls.BACKPACK_WIDTH, cls.SCREEN_HEIGHT, 0, 0
        )

    def _clear_entities(cls):
        """
        Clears all of the entities in the current game map from the buffer console.
        """
        cls.entities = pygame.sprite.Group()

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
        cls.screen.fill((0, 0, 0))
        cls._render_map()
        cls._render_entities()
        pygame.display.update()
        # cls._display_game()
        # cls._display_ui()
        # tdl.flush()
        # cls._clear_all()


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()  # get rekt
        self.rect.x = x
        self.rect.y = y
