import pygame
import math
import json


class GraphRepresentation():

    def __init__(self) -> None:
        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open("data/connections.json", 'r', encoding='utf-8') as f:
            self.con = json.load(f)
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.center: tuple[int, int] = (640, 360)
        self.node_coords: dict[str, tuple[int, int]] = {}
        self.max_x: int = 0
        self.max_y: int = 0
        self.x_center: int | float = self.get_center_coords()
        self.sep: int
        self.circle_size: int
        self.get_sep_and_size(self.max_x, self.max_y)
        self.render()

    def get_sep_and_size(self, max_x: int, max_y: int):
        if max_y > 3:
            self.sep = 50
            self.circle_size = 10
        elif 0 <= max_x <= 8:
            self.sep = 120
            self.circle_size = 30
        elif 8 < max_x <= 16:
            self.sep = 85
            self.circle_size = 20
        elif 16 < max_x:
            self.sep = 50
            self.circle_size = 10

    def get_center_coords(self) -> int:
        max_x: int = 0
        min_x: int = 0
        max_y: int = 0
        for hub in self.data['hub'].values():
            if hub['coord'][0] >= max_x:
                max_x = hub['coord'][0]
            elif hub['coord'][0] < min_x:
                min_x = hub['coord'][0]
            elif hub['coord'][1] > max_y:
                max_y = hub['coord'][1]
        x_center: int | float = (max_x - min_x) / 2
        self.max_x = max_x
        self.max_y = max_y
        return x_center

    def get_node_coords(self, next_node: str) -> tuple[int, int]:
        scale_x: int = self.x_center - self.data['hub'][next_node]['coord'][0]
        x = self.center[0] - self.sep * scale_x
        y = self.center[1] - self.sep * self.data['hub'][next_node]['coord'][1]

        return x, y

    def draw_connection(self, node: str, start_x: int | float,
                        start_y: int | float) -> None:
        if not self.con[node]:
            return
        else:
            for next_node in self.con[node]:
                end_x, end_y = self.get_node_coords(next_node)
                pygame.draw.line(self.screen, 'grey', [start_x, start_y],
                                 [end_x, end_y], 2)
                self.con[node].remove(next_node)
                self.con[next_node].remove(node)

    def draw_hub(self, color, x, y, size) -> None:
        if color == 'rainbow':
            # hacer color rainbow
            pygame.draw.circle(self.screen, 'green',
                               [x, y], size, 0)
        else:
            pygame.draw.circle(self.screen, color,
                               [x, y], size, 0)
        pygame.draw.circle(self.screen, 'white', [x, y], size, 1)

    def render(self) -> None:
        pygame.display.set_caption("Fly-in")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.QUIT:
                    running = False

            for hub in self.data['hub'].values():
                scale_x: int = self.x_center - hub['coord'][0]
                x = self.center[0] - self.sep * scale_x
                y = self.center[1] - self.sep * hub['coord'][1]
                color = hub['color']
                node = next(k for k, v in self.data['hub'].items() if v == hub)
                if node in self.con:
                    self.draw_connection(node, x, y)
                self.node_coords[node] = (x, y)
                self.draw_hub(color, x, y, self.circle_size)

            for i in range(1, self.data['nb_drones']):
                points: list[int | float] = []
                for i in range(3):
                    angle = i * (2 * math.pi / 3)
                    x = (self.node_coords['start'][0]
                         + self.circle_size * math.cos(angle))
                    y = (self.node_coords['start'][1]
                         + self.circle_size * math.sin(angle))
                    points.append((x, y))
                pygame.draw.polygon(self.screen, 'red', points, 0)

            pygame.display.flip()

        pygame.quit()


GraphRepresentation()
