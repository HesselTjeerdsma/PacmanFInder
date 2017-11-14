import pygame
from random import randint

from core.definitions import *
from core.map_parser import SVGMapParser
from core.objects import Player, Block, Text
from core.observe import *
from core.time import AsyncClock
from util.auxillary import x_px_to_mm, x_mm_to_px, y_px_to_mm, y_mm_to_px

import logging
logger = logging.getLogger(__name__)


class Game(Observable):
    def __init__(self, loop, inventory, map: str, caption: str):
        super().__init__()
        self._loop = loop

        # Store arguments, for simple restart
        self._map = map
        self._caption = caption

        # Init map parser
        self._map_parser = SVGMapParser(self._map)

        # Screen initialization
        #self._screen_size = self._map_parser.get_dimensions()
        #self._screen = pygame.display.set_mode(self._screen_size)  # Create screen
        #pygame.display.set_caption(self._caption)  # Set caption of screen
        # pygame.mouse.set_visible(False)  # Mouse visibility

        # Some vars
        self._clock = AsyncClock(self._loop)  # The clock
        self._quit = False  # Var to quit the game
        self._game_over = False  # Game lost

        self._cherry_spawn_handle = None  # Asyncio handle to stop spawning events

        # Create background
        #self._background = pygame.Surface(self._screen.get_size())  # Create Surface
        #self._background.fill(COLOR_BLACK)  # Fill with color

        # Sprite inventory
        self._sprite_inventory = inventory

        # Display the background; needed to not have a pacman trail
        #self._sprite_inventory.all.clear(self._screen, self._background)

        # Init walls/food
        self._init_sprites()

    def _init_sprites(self):
        # Score heading
        score_heading = Text("Scores:", (100, 50))
        # self._score_list.add(score_heading)
        self._sprite_inventory.all.add(score_heading)

        # TODO: remove this, just for debug
        if DEBUG_PLAYER:
            pacman = Player(1375, 150, COLOR_GREEN, p_type='pacman', name="2Pac")
            pacman.debug = True
            self._sprite_inventory.players.add(pacman)
            self._sprite_inventory.pacmans.add(pacman)
            self._sprite_inventory.all.add(pacman)
            #self._draw_score_list()

        # Read walls/food from svg file based on color
        for block in self._map_parser.get_blocks():
            if block[5] == COLOR_BLUE:
                wall = Block(block[0], block[1], block[2], block[3], block[4], block[5])
                self._sprite_inventory.walls.add(wall)
                self._sprite_inventory.all.add(wall)
            elif block[5] == COLOR_WHITE:
                food = Block(block[0], block[1], block[2], block[3], block[4], block[5])
                self._sprite_inventory.food.add(food)
                self._sprite_inventory.all.add(food)
            elif block[5] == COLOR_PINK:
                energizer = Block(block[0], block[1], block[2], block[3], block[4], block[5])
                self._sprite_inventory.energizers.add(energizer)
                self._sprite_inventory.all.add(energizer)

        # Start the cherry spawning process
        self._loop.call_later(randint(90, 100)/10, self._spawn_cherry)

    def _restart(self):
        logger.debug("Restarting application")

        # Remove all sprites from all groups
        for sprite in self._sprite_inventory.all:
            sprite.kill()

        # Clear all events from the queue
        pygame.event.clear()

        # Init walls/food again
        self._init_sprites()

        # Game not over
        self._game_over = False

    def _draw_score_list(self):
        # Amount of score sprites and players
        number_of_players = len(self._sprite_inventory.players)
        number_of_scores = len(self._sprite_inventory.score_list)

        # More players than score sprites
        if number_of_players > number_of_scores:
            # Add score sprite
            for x in range(number_of_scores, number_of_players):
                score_sprite = Text("", (100, 82+32*x))
                self._sprite_inventory.score_list.add(score_sprite)
                self._sprite_inventory.all.add(score_sprite)
        # More score sprites than players
        elif number_of_players < number_of_scores:
            # Remove score sprite
            self._sprite_inventory.score_list.sprites()[-1].kill()

        # List of all names and scores
        scores = []
        for player in self._sprite_inventory.players:
            scores.append((player.name, player.score))

        # Write the right text to the sprites
        i = 0
        for name, score in sorted(scores, key=lambda y: y[1], reverse=True):
            try:
                self._sprite_inventory.score_list.sprites()[i].change(name + ": " + str(score))
            except KeyError:
                logger.error("More scores than score sprites")
            i += 1

    def _process_game_events(self):
        # Current pressed key
        pressed_key = pygame.key.get_pressed()
        altkey_held = pressed_key[pygame.K_LALT] or pressed_key[pygame.K_RALT]  # Is an alt-key held?
        arrowkey_held = pressed_key[pygame.K_UP] or pressed_key[pygame.K_DOWN] or pressed_key[pygame.K_LEFT] or pressed_key[pygame.K_RIGHT]  # Is an arrow-key held?

        # Loop over all events
        for event in pygame.event.get():
            # Quit game on close or alt+f4 combo
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and altkey_held):
                self._quit = True  # Stop the loop
            else:
                if self._game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._restart()  # Restart game
                elif len(self._sprite_inventory.players) > 0:
                    if event.type == (pygame.USEREVENT + 1):
                        # Penalize player when he moves more than the allowed limit
                        distance_moved_squared = (event.x - x_px_to_mm(event.player.rect.centerx)) ** 2 + \
                                                 (event.y - y_px_to_mm(event.player.rect.centery)) ** 2
                        if distance_moved_squared >= JUMP_LIMIT ** 2:
                            logger.debug("Player `%s` moved more than the allowed limit", event.player.name)
                            try:  # Cancel any running timer
                                event.player.quarantine_handle.cancel()
                            except AttributeError:
                                pass

                            # Set timer for quarantine duration
                            event.player.quarantine_handle = self._loop.call_later(TIMER_QUARANTINE, event.player.quarantine_callback)
                            event.player.quarantine = True
                            self.notify(Observation(self, 'quarantine', event.player))

                        # Move player
                        error = event.player.move(x_mm_to_px(event.x), y_mm_to_px(event.y), self._sprite_inventory.walls)
                        if error:
                            self.notify(Observation(self, 'location_error', {
                                'player': event.player,
                                **error
                            }))

                    # Arrow key support for debug purposes
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self._sprite_inventory.players.sprites()[0].change_speed(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self._sprite_inventory.players.sprites()[0].change_speed(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self._sprite_inventory.players.sprites()[0].change_speed(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self._sprite_inventory.players.sprites()[0].change_speed(1, 0)
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_UP:
                            self._sprite_inventory.players.sprites()[0].change_speed(0, 1)
                        elif event.key == pygame.K_DOWN:
                            self._sprite_inventory.players.sprites()[0].change_speed(0, -1)
                        elif event.key == pygame.K_LEFT:
                            self._sprite_inventory.players.sprites()[0].change_speed(1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self._sprite_inventory.players.sprites()[0].change_speed(-1, 0)

        # Should Pacman move?
        if arrowkey_held and len(self._sprite_inventory.players) > 0 and not self._game_over:
            error = self._sprite_inventory.players.sprites()[0].move_by_arrow_keys(self._sprite_inventory.walls)  # Move Pacman

    # TODO: move to objects or sth
    def _spawn_cherry(self):
        # Create cherry in random position
        x = randint(20, 1580)
        y = randint(145, 395)
        animate = {
            'interval': 0.5,
            'colors': [COLOR_WHITE, COLOR_RED]
        }
        cherry = Block(x, y, 20, 20, 0, COLOR_RED, animate)

        # Add to sprite lists
        self._sprite_inventory.cherries.add(cherry)
        self._sprite_inventory.all.add(cherry)

        # Auto destruct cherry
        lifetime = randint(-CHERRY_AVG_LIFETIME, CHERRY_AVG_LIFETIME)+CHERRY_AVG_LIFETIME
        logger.debug("Cherry visible for %0.1f seconds", lifetime)
        self._loop.call_later(lifetime, cherry.kill)

        # Notify all players
        for player_to_notify in self._sprite_inventory.players:
            self.notify(Observation(self, 'cherry_spawned', {
                'player': player_to_notify,
                'lifetime': lifetime,
                'location': {
                    'x': cherry.rect.x,
                    'y': cherry.rect.y
                }
            }))

        # Generate new cherry
        spawntime = lifetime + randint(-CHERRY_AVG_GRACE, CHERRY_AVG_GRACE) + CHERRY_AVG_GRACE
        logger.debug("New cherry will be seen after %0.1f seconds", spawntime)
        self._cherry_spawn_handle = self._loop.call_later(spawntime, self._spawn_cherry)

    async def play(self):
        # Main game loop
        while not self._quit:
            # Process events (move-event, keystrokes, mouse click and quit)
            self._process_game_events()

            if self._game_over:
                # Pause for the next frame
                passed_time = await self._clock.tick(10)  # Run on lower FPS

                # Auto restart the game
                # TODO: BUG: does some weird thing when using the arrow keys
                self._restart()
            else:
                # Pause for the next frame
                passed_time = await self._clock.tick(60)  # Cap on 60 FPS

                # ----- Collision detection -----
                # Check whether cherry is hit
                cherry_hit_list = pygame.sprite.groupcollide(self._sprite_inventory.players,
                                                             self._sprite_inventory.cherries, False, False)
                for player, cherries in cherry_hit_list.items():
                    # Player must not be in quarantine
                    if not player.quarantine:
                        for cherry in cherries:
                            # Remove cherry
                            cherry.kill()
                            # Add score
                            player.score += SCORE_CHERRY
                            # Notify all players
                            for player_to_notify in self._sprite_inventory.players:
                                self.notify(Observation(self, 'cherry', {
                                    'who': player,
                                    'player': player_to_notify,
                                    'location': {
                                        'x': cherry.rect.x,
                                        'y': cherry.rect.y
                                    }
                                }))
                            # Update score list
                            self._draw_score_list()

                # Check whether food is hit
                food_hit_list = pygame.sprite.groupcollide(self._sprite_inventory.pacmans,
                                                           self._sprite_inventory.food, False, False)
                for pacman, foods in food_hit_list.items():
                    # Player must not be in quarantine
                    if not pacman.quarantine:
                        for food in foods:
                            # Remove food
                            food.kill()
                            # Add score
                            pacman.score += SCORE_FOOD
                            # Notify all players
                            for player_to_notify in self._sprite_inventory.players:
                                self.notify(Observation(self, 'food', {
                                    'who': pacman,
                                    'player': player_to_notify,
                                    'location': {
                                        'x': food.rect.x,
                                        'y': food.rect.y
                                    }
                                }))
                            # Update score list
                            self._draw_score_list()

                energizer_hit_list = pygame.sprite.groupcollide(self._sprite_inventory.pacmans,
                                                                self._sprite_inventory.energizers, False, False)
                for pacman, energizers in energizer_hit_list.items():
                    # Player must not be in quarantine
                    if not pacman.quarantine:
                        for energizer in energizers:
                            # Remove energizer
                            energizer.kill()
                            # Add score
                            pacman.score += SCORE_ENERGIZER

                            # Update score list
                            self._draw_score_list()

                            # Pacman cannot be hit
                            pacman.vulnerable = False
                            # Pacman can eat ghosts
                            pacman.can_eat_others = True
                            # Change Pacman color
                            pacman.change_color(COLOR_BLUE)

                            # Notify all players
                            for player_to_notify in self._sprite_inventory.players:
                                self.notify(Observation(self, 'energizer', {
                                    'who': pacman,
                                    'player': player_to_notify,
                                    'location': {
                                        'x': energizer.rect.x,
                                        'y': energizer.rect.y
                                    }
                                }))

                            try:  # Cancel any running timer
                                pacman.can_eat_others_handle.cancel()
                            except AttributeError:
                                pass
                            # Set timer for energizer duration
                            pacman.can_eat_others_handle = self._loop.call_later(TIMER_ENERGIZER, pacman.energizer_callback)

                # Check whether Pacman and a ghost hit
                ghost_hit_list = pygame.sprite.groupcollide(self._sprite_inventory.pacmans,
                                                            self._sprite_inventory.ghosts, False, False)
                for pacman, ghosts in ghost_hit_list.items():
                    # Hit only possible when pacman is not in quarantine
                    if not pacman.quarantine:
                        # Loop over all ghosts hit
                        for ghost in ghosts:
                            # Hit only possible when ghost is not in quarantine
                            if not ghost.quarantine:
                                # Can pacman eat ghosts; ate energizer?
                                if pacman.can_eat_others:
                                    logger.debug("Pacman `%s` hit `%s`", pacman.name, ghost.name)
                                    # Ghost loses a life
                                    ghost.lives -= 1
                                    # Pacman scores
                                    pacman.score += SCORE_HIT_GHOST*pacman.score_multiplier

                                    if ghost.lives == 0:
                                        # Player is dead
                                        logger.debug("Player `%s` is game over", ghost.name)
                                        # Remove player from the game
                                        ghost.kill()
                                        # Notify player with event
                                        self.notify(Observation(self, 'game_over', ghost))
                                    else:
                                        try:  # Cancel any running timer
                                            ghost.quarantine_handle.cancel()
                                        except AttributeError:
                                            pass

                                        # Set timer for quarantine duration
                                        ghost.quarantine_handle = self._loop.call_later(TIMER_QUARANTINE, ghost.quarantine_callback)
                                        # Put ghost in quarantine for some seconds
                                        ghost.quarantine = True
                                        self.notify(Observation(self, 'quarantine', ghost))

                                    # Notify both players
                                    # TODO: split actions?
                                    self.notify(Observation(self, 'collision', {'hit': ghost, 'player': pacman}))
                                    self.notify(Observation(self, 'collision', {'hit': pacman, 'player': ghost}))

                                    # Increase multiplier
                                    pacman.score_multiplier += 1
                                else:
                                    logger.debug("Ghost `%s` hit `%s`", ghost.name, pacman.name)
                                    # Pacman loses a life
                                    pacman.lives -= 1
                                    # Ghost scores
                                    ghost.score += SCORE_HIT_PACMAN

                                    if pacman.lives == 0:
                                        # Player is dead
                                        logger.debug("Player `%s` is game over", pacman.name)
                                        # Remove player from the game
                                        pacman.kill()
                                        # Notify player with event
                                        self.notify(Observation(self, 'game_over', pacman))
                                    else:
                                        try:  # Cancel any running timer
                                            pacman.quarantine_handle.cancel()
                                        except AttributeError:
                                            pass

                                        # Set timer for quarantine duration
                                        pacman.quarantine_handle = self._loop.call_later(TIMER_QUARANTINE, pacman.quarantine_callback)

                                        # Put pacman in quarantine for some seconds
                                        pacman.quarantine = True
                                        self.notify(Observation(self, 'quarantine', pacman))

                                    # Notify both players
                                    # TODO: split actions?
                                    self.notify(Observation(self, 'collision', {'hit': ghost, 'player': pacman}))
                                    self.notify(Observation(self, 'collision', {'hit': pacman, 'player': ghost}))

                        # Update score list
                        self._draw_score_list()

                # ----- Game over -----
                # TODO: bug or feature? It might be possible to have 0 food and a winning Ghost
                # all food/energizers are collected OR all pacmans are gone -> game done
                if (len(self._sprite_inventory.food) == 0 and len(self._sprite_inventory.energizers) == 0)\
                        or (ghost_hit_list and len(self._sprite_inventory.pacmans) == 0):
                    self._game_over = True
                    # Find the highest scoring player
                    # TODO: bug or feature? Highest scoring player might be dead...
                    winner = None
                    for player in self._sprite_inventory.players:
                        try:
                            if player.score > winner.score:
                                winner = player
                        except AttributeError:
                            winner = player

                    # Notify players the game has ended
                    for player in self._sprite_inventory.players:
                        if player == winner:
                            self.notify(Observation(self, 'game_won', player))
                        else:
                            self.notify(Observation(self, 'game_over', player))

                        player.kill()

                    try:  # Stop cherry spawning process
                        self._cherry_spawn_handle.cancel()
                    except AttributeError:
                        pass

                    # bg = Block(0, 0, self._screen_size[0], self._screen_size[1], 0, COLOR_BLACK)
                    text = Text("Player `{}` won with {} points and {} remaining lives".format(winner.name,
                                                                                               winner.score,
                                                                                               winner.lives),
                                pos=(self._screen_size[0] // 2, self._screen_size[1] // 2), centered=True)
                    # self._all.add((bg, text))
                    self._sprite_inventory.all.add(text)

            # ----- Render section -----
                # Call update method on all sprites
                # Only needed when not game over
                self._sprite_inventory.all.update(passed_time)

            # Redraw dirty sprites only
            #rects = self._sprite_inventory.all.draw(self._screen)  # Get updated rectangles
            #pygame.display.update(rects)  # Draw rectangles

        # Close window and exit
        pygame.quit()
