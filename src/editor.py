import os.path
import sys
from random import choice, randint

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
    def __init__(self, land_tiles, switch):
        """Initialize the editor"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Switch function
        self.switch = switch

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

        # Foreground objects
        self.foreground = pygame.sprite.Group()
        # Background objects
        self.background = pygame.sprite.Group()

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
                  self.animations[0]["frames"], 0, self.origin, [self.map_objects, self.foreground])
        # Sky drag handle (ID: 1)
        self.sky_handle = MapObject((settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2),
                                    [self.sky_handle_surface], 1, self.origin,
                                    [self.map_objects, self.background])
        # Active clouds
        self.clouds = []
        # Import cloud surfaces
        self.cloud_surfaces = utilities.import_folder("../graphics/clouds")
        # Initialize the cloud timer, set it to spawn a cloud every 4 seconds
        self.cloud_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.cloud_timer, 4000)

        # Spawn some clouds at the beginning
        self._start_clouds()

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
        self._update_surface(delta_time)

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

            # Save the map when user clicks return (enter)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch(self._create_grid())

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

            # Create the clouds
            self._create_clouds(event)

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

    def _get_current_cell(self, obj = None):
        """Get the current cell"""
        # Get the distance between the mouse position and the map origin
        distance_origin = (vector(mouse_pos())
                           - self.origin) if not obj else vector(obj.origin_distance) - self.origin

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
    def _update_surface(self, delta_time):
        """Update and draw everything onto the main surface"""
        self.surface.fill("white")

        # Draw the sky
        self._display_sky(delta_time)

        # Draw the map
        self._draw_map()

        # Draw the tile lines
        self._draw_lines()

        # If user want's to put something, draw a preview
        self._show_preview()

        # Display the menu
        self.menu.display(self.select_index)

    def _display_sky(self, delta_time):
        """Draw the sky based off sky handle position"""
        # Draw the sky
        self.surface.fill(settings.COLORS["SKY"])

        # Get center of the sky handle
        pos_y = self.sky_handle.rect.centery

        # If horizon is visible on the screen, draw it
        if pos_y > 0:
            # Horizon lines
            horizon_rect_1 = pygame.Rect(0, pos_y - 2, settings.WINDOW_WIDTH, 10)
            horizon_rect_2 = pygame.Rect(0, pos_y - 7, settings.WINDOW_WIDTH, 4)
            horizon_rect_3 = pygame.Rect(0, pos_y - 10, settings.WINDOW_WIDTH, 2)
            # Draw the horizon lines
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_1)
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_2)
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_3)

            # Draw the clouds, only if sky is visible
            self._display_clouds(delta_time, pos_y)

        # If horizon is on the screen, draw the sea in excepted position
        if 0 < pos_y < settings.WINDOW_HEIGHT:
            # Create the sea rectangle
            sea_rect = pygame.Rect(0, pos_y, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
            # Draw it
            pygame.draw.rect(self.surface, settings.COLORS["SEA"], sea_rect)
            # Draw another horizon line for a nice look
            pygame.draw.line(self.surface, settings.COLORS["HORIZON"],
                             (0, pos_y), (settings.WINDOW_WIDTH, pos_y), 3)

        # Otherwise just fill the entire screen with sea color, the horizon isn't visible anyway
        if pos_y < 0:
            self.surface.fill(settings.COLORS["SEA"])

    def _display_clouds(self, delta_time, pos_y):
        """Display the clouds"""
        # Go through every active cloud
        for cloud in self.clouds:
            # Move it based off the speed
            cloud["pos"][0] -= cloud["speed"] * delta_time

            # Calculate its position, to make them move with horizon
            cloud_x = cloud["pos"][0]
            cloud_y = pos_y - cloud["pos"][1]

            # Blit it
            self.surface.blit(cloud["surface"], (cloud_x, cloud_y))

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
        # Draw the background objects
        self.background.draw(self.surface)

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

        # Draw the foreground objects
        self.foreground.draw(self.surface)

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
                    # Choose between background or foreground group
                    group = [self.map_objects]
                    # If object's type is palm background, add the background group
                    if settings.EDITOR_INFO[self.select_index]["style"] == "palm_bg":
                        group.append(self.background)
                    # Otherwise add the foreground one
                    else:
                        group.append(self.foreground)

                    MapObject(mouse_pos(), self.animations[self.select_index]["frames"], self.select_index,
                              self.origin, group)
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

    def _create_grid(self):
        """Create the map grid"""
        # Clear the tile objects
        for tile in self.map_data.values():
            tile.objects = []

        # Go through each of the objects that exist on the map
        for obj in self.map_objects:
            # Get the current cell
            current_cell = self._get_current_cell()
            # Get object's offset in comparison to the cell
            offset = vector(obj.origin_distance) - (vector(current_cell) * settings.TILE_SIZE)

            # If the cell has a tile
            if current_cell in self.map_data:
                self.map_data[current_cell].add_id(obj.tile_id, offset)
            # Otherwise create one
            else:
                self.map_data[current_cell] = MapTile(obj.tile_id, offset)

        # Calculate the grid offset
        # Get the first tile, which is the left one, get the X-Axis value from it (tiles sorted by X value)
        left = sorted(self.map_data.keys(), key=lambda tile: tile[0])[0][0]
        # Get the first top tile Y-Axis position, sorted by Y value
        top = sorted(self.map_data.keys(), key=lambda tile: tile[1])[0][1]

        # Grid layers (ordered by the Z-value, ascending)
        layers = {
            "water": {},
            "bg palms": {},
            "terrain": {},
            "enemies": {},
            "coins": {},
            "fg objects": {}
        }

        # Go through every map item
        for pos, tile in self.map_data.items():
            # Adjust positions to local one
            adjusted_col = pos[0] - left
            adjusted_row = pos[1] - top

            # Change the positions from tiles into pixels
            pos_x = adjusted_col * settings.TILE_SIZE
            pos_y = adjusted_row * settings.TILE_SIZE

            # Check if tile has water, if so get it with the bottom or top style
            if tile.water:
                layers["water"][(pos_x, pos_y)] = tile.get_water_type()

            # If tile has terrain
            if tile.terrain:
                # If is in the land tiles, get it with its neighbors
                if tile.get_terrain() in self.land_tiles:
                    layers["terrain"][(pos_x, pos_y)] = tile.get_terrain()
                # Otherwise just set it to default type
                else:
                    layers["terrain"][(pos_x, pos_y)] = 'X'

            # If tile is a coin just set the tile as a coin (center its position)
            if tile.coin:
                layers["coins"][(pos_x + settings.TILE_SIZE // 2, pos_y + settings.TILE_SIZE // 2)] = tile.coin

            # If there is an enemy, place it
            if tile.enemy:
                layers["enemies"][(pos_x, pos_y)] = tile.enemy

            # If tile has objects
            if tile.objects:
                # Go through each of the object, while taking its offset
                for obj, offset in tile.objects:
                    # If object is a palm background, save it as it
                    if obj in [item_id for item_id, item in settings.EDITOR_INFO.items()
                               if item["style"] == "palm_bg"]:
                        layers["bg palms"][(int(pos_x + offset.x), int(pos_y + offset.y))] = obj
                    # Otherwise save it as palm foreground
                    else:
                        layers["fg objects"][(int(pos_x + offset.x), int(pos_y + offset.y))] = obj

        return layers

    def _create_clouds(self, event):
        """Create the clouds"""
        # If cloud cooldown passed
        if event.type == self.cloud_timer:
            # Choose a random cloud
            cloud_surface = choice(self.cloud_surfaces)
            # Make some of the clouds two times bigger
            if randint(0, 4) < 2:
                cloud_surface = pygame.transform.scale2x(cloud_surface)

            # Choose a random speed
            speed = randint(20, 40)
            # Choose a random position of the cloud, make them appear from the right side of the screen
            pos = [randint(50, 100) + settings.WINDOW_WIDTH, randint(0, settings.WINDOW_HEIGHT)]

            # Add it to the active clouds
            self.clouds.append({"surface": cloud_surface, "pos": pos, "speed": speed})

            # Remove the old clouds, that went beyond the visible surface
            self.clouds = [cloud for cloud in self.clouds if cloud["pos"][0] > -450]

    def _start_clouds(self):
        """Make the clouds appear at the start"""
        # Create 15 clouds at the start
        for cloud_num in range(15):
            # Create a cloud with random image, size
            cloud = (pygame.transform.scale2x(choice(self.cloud_surfaces))
                     if randint(0, 4) < 2
                     else choice(self.cloud_surfaces))
            # Choose a random position in the visible part of screen
            cloud_pos = [randint(0, settings.WINDOW_WIDTH), randint(0, settings.WINDOW_HEIGHT)]
            # Generate a random speed
            speed = randint(20, 40)

            # Create the cloud, add it to the current ones
            self.clouds.append({"surface": cloud, "pos": cloud_pos, "speed": speed})


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
                type_dict = {item_id: item["type"] for item_id, item in settings.EDITOR_INFO.items()}

                # Preview surface with lowered alpha value
                surface = self.previews[self.select_index].copy()
                surface.set_alpha(200)

                # Check if this is a tile
                if type_dict[self.select_index] == "tile":
                    # Get this cell
                    current_cell = self._get_current_cell()
                    # Get its rect in the world, in tile position
                    rect = surface.get_rect(topleft=self.origin + vector(current_cell) * settings.TILE_SIZE)

                # Else get rect of the object in pixels
                else:
                    rect = surface.get_rect(center=mouse_pos())

                # Blit the preview
                self.surface.blit(surface, rect)

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

        # Load the previews into a dictionary
        self.previews = {item_id: load(os.path.join(settings.BASE_PATH, item["preview"]))
                         for item_id, item in settings.EDITOR_INFO.items()
                         if item["preview"]}

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
