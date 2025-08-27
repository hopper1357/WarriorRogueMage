import pygame
import os

TILESIZE = 32

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type

        # Simple visual representation for now
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        if self.tile_type == "wall":
            self.image.fill((100, 100, 100)) # Gray for walls
        else:
            self.image.fill((50, 150, 50)) # Green for grass

        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)

class Map:
    def __init__(self, filename):
        self.data = []
        game_folder = os.path.dirname(__file__)
        map_folder = os.path.join(game_folder, '..', 'assets', 'maps')
        self.map_path = os.path.join(map_folder, filename)
        with open(self.map_path, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

        self.all_tiles = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        for row, tiles in enumerate(self.data):
            for col, tile_char in enumerate(tiles):
                if tile_char == '#':
                    wall_tile = Tile(col, row, "wall")
                    self.all_tiles.add(wall_tile)
                    self.walls.add(wall_tile)
                else:
                    grass_tile = Tile(col, row, "grass")
                    self.all_tiles.add(grass_tile)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(800 / 2)
        y = -target.rect.centery + int(600 / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - 800), x)  # right
        y = max(-(self.height - 600), y)  # bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)
