import pygame
import json

class GraphRepresentation():
    def __init__(self) -> None:
        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.render()
    def draw_hub(self, color, x, y) -> None:
         pygame.draw.circle(self.screen, color, 
                                  [x, y], 30, 0)
    def render(self) -> None:
        pygame.display.set_caption("Fly-in")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            for hub in self.data['hub'].values():
                x = hub['coord'][0] * 100
                y = hub['coord'][1] * 100
                color = hub['color']
                self.draw_hub(color, 100 + x, 360 - y)
            pygame.display.flip()

        pygame.quit()

GraphRepresentation()