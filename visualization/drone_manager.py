from typing import Any
import math
import random
import pygame


class DroneManager:
    """
    Manages the visual representation and animation of the drones.

    Stores the position, movement state, orientation and color of each
    drone and controls its animation throughout the simulation turns.
    """

    def __init__(self, screen: pygame.Surface, data: dict[str, Any],
                 turns: dict[str, Any],
                 node_coords: dict[str, tuple[int, int]],
                 drone_size: int) -> None:
        """
        Initializes the drone manager.

        Args:
            screen: Pygame surface where the drones are rendered.
            data: Map data containing information such as the number of
                drones.
            turns: Simulation results containing the movements performed
                by each drone on every turn.
            node_coords: Dictionary mapping node names to their screen
                coordinates.
            drone_size: Size used when drawing each drone.
        """

        self.screen = screen
        self.data = data
        self.turns = turns
        self.node_coords = node_coords
        self.drone_size = drone_size

        self.colors: list[str] = ["red", "blue", "green", "yellow",
                                  "orange", "purple", "pink", "cyan",
                                  "black"]

        self.drone_pos: dict[str, tuple[float, float]] = {}
        self.drone_start_pos: dict[str, tuple[float, float]] = {}
        self.drone_target_pos: dict[str, tuple[float, float]] = {}
        self.drone_angles: dict[str, float] = {}
        self.drone_colors: dict[str, str] = {}

        self.current_turn: int = 1
        self.turn_progress: float = 0.0
        self.turn_duration: float = 1.0
        self.animation_finished: bool = False
        self.paused: bool = False

        self.create_drones()

        if str(self.current_turn) in self.turns:
            self.prepare_turn()
        else:
            self.animation_finished = True

    def create_drones(self) -> None:
        """
        Creates all drones at the starting hub.

        Initializes each drone's position, orientation and randomly
        assigned display color.
        """

        nb_drones: int = self.data["nb_drones"]
        start_coord = self.node_coords["start"]

        for i in range(1, nb_drones + 1):
            drone = str(i)
            self.drone_pos[drone] = (float(start_coord[0]),
                                     float(start_coord[1]))
            self.drone_angles[drone] = 0.0
            self.drone_colors[drone] = random.choice(self.colors)

    def prepare_turn(self) -> None:
        """
        Prepares the positions and targets for the current turn.

        Reads the movements scheduled for the current turn and calculates
        the target position of each drone. Drones entering a restricted
        hub are positioned halfway between their origin and destination
        to represent their transit state.
        """

        turn_data = self.turns[str(self.current_turn)]
        self.turn_progress = 0.0

        for drone, start_position in self.drone_pos.items():
            self.drone_start_pos[drone] = start_position
            self.drone_target_pos[drone] = start_position

            if drone not in turn_data:
                continue

            drone_data = turn_data[drone]
            movement = drone_data["movement"]
            dest = drone_data["hub"]
            if movement == 1:
                dest = dest.split("-")[1]
            if movement == 0:
                continue

            dest_pos = self.node_coords[dest]
            start_x, start_y = start_position
            dest_x, dest_y = dest_pos
            if movement == 1:
                target_x = start_x + (dest_x - start_x) / 2
                target_y = start_y + (dest_y - start_y) / 2
                self.drone_target_pos[drone] = (target_x, target_y)
            elif movement == 2:
                self.drone_target_pos[drone] = (float(dest_x), float(dest_y))

            dx = dest_x - start_x
            dy = dest_y - start_y
            if dx != 0 or dy != 0:
                self.drone_angles[drone] = math.atan2(dy, dx)

    def update(self, dt: float) -> None:
        """
        Updates the position of every drone during the current turn.

        Advances the animation according to the elapsed time and
        interpolates each drone's position between its starting and target
        positions. When the turn reaches its end, the next turn is started.

        Args:
            dt: Time elapsed since the previous update, in seconds.
        """

        if self.animation_finished or self.paused:
            return

        self.turn_progress += dt / self.turn_duration
        if self.turn_progress > 1.0:
            self.turn_progress = 1.0

        for drone_id in self.drone_pos:
            start = self.drone_start_pos[drone_id]
            target = self.drone_target_pos[drone_id]
            start_x, start_y = start
            target_x, target_y = target

            x = (start_x
                 + (target_x - start_x) * self.turn_progress)
            y = (start_y
                 + (target_y - start_y) * self.turn_progress)
            self.drone_pos[drone_id] = (x, y)

        if self.turn_progress >= 1.0:
            self.finish_turn()

    def finish_turn(self) -> None:
        """
        Completes the current turn and prepares the next one.

        Sets all drones to their final positions for the current turn,
        advances the turn counter and prepares the next turn if one exists.
        If there are no more turns, the animation is marked as finished.
        """

        for drone in self.drone_pos:
            self.drone_pos[drone] = self.drone_target_pos[drone]

        self.current_turn += 1

        if str(self.current_turn) not in self.turns:
            self.animation_finished = True
            return

        self.prepare_turn()

    def toggle_pause(self) -> None:
        """
        Pauses or resumes the animation.
        """

        self.paused = not self.paused

    def restart(self) -> None:
        """
        Restarts the animation from the beginning.

        Resets every drone to the starting hub, resets the turn counter
        and animation state, and prepares the first turn.
        """

        start = self.node_coords["start"]
        for drone in self.drone_pos:
            self.drone_pos[drone] = (float(start[0]), float(start[1]))
            self.drone_angles[drone] = 0.0
        self.current_turn = 1
        self.turn_progress = 0.0
        self.animation_finished = False
        self.paused = False

        if str(self.current_turn) in self.turns:
            self.prepare_turn()
        else:
            self.animation_finished = True

    def next_turn(self) -> None:
        """
        Advances directly to the next simulation turn.

        Immediately completes the current turn, moves all drones to their
        target positions and prepares the following turn. The animation is
        paused after advancing.
        """

        if self.animation_finished:
            return

        for drone in self.drone_pos:
            self.drone_pos[drone] = self.drone_target_pos[drone]

        self.current_turn += 1
        if str(self.current_turn) not in self.turns:
            self.animation_finished = True
            return

        self.prepare_turn()
        self.paused = True

    def previous_turn(self) -> None:
        """
        Moves back to the previous simulation turn.

        Reconstructs the drone positions from the beginning of the
        simulation until reaching the requested turn, then prepares that
        turn for display.

        If the current turn is the first turn, the animation is restarted
        and paused.
        """

        valid_turns = [int(turn) for turn in self.turns]
        last_turn = max(valid_turns)

        if self.current_turn > last_turn:
            target_turn = last_turn
        else:
            target_turn = self.current_turn - 1

        if target_turn < 1:
            self.restart()
            self.paused = True
            return

        self.reset_positions()
        for turn_number in range(1, target_turn):
            self.current_turn = turn_number
            self.prepare_turn()
            for drone in self.drone_pos:
                self.drone_pos[drone] = self.drone_target_pos[drone]

        self.current_turn = target_turn
        self.animation_finished = False
        self.turn_progress = 0.0
        self.prepare_turn()

        self.paused = True

    def reset_positions(self) -> None:
        """
        Resets all drones to the starting hub.

        Resets the current, starting and target positions of every drone,
        as well as their orientation.
        """

        start_pos = self.node_coords["start"]

        for drone in self.drone_pos:
            self.drone_pos[drone] = (float(start_pos[0]), float(start_pos[1]))
            self.drone_start_pos[drone] = (float(start_pos[0]),
                                           float(start_pos[1]))
            self.drone_target_pos[drone] = (float(start_pos[0]),
                                            float(start_pos[1]))
            self.drone_angles[drone] = 0.0

    def draw_drone(self, position: tuple[float, float],
                   angle: float, color: str) -> None:
        """
        Draws a single drone as a rotated triangle.

        Calculates the coordinates of the triangle's vertices after
        applying the specified rotation and draws the resulting polygon
        on the Pygame surface.

        Args:
            position: Screen coordinates where the drone is drawn.
            angle: Rotation angle of the drone in radians.
            color: Color used to fill the drone.
        """

        x, y = position
        size = self.drone_size
        triangle = [(size, 0), (-size, -size), (-size, size)]
        rotated_points: list[tuple[float, float]] = []
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        for point_x, point_y in triangle:
            rotated_x = (point_x * cos_angle - point_y * sin_angle)
            rotated_y = (point_x * sin_angle + point_y * cos_angle)
            rotated_points.append((x + rotated_x, y + rotated_y))
        pygame.draw.polygon(self.screen, color, rotated_points)
        pygame.draw.polygon(self.screen, "white", rotated_points, 1)

    def draw(self) -> None:
        """
        Draws all drones on the Pygame surface.

        Uses each drone's current position, orientation and assigned color
        to render it on the screen.
        """

        for drone in self.drone_pos:
            position = self.drone_pos[drone]
            angle = self.drone_angles[drone]
            color = self.drone_colors[drone]
            self.draw_drone(position, angle, color)
