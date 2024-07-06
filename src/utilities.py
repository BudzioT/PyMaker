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
                image_surface = pygame.image.load(full_path)

                # Append it to the images list
                images_list.append(image_surface)

                print(full_path)

        return images_list


    def import_folder_dict(self, path):
        """Import the folder as a dictionary"""
        pass


utilities = Utilities()
