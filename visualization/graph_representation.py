from .drone_manager import DroneManager
from .map_renderer import MapRenderer
import pygame
import json


class GraphRepresentation:

    def __init__(self) -> None:
        with open("data/map.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
        with open("data/connections.json", "r", encoding="utf-8") as f:
            self.connections = json.load(f)
        with open("data/turns.json", "r", encoding="utf-8") as f:
            self.turns = json.load(f)

        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Fly-in")
        self.clock = pygame.time.Clock()

        self.map_renderer = MapRenderer(self.screen, self.data,
                                        self.connections)
        self.drone_manager = DroneManager(self.screen, self.data,
                                          self.turns,
                                          self.map_renderer.node_coords,
                                          self.map_renderer.drone_size)
        self.render()

    def draw_menu(self) -> None:
        font = pygame.font.Font(None, 24)
        pygame.draw.rect(self.screen, "black", (0, 660, 1280, 60))
        instructions = [
            ("SPACE", "Pausar/Reanudar"),
            ("R", "Reiniciar"),
            ("<-", "Retroceder"),
            ("->", "Avanzar"),
            ("ESC", "Salir"),
        ]
        x = 30
        for key, description in instructions:
            text = font.render(
                f"{key}: {description}",
                True,
                "white")
            self.screen.blit(text, (x, 680))
            x += text.get_width() + 35

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.drone_manager.toggle_pause()
                elif event.key == pygame.K_r:
                    self.drone_manager.restart()
                elif event.key == pygame.K_RIGHT:
                    self.drone_manager.next_turn()
                elif event.key == pygame.K_LEFT:
                    self.drone_manager.previous_turn()

        return True

    def render(self) -> None:
        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()

            self.map_renderer.update_rainbow(dt)
            self.drone_manager.update(dt)

            self.screen.fill("black")
            self.map_renderer.draw_map()
            self.drone_manager.draw()
            self.draw_menu()

            pygame.display.flip()

        pygame.quit()
