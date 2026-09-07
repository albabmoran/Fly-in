from typing import Any
import math
import random
import pygame


class DroneManager:

    def __init__(self, screen: pygame.Surface, data: dict[str, Any],
                 turns: dict[str, Any],
                 node_coords: dict[str, tuple[int, int]],
                 drone_size: int) -> None:
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
        """Create all drones at the starting hub."""

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
        Prepare the positions and targets for the current turn.
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
        Update the position of every drone during the current turn.
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

            # Linear interpolation between start and target.
            x = (start_x
                 + (target_x - start_x) * self.turn_progress)
            y = (start_y
                 + (target_y - start_y) * self.turn_progress)
            self.drone_pos[drone_id] = (x, y)

        if self.turn_progress >= 1.0:
            self.finish_turn()

    def finish_turn(self) -> None:
        """
        Save the final positions of the current turn
        and prepare the next one.
        """

        for drone in self.drone_pos:
            self.drone_pos[drone] = self.drone_target_pos[drone]

        self.current_turn += 1

        if str(self.current_turn) not in self.turns:
            self.animation_finished = True
            return

        self.prepare_turn()

    def toggle_pause(self) -> None:
        """Pause or resume the animation."""

        self.paused = not self.paused

    def restart(self) -> None:
        """Restart the animation from the beginning."""

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
        Advance directly to the next turn.

        The current turn is completed immediately and the
        following turn is prepared.
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
        Go back one turn.

        The animation is reconstructed from the beginning
        until the desired turn.
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
        """Put every drone back at the start."""

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
        """Draw one drone as a triangle."""

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
        """Draw all drones."""

        for drone in self.drone_pos:
            position = self.drone_pos[drone]
            angle = self.drone_angles[drone]
            color = self.drone_colors[drone]
            self.draw_drone(position, angle, color)
