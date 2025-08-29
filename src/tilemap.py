import pygame
import os

TILESIZE = 32

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)

class HazardTile(Tile):
    def __init__(self, x, y, image, damage, damage_type):
        super().__init__(x, y, image)
        self.damage = damage
        self.damage_type = damage_type

class Map:
    def __init__(self, filepath):
        self.data = []
        # If the filepath is not absolute, assume it's a filename in the default maps folder
        if not os.path.isabs(filepath):
            game_folder = os.path.dirname(__file__)
            map_folder = os.path.join(game_folder, '..', 'assets', 'maps')
            filepath = os.path.join(map_folder, filepath)

        with open(filepath, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

        self.all_tiles = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()

        # Define tile images
        wall_img = pygame.Surface((TILESIZE, TILESIZE)); wall_img.fill((100, 100, 100))
        grass_img = pygame.Surface((TILESIZE, TILESIZE)); grass_img.fill((50, 150, 50))
        fire_img = pygame.Surface((TILESIZE, TILESIZE)); fire_img.fill((200, 50, 50))

        for row, tiles in enumerate(self.data):
            for col, tile_char in enumerate(tiles):
                grass_tile = Tile(col, row, grass_img.copy())
                self.all_tiles.add(grass_tile)

                if tile_char == '#':
                    wall_tile = Tile(col, row, wall_img.copy())
                    self.all_tiles.add(wall_tile)
                    self.walls.add(wall_tile)
                elif tile_char == 'F':
                    fire_tile = HazardTile(col, row, fire_img.copy(), damage="1d6", damage_type="fire")
                    self.all_tiles.add(fire_tile)
                    self.hazards.add(fire_tile)

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
