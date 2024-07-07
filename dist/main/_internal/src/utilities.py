import os
from os.path import join as path_join

import pygame

from src.settings import settings


class Utilities:
    """Class that gives utilities"""
    def __init__(self):
        """Initialize the utilities"""
        pass

    def import_folder(self, path):
        """Import the folder"""
        # Images list
        images_list = []

        # Change the path into absolute one
        path = str(path_join(settings.BASE_PATH, path))

        # Go through each of the file and directory in given path
        for path, directory, images in os.walk(path):
            # Go through each image
            for image_name in images:
                # Save the path to the image
                full_path = path + '/' + image_name
                # Load it
                image_surface = pygame.image.load(full_path).convert_alpha()

                # Append it to the images list
                images_list.append(image_surface)
        # Return the images
        return images_list

    def import_folder_dict(self, path):
        """Import the folder as a dictionary"""
        # Images dictionary
        images_dict = {}

        # Change the path into absolute
        path = str(path_join(settings.BASE_PATH, path))

        # Go through each of the file and directory
        for path, directory, images in os.walk(path):
            # Go through each image
            for image_name in images:
                # Save its path
                full_path = path + '/' + image_name
                # Load the image
                image_surface = pygame.image.load(full_path).convert_alpha()

                # Create a new item in dictionary with image name (without .png) as key and the surface as value
                images_dict[image_name.split('.')[0]] = image_surface
        # Return the images dictionary
        return images_dict


utilities = Utilities()
