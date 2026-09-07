from .simulation_setup import SimulationSetup
from parsing import FormatError
from .drone import Drone
from .move import Move
from typing import Any
import json


class StateMachine:
    def __init__(self) -> None:
        self.setup = SimulationSetup()

        self.nb_drones = self.setup.get_nb_drones()
        self.max_flow = self.setup.get_max_flow()
        self.drones: list[Drone] = []

        self.turn: int = 0
        self.result: dict[int, Any] = {}
        self.run()

    def instantiate_drones(self) -> None:
        cost, path = self.setup.get_shortest_path()

        for i in range(1, self.nb_drones + 1):
            self.drones.append(Drone(i, path.copy(), cost))

    def run(self) -> None:
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
        con_use: int = 0
        for drone in turn_movement:
            if drone['start'] == start and drone['target'] == target:
                con_use += 1
        return con_use >= self.max_flow

    def restricted_conflict(self, target: str,
                            turn_movement: list[dict[str, Any]]) -> bool:
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
        return self.setup.data['hub'][hub]['zone'] == 'restricted'

    def resolve_conflict(self, drone: Drone,
                         blocked_con: list[tuple[str, str]] | None = None,
                         blocked_hubs: list[str] | None = None) -> bool:
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
        with open("data/log.txt", "w", encoding="utf-8") as f:
            lines: list[str] = []
            for turn in self.result.values():
                drones: list[str] = []
                for id, data in turn.items():
                    drones.append(f"D{id}-{data['hub']}")
                lines.append(" ".join(drones))
            f.write("\n".join(lines))

    def convert_to_json(self) -> None:
        with open("data/turns.json", 'w', encoding='utf-8') as f:
            json.dump(self.result, f, indent=4)
