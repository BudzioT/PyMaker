class Settings:
    """Game settings"""
    def __init__(self):
        """Initialize the settings"""
        # Size of one tile
        self.TILE_SIZE = 64

        # Dimensions of the window
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720

        # COLORS
        self.COLORS = {
            "SKY": "#DDC6A1",
            "SEA": "#92A9CE",
            "LINE": "black",
            "HORIZON": "#F5F1DE",
            "HORIZON_TOP": "#D1AA9D"
        }


settings = Settings()
