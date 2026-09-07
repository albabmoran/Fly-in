from .simulation_setup import SimulationSetup
from parsing import FormatError
from .drone import Drone
from .move import Move
from typing import Any
import json


class StateMachine:
    """Controls the drone simulation turn by turn.

    The state machine creates the drones, manages their movements through
    the map, resolves conflicts caused by capacity restrictions, and stores
    the result of each simulation turn.
    """

    def __init__(self) -> None:
        """
        Initializes the simulation state.

        Loads the map configuration, retrieves the number of drones and
        maximum flow, initializes the drone list and simulation results,
        and starts the simulation.
        """

        self.setup = SimulationSetup()

        self.nb_drones = self.setup.get_nb_drones()
        self.max_flow = self.setup.get_max_flow()
        self.drones: list[Drone] = []

        self.turn: int = 0
        self.result: dict[int, Any] = {}
        self.run()

    def instantiate_drones(self) -> None:
        """
        Creates all drones using the shortest available path.

        Each drone is initialized with a copy of the shortest path and
        its corresponding movement cost.

        Returns:
            None
        """

        cost, path = self.setup.get_shortest_path()

        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(i, path.copy(), cost))

    def run(self) -> None:
        """
        Runs the simulation until all drones reach the end.

        Initializes the drones and executes one simulation step per turn.
        Once all drones have finished, the results are saved to both a text
        log file and a JSON file.

        Returns:
            None
        """

        self.instantiate_drones()
        while not all(drone.finished for drone in self.drones):
            self.turn += 1
            self.simulation()
        self.convert_to_txt()
        self.convert_to_json()
        print(f'\033[32;1m    Map solved in {self.turn} turns'
              ', movements saved in data/log.txt\033[0m')

    def connection_conflict(self, start: str, target: str,
                            turn_movement: list[dict[str, Any]]) -> bool:
        """
        Checks whether a connection has reached its capacity.

        Counts the number of drones already using the same connection
        during the current turn and compares it with the maximum allowed
        flow.

        Args:
            start: Name of the node from which the connection starts.
            target: Name of the node to which the connection leads.
            turn_movement: Movements already scheduled for the current
                turn.

        Returns:
            'True' if the connection has reached its maximum capacity,
            otherwise 'False'.
        """

        con_use: int = 0
        for drone in turn_movement:
            if drone['start'] == start and drone['target'] == target:
                con_use += 1
        return con_use >= self.max_flow

    def restricted_conflict(self, target: str,
                            turn_movement: list[dict[str, Any]]) -> bool:
        """
        Checks whether a restricted hub has reached its capacity.

        Calculates the number of drones currently occupying the target hub,
        the drones leaving it during the current turn and the drones
        entering it. The resulting occupancy is compared with the maximum
        allowed flow.

        Args:
            target: Name of the restricted hub being checked.
            turn_movement: Movements already scheduled for the current
                turn.

        Returns:
            'True' if the restricted hub would exceed its capacity,
            otherwise 'False'.
        """

        occupied: int = 0
        outgoing: int = 0
        incoming: int = 0

        for drone in self.drones:
            if drone.pos == target and not drone.transit:
                occupied += 1
            if drone.transit and drone.target == target:
                incoming += 1
        for movement in turn_movement:
            if movement["start"] == target:
                outgoing += 1
        return occupied - outgoing + incoming >= self.max_flow

    def is_restricted(self, hub: str) -> Any:
        """
        Checks whether a hub is a restricted zone.

        Args:
            hub: Name of the hub to check.

        Returns:
            'True' if the hub is in the restricted zone, otherwise
            'False'.
        """

        return self.setup.data['hub'][hub]['zone'] == 'restricted'

    def resolve_conflict(
            self, drone: Drone,
            blocked_con: list[tuple[str, str]] | None = None,
            blocked_hubs: list[str] | None = None) -> bool:
        """
        Attempts to find an alternative path for a blocked drone.

        Calculates a new shortest path while avoiding the specified blocked
        connections or hubs. The new path is only accepted if its cost is
        lower than the cost of waiting for one turn.

        If no valid path is available, or the alternative path is not more
        efficient than waiting, the drone remains stationary for the turn.

        Args:
            drone: Drone whose movement is blocked.
            blocked_con: Connections that must be avoided when calculating
                the alternative path.
            blocked_hubs: Hubs that must be avoided when calculating the
                alternative path.

        Returns:
            'True' if an alternative path was found and assigned to the
            drone, otherwise 'False'.
        """

        if blocked_con is None:
            blocked_con = []
        if blocked_hubs is None:
            blocked_hubs = []

        try:
            new_cost, new_path = self.setup.get_shortest_path(
                start_node=drone.pos,
                blocked_con=blocked_con,
                blocked_hubs=blocked_hubs)
        except FormatError:
            drone.movement = Move.still
            drone.waiting_turns += 1
            return False

        waiting_cost = drone.cost + 1
        if new_cost < waiting_cost:
            drone.path = new_path
            drone.cost = new_cost
            drone.waiting_turns = 0
            return True
        else:
            drone.movement = Move.still
            drone.waiting_turns += 1
            return False

    def execute_move(self, drone: Drone,
                     turn_movement: list[dict[str, Any]]) -> None:
        """
        Executes the next movement of a drone.

        Determines the drone's next node and performs either a normal move
        or starts a transit if the target node is restricted. The movement
        is then registered in the movements of the current turn.

        Args:
            drone: Drone that will perform the movement.
            turn_movement: List containing the movements already scheduled
                for the current turn.

        Returns:
            None
        """

        target = drone.get_next_node()
        start = drone.pos

        if self.is_restricted(target):
            drone.start_transit(target)
        else:
            drone.move_drone(target)
        turn_movement.append({"drone": drone.id,
                              "start": start,
                              "target": target})

    def save_turn_result(self, finished_drones: list[Drone]) -> None:
        """
        Stores the movements and positions for the current turn.

        Finished drones are excluded from the result. Drones in transit
        store their current position and target, while drones that have
        moved to a hub store their current position.

        Args:
            finished_drones: Drones that have completed their path and
                should not be included in the current turn's output.

        Returns:
            None
        """

        self.result[self.turn] = {}

        for drone in self.drones:
            if drone in finished_drones:
                continue
            if drone.movement == 1:
                self.result[self.turn][drone.id] = {
                    "movement": drone.movement.value,
                    "hub": f'{drone.pos}-{drone.target}'}
            elif drone.pos == 'start':
                continue
            else:
                self.result[self.turn][drone.id] = {
                    "movement": drone.movement.value,
                    "hub": drone.pos}

    def simulation(self) -> None:
        """
        Executes one turn of the drone simulation.

        Processes every drone that has not finished its path, completing
        ongoing transits, checking movement conflicts and executing valid
        movements. When a conflict occurs, an alternative path may be
        calculated.

        After all drones have been processed, the result of the current
        turn is saved.

        Returns:
            None
        """

        turn_movement: list[dict[str, Any]] = []
        finished_drones: list[Drone] = []

        for drone in self.drones:
            if drone.finished:
                finished_drones.append(drone)
                continue
            if drone.transit:
                turn_movement.append({"drone": drone.id,
                                      "start": drone.pos,
                                      "target": drone.target,
                                      })
                drone.complete_transit()
                continue

            next_node = drone.get_next_node()
            if self.is_restricted(next_node):
                if self.restricted_conflict(next_node, turn_movement):
                    new_target = self.resolve_conflict(
                        drone=drone, blocked_hubs=[next_node])
                    if new_target:
                        self.execute_move(drone, turn_movement)
                else:
                    self.execute_move(drone, turn_movement)
            else:
                if self.connection_conflict(drone.pos, next_node,
                                            turn_movement):
                    new_target = self.resolve_conflict(
                        drone=drone,
                        blocked_con=[(drone.pos, next_node)])
                    if new_target:
                        self.execute_move(drone, turn_movement)
                else:
                    self.execute_move(drone, turn_movement)

        self.save_turn_result(finished_drones)

    def convert_to_txt(self) -> None:
        """
        Saves the simulation results to a text log.

        Converts the stored turn results into the expected drone movement
        format and writes them to 'data/log.txt'.

        Returns:
            None
        """

        with open("data/log.txt", "w", encoding="utf-8") as f:
            lines: list[str] = []
            for turn in self.result.values():
                drones: list[str] = []
                for id, data in turn.items():
                    drones.append(f"D{id}-{data['hub']}")
                lines.append(" ".join(drones))
            f.write("\n".join(lines))

    def convert_to_json(self) -> None:
        """
        Saves the simulation results to a JSON file.

        Writes the turn-by-turn simulation results to
        'data/turns.json' using an indented JSON format.

        Returns:
            None
        """

        with open("data/turns.json", 'w', encoding='utf-8') as f:
            json.dump(self.result, f, indent=4)
