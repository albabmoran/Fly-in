from .move import Move


class Drone:
    """
    Represents a drone moving through the map.

    A drone stores its current position, planned path, movement cost and
    state during the simulation. It can move between connected nodes or
    remain in transit when a connection requires multiple turns.
    """

    def __init__(self, id: int, path: list[str], cost: int) -> None:
        """
        Initializes a drone with its path and movement cost.

        Args:
            id: Unique identifier of the drone.
            path: Ordered list of nodes that the drone must traverse.
            cost: Initial movement cost available to the drone.

        Returns:
            None
        """

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
        """
        Gets the next node in the drone's planned path.

        Returns:
            The name of the next node the drone should reach.
        """

        idx = self.path.index(self.pos)
        return self.path[idx + 1]

    def start_transit(self, target: str) -> None:
        """
        Starts the drone's transit to a target node.

        Sets the target node and changes the drone state to indicate that
        it is currently traversing a connection.

        Args:
            target: Name of the node the drone is travelling towards.

        Returns:
            None
        """

        self.target = target
        self.movement = Move.connect
        self.transit = True
        self.cost -= 1

    def complete_transit(self) -> None:
        """
        Completes the drone's transit and updates its position.

        Moves the drone to its target node, clears its transit state and
        updates its movement status. If the target is the end node, the
        drone is marked as finished.

        Returns:
            None

        Raises:
            ValueError: If the drone is in transit without a target node.
        """

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
        """
        Moves the drone directly to a target node.

        Updates the drone's position and movement state, resets its waiting
        turns and decreases its remaining movement cost. If the target is
        the end node, the drone is marked as finished.

        Args:
            target: Name of the node where the drone will move.

        Returns:
            None
        """

        self.pos = target
        self.movement = Move.move
        self.waiting_turns = 0
        self.cost -= 1
        if self.pos == "end":
            self.finished = True
