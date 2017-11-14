import pygame


class SpriteInventory:
    def __init__(self):
        # Sprite lists
        self.all = pygame.sprite.LayeredDirty()  # All sprites
        self.walls = pygame.sprite.LayeredDirty()  # Wall sprites

        self.food = pygame.sprite.LayeredDirty()  # Food sprites
        self.energizers = pygame.sprite.LayeredDirty()  # Energizer sprites
        self.cherries = pygame.sprite.LayeredDirty()  # Cherry sprites

        self.players = pygame.sprite.LayeredDirty()  # Player sprites
        self.pacmans = pygame.sprite.LayeredDirty()  # Pacman sprites
        self.ghosts = pygame.sprite.LayeredDirty()  # Ghost sprites

        self.score_list = pygame.sprite.LayeredDirty()  # Score list sprites
