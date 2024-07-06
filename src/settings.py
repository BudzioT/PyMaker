import os


class Settings:
    """Game settings"""
    def __init__(self):
        """Initialize the settings"""
        # Size of one tile
        self.TILE_SIZE = 64

        # Dimensions of the window
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720

        # Animation speed
        self.ANIMATION_SPEED = 7

        # File base absolute path
        self.BASE_PATH = os.path.abspath(os.path.dirname(__file__))

        # COLORS
        self.COLORS = {
            "SKY": "#DDC6A1",
            "SEA": "#92A9CE",
            "LINE": "black",
            "HORIZON": "#F5F1DE",
            "HORIZON_TOP": "#D1AA9D",
            "BUTTON": "#43424F",
            "BUTTON_LINE": "#EDECE4",
            "MENU": "#82827E"
        }

        # Information for the map editor
        self.EDITOR_INFO = {
            # Player
            0: {"type": "object", "style": "player", "menu": None, "menu_surf": None,
                "graphics": "../graphics/player/idle_right", "preview": None},

            # Terrains
            1: {"type": "object", "style": "sky", "menu": None, "menu_surf": None, "graphics": None,
                "preview": None},
            2: {"type": "tile", "style": "terrain", "menu": "terrain", "menu_surf": "../graphics/menu/land.png",
                "graphics": None, "preview": "../graphics/preview/land.png"},
            3: {"type": "tile", "style": "water", "menu": "terrain", "menu_surf": "../graphics/menu/water.png",
                "graphics": "../graphics/terrain/water/animation", "preview": "../graphics/preview/water.png"},

            # Coins
            4: {"type": "tile", "style": "coin", "menu": "coin", "menu_surf": "../graphics/menu/gold.png",
                "graphics": "../graphics/items/gold", "preview": "../graphics/preview/gold.png"},
            5: {"type": "tile", "style": "coin", "menu": "coin", "menu_surf": "../graphics/menu/silver.png",
                "graphics": "../graphics/items/silver", "preview": "../graphics/preview/silver.png"},
            6: {"type": "tile", "style": "coin", "menu": "coin", "menu_surf": "../graphics/menu/diamond.png",
                "graphics": "../graphics/items/diamond", "preview": "../graphics/preview/diamond.png"},

            # Enemies
            7: {"type": "tile", "style": "enemy", "menu": "enemy", "menu_surf": "../graphics/menu/spikes.png",
                "graphics": "../graphics/enemies/spikes", "preview": "../graphics/preview/spikes.png"},
            8: {"type": "tile", "style": "enemy", "menu": "enemy", "menu_surf": "../graphics/menu/tooth.png",
                "graphics": "../graphics/enemies/tooth/idle", "preview": "../graphics/preview/tooth.png"},
            9: {"type": "tile", "style": "enemy", "menu": "enemy",
                "menu_surf": "../graphics/menu/shell_left.png", "graphics": "../graphics/enemies/shell_left/idle",
                "preview": "../graphics/preview/shell_left.png"},
            10: {"type": "tile", "style": "enemy", "menu": "enemy",
                 "menu_surf": "../graphics/menu/shell_right.png",
                 "graphics": "../graphics/enemies/shell_right/idle",
                 "preview": "../graphics/preview/shell_right.png"},

            # Palm foregrounds
            11: {"type": "object", "style": "palm_fg", "menu": "palm fg",
                 "menu_surf": "../graphics/menu/small_fg.png", "graphics": "../graphics/terrain/palm/small_fg",
                 "preview": "../graphics/preview/small_fg.png"},
            12: {"type": "object", "style": "palm_fg", "menu": "palm fg",
                 "menu_surf": "../graphics/menu/large_fg.png", "graphics": "../graphics/terrain/palm/large_fg",
                 "preview": "../graphics/preview/large_fg.png"},
            13: {"type": "object", "style": "palm_fg", "menu": "palm fg",
                 "menu_surf": "../graphics/menu/left_fg.png", "graphics": "../graphics/terrain/palm/left_fg",
                 "preview": "../graphics/preview/left_fg.png"},
            14: {"type": "object", "style": "palm_fg", "menu": "palm fg",
                 "menu_surf": "../graphics/menu/right_fg.png", "graphics": "../graphics/terrain/palm/right_fg",
                 "preview": "../graphics/preview/right_fg.png"},

            # Palm backgrounds
            15: {"type": "object", "style": "palm_bg", "menu": "palm bg",
                 "menu_surf": "../graphics/menu/small_bg.png", "graphics": "../graphics/terrain/palm/small_bg",
                 "preview": "../graphics/preview/small_bg.png"},
            16: {"type": "object", "style": "palm_bg", "menu": "palm bg",
                 "menu_surf": "../graphics/menu/large_bg.png", "graphics": "../graphics/terrain/palm/large_bg",
                 "preview": "../graphics/preview/large_bg.png"},
            17: {"type": "object", "style": "palm_bg", "menu": "palm bg",
                 "menu_surf": "../graphics/menu/left_bg.png", "graphics": "../graphics/terrain/palm/left_bg",
                 "preview": "../graphics/preview/left_bg.png"},
            18: {"type": "object", "style": "palm_bg", "menu": "palm bg",
                 "menu_surf": "../graphics/menu/right_bg.png", "graphics": "../graphics/terrain/palm/right_bg",
                 "preview": "../graphics/preview/right_bg.png"},
        }

        # Directions of the neighbor cells and their names
        self.NEIGHBOR_CELLS = {
            'A': (0, -1),
            'B': (1, -1),
            'C': (1, 0),
            'D': (1, 1),
            'E': (0, 1),
            'F': (-1, 1),
            'G': (-1, 0),
            'H': (-1, -1)
        }


settings = Settings()
