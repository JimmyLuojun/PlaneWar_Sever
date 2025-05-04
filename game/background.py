# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/background.py
"""Handles the game's background image, scrolling, and drawing.

Defines the `Background` class responsible for loading the background image,
updating its scrolling position based on a defined speed, and drawing the
correct portion onto the game screen each frame.
"""
import pygame
import os
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT
# No internal package imports needed here

class Background:
    """
    Handles loading, scrolling, and drawing the game's background image.
    """
    def __init__(self, image_path, screen_width, screen_height, scroll_speed):
        """
        Initializes the Background object.

        Args:
            image_path (str): The full path to the background image file.
            screen_width (int): The width of the game screen.
            screen_height (int): The height of the game screen.
            scroll_speed (int): The speed at which the background scrolls (pixels per frame).
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_speed = scroll_speed
        self.image = None
        self.image_height = 0
        self.y1 = 0
        self.y2 = 0 # Positioned above y1 initially

        if not image_path or not os.path.exists(image_path):
            print(f"Warning: Background image not found or path invalid: {image_path}. Background will be black.")
            return # Leave self.image as None

        try:
            # Load using convert() for performance as background is likely opaque
            loaded_image = pygame.image.load(image_path).convert()

            # Scale image width to screen width, maintain aspect ratio for height initially
            original_width, original_height = loaded_image.get_size()
            aspect_ratio = original_height / original_width
            scaled_height = int(screen_width * aspect_ratio)

            # Ensure height is at least screen height for seamless scrolling
            if scaled_height < screen_height:
                print(f"Info: Background image height after scaling ({scaled_height}) is less than screen height ({screen_height}). Adjusting height.")
                scaled_height = screen_height # Stretch height to match screen if needed

            self.image = pygame.transform.scale(loaded_image, (screen_width, scaled_height))
            self.image_height = self.image.get_height()
            self.y2 = -self.image_height # Position second image directly above the first
            print(f"Successfully loaded and scaled background: {os.path.basename(image_path)}")

        except pygame.error as e:
            print(f"Error loading/scaling background image {image_path}: {e}. Background will be black.")
            self.image = None # Ensure image is None on error

    def update(self):
        """Updates the vertical position of the background images for scrolling."""
        if not self.image:
            return # Do nothing if image wasn't loaded

        # Move both images down
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed

        # If the first image is completely off-screen below, reset it above the second image
        if self.y1 >= self.image_height:
            self.y1 = self.y2 - self.image_height

        # If the second image is completely off-screen below, reset it above the first image
        if self.y2 >= self.image_height:
            self.y2 = self.y1 - self.image_height

    def draw(self, surface):
        """
        Draws the background images onto the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the background on (usually the screen).
        """
        if self.image:
            surface.blit(self.image, (0, self.y1))
            surface.blit(self.image, (0, self.y2))
        else:
            # Fallback: Fill with black if the image failed to load
            surface.fill((0, 0, 0)) # Use BLACK constant if imported, otherwise tuple
