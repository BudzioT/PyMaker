import os.path
import sys

import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_pressed
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load

from src.settings import settings
from src.menu import Menu
from src.map_tile  import MapTile
from src.utilities import utilities
from src.map_object import MapObject
from src.timer import Timer


class Editor:
    """The game's level editor"""
    def __init__(self, land_tiles):
        """Initialize the editor"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Navigation origin
        self.origin = vector()
        # Pan active flag
        self.pan = False
        # Its offset
        self.pan_offset = vector()

        # Surface of support lines
        self.support_surface = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Set its color key as green
        self.support_surface.set_colorkey("green")
        # Set alpha of everything visible to 40
        self.support_surface.set_alpha(40)

        # Object select index
        self.select_index = 2

        # Map data
        self.map_data = {}
        # Object of the map (objects are off-grid tiles)
        self.map_objects = pygame.sprite.Group()

        # Land tile surfaces
        self.land_tiles = land_tiles
        # Import other assets
        self._import_assets()

        # Last clicked cell
        self.last_cell = None

        # Dragging objects flag
        self.drag_active = False

        # Create the menu
        self.menu = Menu()

        # The player with ID 0
        MapObject((200, settings.WINDOW_HEIGHT / 2),
                  self.animations[0]["frames"], 0, self.origin, self.map_objects)
        # Sky drag handle (ID: 1)
        self.sky_handle = MapObject((settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2),
                                    [self.sky_handle_surface], 1, self.origin, self.map_objects)

        # Object adding timer
        self.object_timer = Timer(400)

    def run(self, delta_time):
        """Run the level editor"""
        # Run the event loop
        self._get_events()

        # Run the animations
        self._update_animations(delta_time)
        # Update the map objects
        self.map_objects.update(delta_time)

        # Update the object timer
        self.object_timer.update()

        # Update the surface
        self._update_surface()

    # Input
    def _get_events(self):
        """Get the editor's input events"""
        # Go through each event that happened
        for event in pygame.event.get():
            # If user wants to quit, close the game
            if event.type == pygame.QUIT:
                # Uninitialize pygame modules
                pygame.quit()
                # Quit
                sys.exit()

            # Check and handle panning inputs
            self._pan_input(event)
            # Check for select input
            self._select(event)

            # Handle menu clicks
            self._menu_click(event)

            # Handle object dragging
            self._drag_object(event)

            # Handle clicks outside of menu
            self._map_add()
            self._map_remove()

    def _pan_input(self, event):
        """Get panning input"""
        # If middle button is pressed, activate panning
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed()[1]:
            self.pan = True
            # Calculate the offset between mouse and the origin point
            self.pan_offset = vector(mouse_pos()) - self.origin

        # If middle button is released set panning to false
        if not mouse_pressed()[1]:
            self.pan = False

        # If event is mouse wheel scroll
        if event.type == pygame.MOUSEWHEEL:
            # If user is holding left control, move the Y-Axis of the map by scrolling
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            # Otherwise move the X-Axis of the map
            else:
                # Scroll the map with it
                self.origin.x -= event.y * 50

        # If user is panning, move the origin to the same direction but with offset
        if self.pan:
            self.origin = vector(mouse_pos()) - self.pan_offset

            # Update the objects
            for obj in self.map_objects.sprites():
                obj.update_pos(self.origin)

    def _select(self, event):
        """Select the items"""
        # Check for a key press
        if event.type == pygame.KEYDOWN:
            # If user pressed right, increase the selection index
            if event.type == pygame.K_d or event.type == pygame.K_RIGHT:
                self.select_index += 1
            # If user pressed left, decrease it
            if event.type == pygame.K_a or event.type == pygame.K_LEFT:
                self.select_index -= 1

        # Don't allow the user to change index below 0
        self.select_index = max(self.select_index, 0)
        # Don't allow him to change it to high too
        self.select_index = min(self.select_index, len(settings.EDITOR_INFO))

    def _menu_click(self, event):
        """Handle menu clicks"""
        # If the user clicked the moused and the cursor is on the menu, handle the click
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            # Save the selection index
            self.select_index = self.menu.handle_click(mouse_pos(), mouse_pressed())

    def _get_current_cell(self):
        """Get the current cell"""
        # Get the distance between the mouse position and the map origin
        distance_origin = vector(mouse_pos()) - self.origin

        # If horizontal distance is higher than 0, just get its tile column
        if distance_origin.x > 0:
            column = int(distance_origin.x / settings.TILE_SIZE)
        # Otherwise subtract one, to prevent two tiles with the same tile position
        else:
            column = int(distance_origin.x / settings.TILE_SIZE) - 1

        # If vertical distance is below the origin, set the row to the tile
        if distance_origin.y > 0:
            row = int(distance_origin.y / settings.TILE_SIZE)
        # Otherwise subtract one again
        else:
            row = int(distance_origin.y / settings.TILE_SIZE) - 1

        # Return the cell's position
        return column, row

    # Drawing
    def _update_surface(self):
        """Update and draw everything onto the main surface"""
        self.surface.fill("white")

        # Draw the map
        self._draw_map()

        # Draw the tile lines
        self._draw_lines()

        # Draw a circle
        pygame.draw.circle(self.surface, "red", self.origin, 10)

        # If user want's to put something, draw a preview
        self._show_preview()

        # Display the menu
        self.menu.display(self.select_index)

    def _draw_lines(self):
        """Draw the tile lines"""
        # Calculate the amount of columns and rows
        columns = settings.WINDOW_WIDTH // settings.TILE_SIZE
        rows = settings.WINDOW_HEIGHT // settings.TILE_SIZE

        # Make the surface green to help with transparency
        self.support_surface.fill("green")

        # Offset to keep the lines in screen
        origin_offset = vector(self.origin.x - int(self.origin.x / settings.TILE_SIZE) * settings.TILE_SIZE,
                               self.origin.y - int(self.origin.y / settings.TILE_SIZE) * settings.TILE_SIZE)

        # Go through each column (added one because one column on the right doesn't get drawn)
        for col in range(columns + 1):
            # Calculate the vertical position by the tile size and offset them by column number from origin
            pos_x = origin_offset.x + col * settings.TILE_SIZE
            # Draw the column line
            pygame.draw.line(self.support_surface, settings.COLORS["LINE"],
                             (pos_x, 0), (pos_x, settings.WINDOW_HEIGHT))
        # Go through each row
        for row in range(rows + 1):
            # Calculate the horizontal position
            pos_y = origin_offset.y + row * settings.TILE_SIZE
            # Draw the row line
            pygame.draw.line(self.support_surface, settings.COLORS["LINE"],
                             (0, pos_y), (settings.WINDOW_WIDTH, pos_y))

        # Blit the support lines onto the main surface
        self.surface.blit(self.support_surface, (0, 0))

    def _draw_map(self):
        """Draw the map"""
        # Go through each tile placed
        for cell_pos, tile in self.map_data.items():
            # Get its position in pixels
            pos = self.origin + vector(cell_pos) * settings.TILE_SIZE

            # If tile has water
            if tile.water:
                if tile.water_on_top:
                    self.surface.blit(self.water_bottom, pos)
                else:
                    # Get animation frames of the water (that has ID equal to 3)
                    frames = self.animations[3]["frames"]
                    # Grab the current frame as int
                    frame = int(self.animations[3]["frame"])
                    # Blit the frame
                    self.surface.blit(frames[frame], pos)

            # If it has terrain
            if tile.terrain:
                # Convert the terrain to a string
                terrain_string = ''.join(tile.neighbor_terrain)
                # Take the style based off the neighbors, if it doesn't exist just set it to 'X'
                terrain_style = terrain_string if terrain_string in self.land_tiles else 'X'
                self.surface.blit(self.land_tiles[terrain_style], pos)

            # If it has a coin
            if tile.coin:
                # Take the frames of coin with certain ID
                frames = self.animations[tile.coin]["frames"]
                # Get the frame
                frame = int(self.animations[tile.coin]["frame"])
                # Center the coin in the tile
                rect = frames[frame].get_rect(center=(pos[0] + settings.TILE_SIZE // 2,
                                                      pos[1] + settings.TILE_SIZE // 2))
                # Blit it
                self.surface.blit(frames[frame], rect)

            # Otherwise if it has an enemy
            if tile.enemy:
                # Take the enemy's frames
                frames = self.animations[tile.enemy]["frames"]
                # Get current frame
                frame = int(self.animations[tile.enemy]["frame"])
                # Place it on the middle bottom of a tile
                rect = frames[frame].get_rect(midbottom=(pos[0] + settings.TILE_SIZE // 2,
                                                         pos[1] + settings.TILE_SIZE))
                # Blit the enemy
                self.surface.blit(frames[frame], rect)
        self.map_objects.draw(self.surface)

    def _map_add(self):
        """Add the item to the map"""
        # If user pressed the left mouse button but didn't click on the menu and isn't dragging any object
        if (mouse_pressed()[0]) and (not self.menu.rect.collidepoint(mouse_pos())) and (not self.drag_active):
            # Get the current clicked cell
            current_cell = self._get_current_cell()

            # Check if user is placing a tile
            if settings.EDITOR_INFO[self.select_index]["type"] == "tile":
                # If user didn't click on the same cell twice
                if current_cell != self.last_cell:
                    # If there is something already, change the cell to the current ID
                    if current_cell in self.map_data:
                        self.map_data[current_cell].add_id(self.select_index)

                    # Otherwise add new cell to the map data
                    else:
                        self.map_data[current_cell] = MapTile(self.select_index)

                    self._check_neighbor_cells(current_cell)

                    # Save the current cell, as the last one
                    self.last_cell = current_cell

            # Otherwise he's placing an object
            else:
                # Check for object placement cooldown, if it passed, place the object
                if not self.object_timer.active:
                    MapObject(mouse_pos(), self.animations[self.select_index]["frames"], self.select_index,
                              self.origin, self.map_objects)
                    # Activate the cooldown
                    self.object_timer.start()

    def _map_remove(self):
        """Remove tile or an object from the map"""
        # Check if user right-clicked on a tile and not on the menu
        if mouse_pressed()[2] and not self.menu.rect.collidepoint(mouse_pos()):
            # Save the object that user points to
            selected_object = self._object_pointed()
            # Check if there was any
            if selected_object:
                # If the object wasn't the player or sky handler, delete it
                if settings.EDITOR_INFO[selected_object.tile_id]["style"] not in ("sky", "player"):
                    selected_object.kill()

            # If there is any data in map, prepare to delete the object
            if self.map_data:
                # Get the current cell and check if it exists in map data
                current_cell = self._get_current_cell()
                if current_cell in self.map_data:
                    # Remove it
                    self.map_data[current_cell].remove_id(self.select_index)

                    # If the current cell is empty now, remove it from the map
                    if self.map_data[current_cell].empty:
                        del self.map_data[current_cell]
                    # Fix the tiling
                    self._check_neighbor_cells(current_cell)

    def _drag_object(self, event):
        """Handle object dragging"""
        # If user is clicking the left mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed()[0]:
            # Go through each object
            for obj in self.map_objects:
                # If it collides with the place, where the user clicked, prepare the dragging action
                if obj.rect.collidepoint(event.pos):
                    obj.prepare_drag()
                    # Set the dragging active flag to True
                    self.drag_active = True

        # If user is done dragging
        if event.type == pygame.MOUSEBUTTONUP and self.drag_active:
            # Go through every object
            for obj in self.map_objects:
                # Stop dragging it and reset the flag
                obj.end_drag(self.origin)
                self.drag_active = False

    def _check_neighbor_cells(self, pos):
        """Check the neighbor cells of the given cell position"""
        # Amount of the neighbor cells
        local_size = 3
        # Local tiles positions in map cell coordinates
        local_tiles = [(pos[0] + column - int(local_size / 2), pos[1] + row - int(local_size / 2))
                       for column in range(local_size)
                       for row in range(local_size)]

        # Go through each cell in the local area of the given cell positions
        for cell in local_tiles:
            # If cell exists
            if cell in self.map_data:
                # Prepare the neighbor list
                self.map_data[cell].neighbor_terrain = []
                self.map_data[cell].water_on_top = False

                # Go through each neighbor tile possible
                for name, side in settings.NEIGHBOR_CELLS.items():
                    # Take the neighbor cell position
                    neighbor_cell = (cell[0] + side[0], cell[1] + side[1])

                    # If neighbor cell exists
                    if neighbor_cell in self.map_data:
                        # If the neighbor exists, and it's water on top of the current cell
                        if self.map_data[cell].water and self.map_data[neighbor_cell].water and name == 'A':
                            # Set the water on top flag to True
                            self.map_data[cell].water_on_top = True

                    # If the neighbor exists and it's a terrain
                    if neighbor_cell in self.map_data:
                        # Add its name to the current cell neighbors
                        self.map_data[cell].neighbor_terrain.append(name)

    def _show_preview(self):
        """Show preview of the placement of a tile and show which objects are draggable"""
        # Check if user isn't in the menu
        if not self.menu.rect.collidepoint(mouse_pos()):
            # Get the object that user points to
            selected_object = self._object_pointed()

            # If the object exists
            if selected_object:
                # Get the object's rectangle inflated by 10 pixels
                rect = selected_object.rect.inflate(10, 10)

                # Width of lines
                width = 3
                # Size of lines
                size = 15
                # Color of them
                color = "black"

                # Draw the lines
                # Bottom left line
                pygame.draw.lines(self.surface, "black", False,
                                  ((rect.left, rect.bottom - size),
                                   rect.bottomleft, (rect.left + size, rect.bottom)), width)
                # Top left line
                pygame.draw.lines(self.surface, "black", False,
                                  ((rect.left, rect.top + size),
                                   rect.topleft, (rect.left + size, rect.top)), width)
                # Bottom right line
                pygame.draw.lines(self.surface, "black", False,
                                  ((rect.right - size, rect.bottom),
                                   rect.bottomright, (rect.right, rect.bottom - size)), width)
                # Top right line
                pygame.draw.lines(self.surface, "black", False,
                                  ((rect.right - size, rect.top),
                                   rect.topright, (rect.right, rect.top + size)), width)

            # Otherwise display the preview of the tile
            else:
                # Get the ID's of tiles and objects and their type
                type_dict = {item_id: item["type"] for item_id, item in settings.EDITOR_INFO}

    def _import_assets(self):
        """Import assets not loaded in the main file"""
        # Load the bottom part of water
        self.water_bottom = (load(os.path.join(settings.BASE_PATH, "../graphics/terrain/water/water_bottom.png"))
                             .convert_alpha())
        # Load the sky handle
        self.sky_handle_surface = (load(os.path.join(settings.BASE_PATH, "../graphics/cursors/handle.png"))
                             .convert_alpha())

        # Animations dictionary
        self.animations = {}
        # Go through every item that exists in editor info
        for item_id, item in settings.EDITOR_INFO.items():
            # If this item has animation
            if item["graphics"]:
                # Load the animation images
                graphics = utilities.import_folder(item["graphics"])
                # Insert it into dictionary with current frame set as 0
                self.animations[item_id] = {
                    "frame": 0,
                    "frames": graphics,
                    "length": len(graphics)
                }

        # Previews dictionary
        self.previews = {}

    def _update_animations(self, delta_time):
        """Update the animations"""
        # Go through each animation that is loaded
        for item in self.animations.values():
            # Increase the frame of it
            item["frame"] += settings.ANIMATION_SPEED * delta_time
            # If the frame is too high, return it to the first one
            if item["frame"] >= item["length"]:
                item["frame"] = 0

    def _object_pointed(self):
        """Check which object does the mouse points on"""
        # Go through every object on the map
        for obj in self.map_objects:
            # Check for mouse collision with it, if there is one, remove it
            if obj.rect.collidepoint(mouse_pos()):
                return obj
