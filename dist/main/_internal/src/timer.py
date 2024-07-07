import pygame


class Timer:
    """Timer class"""
    def __init__(self, duration):
        """Initialize the timer"""
        # Active flag
        self.active = False
        # Duration of the timer
        self.duration = duration
        # Activate time
        self.start_time = 0

    def update(self):
        """Update the timer"""
        # Get the current time
        current_time = pygame.time.get_ticks()
        # If the timer duration passed, deactivate the timer
        if current_time - self.start_time >= self.duration:
            self.stop()

    def start(self):
        """Start the timer"""
        # Activate it
        self.active = True
        # Store the start time
        self.start_time = pygame.time.get_ticks()

    def stop(self):
        """Stop the timer"""
        # Reset the active flag
        self.active = False
        # Reset the start time back to 0
        self.start_time = 0
