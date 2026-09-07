from typing import Any
import pygame


class MapRenderer:

    def __init__(self, screen: pygame.Surface, data: dict[str, Any],
                 connections: dict[str, list[str]]) -> None:
        self.screen = screen
        self.data = data
        self.connections = connections

        self.center: tuple[int, int] = (640, 360)
        self.node_coords: dict[str, tuple[int, int]] = {}
        self.max_x: int = 0
        self.max_y: int = 0
        self.x_center: int | float = self.get_center_coords()

        self.sep: int = 0
        self.circle_size: int = 0
        self.drone_size: int = 0

        self.get_sep_and_size(self.max_x, self.max_y)
        self.calculate_node_coords()

        self.rainbow_time: float = 0.0

    def get_sep_and_size(self, max_x: int, max_y: int) -> None:
        if max_y > 3:
            self.sep = 50
            self.circle_size = 10
            self.drone_size = 12

        elif 0 <= max_x <= 8:
            self.sep = 120
            self.circle_size = 30
            self.drone_size = 12

        elif 8 < max_x <= 16:
            self.sep = 85
            self.circle_size = 20
            self.drone_size = 10

        elif max_x > 16:
            self.sep = 50
            self.circle_size = 10
            self.drone_size = 8

    def get_center_coords(self) -> int | float:
        max_x: int = 0
        min_x: int = 0
        max_y: int = 0

        for hub in self.data["hub"].values():
            x = hub["coord"][0]
            y = hub["coord"][1]

            if x > max_x:
                max_x = x
            if x < min_x:
                min_x = x
            if y > max_y:
                max_y = y

        self.max_x = max_x
        self.max_y = max_y
        return (max_x - min_x) / 2

    def get_node_coords(self, node: str) -> tuple[int, int]:
        scale_x = (
            self.x_center
            - self.data["hub"][node]["coord"][0]
        )
        x = self.center[0] - self.sep * scale_x
        y = (
            self.center[1]
            - self.sep * self.data["hub"][node]["coord"][1]
        )

        return int(x), int(y)

    def calculate_node_coords(self) -> None:
        for node in self.data["hub"]:
            self.node_coords[node] = self.get_node_coords(node)

    def draw_connections(self) -> None:
        drawn_connections: set[tuple[str, str]] = set()

        for node, connections in self.connections.items():
            if node not in self.node_coords:
                continue

            for next_node in connections:
                connection = (node, next_node)
                if connection in drawn_connections:
                    continue
                drawn_connections.add(connection)
                start_x, start_y = self.node_coords[node]
                end_x, end_y = self.node_coords[next_node]
                pygame.draw.line(self.screen, "grey",
                                 (start_x, start_y), (end_x, end_y), 2)

    def get_rainbow_color(self) -> pygame.Color:
        colors: list[pygame.Color] = [
            pygame.Color("red"),
            pygame.Color("orange"),
            pygame.Color("yellow"),
            pygame.Color("green"),
            pygame.Color("blue"),
            pygame.Color("purple"),
        ]

        speed = 2.0
        position = (self.rainbow_time * speed) % len(colors)
        index = int(position)
        next_index = (index + 1) % len(colors)
        progress = position - index

        return colors[index].lerp(colors[next_index], progress)

    def update_rainbow(self, dt: float) -> None:
        self.rainbow_time += dt

    def draw_hub(self, color: str, x: int, y: int, size: int) -> None:
        if color == "rainbow":
            hub_color: pygame.Color = self.get_rainbow_color()
        else:
            hub_color = pygame.Color(color)

        pygame.draw.circle(self.screen, hub_color, (x, y), size)
        pygame.draw.circle(self.screen, "white", (x, y), size, 1)

    def draw_map(self) -> None:
        self.draw_connections()
        for node, position in self.node_coords.items():
            x, y = position
            color = self.data["hub"][node]["color"]
            self.draw_hub(color, x, y, self.circle_size)
