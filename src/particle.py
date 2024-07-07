from src.sprites import AnimatedSprite
from src.settings import settings


class Particle(AnimatedSprite):
    """Simple singular particle"""
    def __init__(self, pos, assets, group):
        """Initialize the particle"""
        super().__init__(pos, assets, group)

        # Center the particle
        self.rect = self.image.get_rect(center=pos)

    def animate(self, delta_time):
        """Animate the particle and destroy the particle"""
        # Increase the frame
        self.frame += settings.ANIMATION_SPEED * delta_time
        # Play the animation if it hasn't ended
        if self.frame < len(self.frames):
            self.image = self.frames[int(self.frame)]

        # Kill the particles when animation ends
        else:
            self.kill()
