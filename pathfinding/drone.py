from .move import Move


class Drone:
    def __init__(self, id: int, path: list[str], cost: int) -> None:
        self.id: int = id

        self.pos: str = 'start'
        self.path: list[str] = path
        self.cost: int = cost
        self.waiting_turns: int = 0
        self.finished: bool = False
        self.movement: Move = Move.still

        self.transit: bool = False
        self.target: str | None = None

    def get_next_node(self) -> str:
        idx = self.path.index(self.pos)
        return self.path[idx + 1]

    def start_transit(self, target: str) -> None:
        self.target = target
        self.movement = Move.connect
        self.transit = True
        self.cost -= 1

    def complete_transit(self) -> None:
        if self.target is None:
            raise ValueError("ERROR: Drone in transit without target")
        self.pos = self.target
        self.target = None
        self.transit = False
        self.movement = Move.move
        self.cost -= 1
        if self.pos == "end":
            self.finished = True

    def move_drone(self, target: str) -> None:
        self.pos = target
        self.movement = Move.move
        self.waiting_turns = 0
        self.cost -= 1
        if self.pos == "end":
            self.finished = True
