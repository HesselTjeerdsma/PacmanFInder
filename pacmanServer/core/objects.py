import pygame
from core.definitions import *

import logging
logger = logging.getLogger(__name__)


class Player(pygame.sprite.DirtySprite):
    def __init__(self, x, y, color, p_type: str, ip: str=None, name: str=''):
        super().__init__()
        self.image = pygame.Surface([16, 16])
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)

        self.rect = pygame.draw.circle(self.image, color, (8, 8), 8)
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)

        # Player attributes
        self._ip = ip
        self._name = name
        self._type = p_type
        self.score = 0
        self.lives = 3

        self.quarantine = False

        if p_type == 'pacman':
            self.can_eat_others = False
        elif p_type == 'ghost':
            self.can_eat_others = True  # Useless for ghost?
        else:
            raise ValueError('Player type `%s` not supported', p_type)

        self.can_eat_others_handle = None
        self.quarantine_handle = None

        # Ghost hitting multiplier
        self.score_multiplier = 1

        # TODO: remove debug
        self.debug = False
        # For arrow key support
        self.x_moveby = 0
        self.y_moveby = 0

    @property
    def ip(self):
        return self._ip

    @property
    def name(self):
        return self._name

    @property
    def p_type(self):
        return self._type

    def change_color(self, color):
        self.dirty = 1
        self.image.fill(COLOR_WHITE)
        self.image.set_colorkey(COLOR_WHITE)

        old_pos = self.rect.center

        self.rect = pygame.draw.circle(self.image, color, (8, 8), 8)
        self.rect.center = old_pos
        self.mask = pygame.mask.from_surface(self.image)

    def energizer_callback(self):
        self.can_eat_others = False
        self.score_multiplier = 1
        self.change_color(COLOR_GREEN)

    def quarantine_callback(self):
        self.quarantine = False

    def move(self, x, y, wall_list):
        # Redraw
        self.dirty = 1

        error = False
        error_msg = {'x': False, 'y': False}

        # Move left/right
        old_x_position = self.rect.centerx
        self.rect.centerx = x
        # Hit a wall?
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        for wall in wall_hit_list:
            if pygame.sprite.collide_mask(self, wall):
                error = True
                error_msg['x'] = True
                self.rect.centerx = old_x_position

        # Move up/down
        old_y_position = self.rect.centery
        self.rect.centery = y
        # Hit a wall?
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        for wall in wall_hit_list:
            if pygame.sprite.collide_mask(self, wall):
                error = True
                error_msg['y'] = True
                self.rect.centery = old_y_position

        if error:
            return error_msg
        else:
            return False

    def update(self, passed_time):
        # TODO: animation of object
        pass

    # For arrow keys support
    def change_speed(self, x, y):
        self.x_moveby += x
        self.y_moveby += y

    # For arrow keys support
    def move_by_arrow_keys(self, wall_list):
        if not self.x_moveby == 0 or not self.y_moveby == 0:
            # Redraw
            self.dirty = 1

        error = False
        error_msg = {'x': False, 'y': False}

        if not (self.x_moveby == 0):
            # Move left/right
            old_x_position = self.rect.centerx
            self.rect.centerx += self.x_moveby
            # Hit a wall?
            wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
            for wall in wall_hit_list:
                if pygame.sprite.collide_mask(self, wall):
                    error = True
                    error_msg['x'] = True
                    self.rect.centerx = old_x_position

        if not (self.y_moveby == 0):
            # Move up/down
            old_y_position = self.rect.centery
            self.rect.centery += self.y_moveby
            # Hit a wall?
            wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
            for wall in wall_hit_list:
                if pygame.sprite.collide_mask(self, wall):
                    error = True
                    error_msg['y'] = True
                    self.rect.centery = old_y_position

        if error:
            return error_msg
        else:
            return False


class Text(pygame.sprite.DirtySprite):
    def __init__(self, msg: str, pos=(0, 0), centered=False, fontname=None, font_size=32, color=COLOR_WHITE):
        super().__init__()
        self._pos = pos
        self._centered = centered
        self._font = pygame.font.SysFont(fontname, font_size)
        self._color = color
        self._msg = None

        self.image = None
        self.rect = None

        self.change(msg)

    def change(self, msg):
        if msg != self._msg:
            self.dirty = 1
            self._msg = msg
            self.image = self._font.render(msg, True, self._color)
            self.rect = self.image.get_rect()
            if self._centered:
                self.rect.center = self._pos
            else:
                self.rect.topleft = self._pos


class Block(pygame.sprite.DirtySprite):
    def __init__(self, x, y, width, height, angle, color=COLOR_BLUE, animate=False):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.image.set_colorkey(COLOR_BLACK)
        self.image = pygame.transform.rotate(self.image, angle)

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        if animate:
            self._animate = True
            self._animate_interval = animate['interval']
            self._animate_colors = animate['colors']

            self._passed_time = 0
        else:
            self._animate = False

    def update(self, passed_time):
        if self._animate:
            self._passed_time += passed_time

            if self._passed_time > self._animate_interval:
                self._passed_time = 0

                self.dirty = 1

                color = self._animate_colors[0]
                self.image.fill(color)
                self._animate_colors.remove(color)
                self._animate_colors.append(color)
