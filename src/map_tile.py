from src.settings import settings


class MapTile:
    """A single map tile"""
    def __init__(self, tile_id):
        """Initialize the tile"""
        # Terrain placed flag
        self.terrain = False
        # Neighbor terrain list for auto-tiling
        self.neighbor_terrain = []

        # If the tile has a coin, what one
        self.coin = None

        # Water flag
        self.water = False
        # Water on top flag, for animating the top water tile
        self.water_on_top = False

        # What enemy is on the tile if there is any
        self.enemy = None

        # Objects on the tile
        self.objects = []

        # Get ID's of items and save them with the corresponding item's style
        self.data = {key: value["style"] for key, value in settings.EDITOR_INFO.items()}

        # Add the tile ID
        self.add_id(tile_id)

        # Empty tile flag
        self.empty = False

    def add_id(self, tile_id):
        """Add item's ID into map tile"""
        # Get the tile's style
        current_style = self.data[tile_id]

        # If the tile is a terrain, set the terrain flag to True
        if current_style == "terrain":
            self.terrain = True
        # If tile is water, set the flag
        elif current_style == "water":
            self.water = True

        # If tile is a coin, save the coin ID
        elif current_style == "coin":
            self.coin = tile_id
        # If tile is an enemy, save the enemy id
        elif current_style == "enemy":
            self.enemy = tile_id

    def remove_id(self, tile_id):
        """Remove item's ID from a tile in the map"""
        # Get the tile's style
        current_style = self.data[tile_id]

        # If tile is a terrain, remove it
        if current_style == "terrain":
            self.terrain = False
        # Remove the water
        elif current_style == "water":
            self.water = False
        # Remove coin when selected
        elif current_style == "coin":
            self.coin = False
        # Remove the enemy
        elif current_style == "enemy":
            self.enemy = False

        # Check if tile is empty now
        self.check()

    def check(self):
        """Check if tile is empty"""
        # If there is nothing on the tile, set the empty flag
        if (not self.terrain) and (not self.water) and (not self.coin) and (not self.enemy):
            self.empty = True
