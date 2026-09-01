from parsing import FormatError
from collections import deque
from typing import Any
import json


class SimulationSetup:

    def __init__(self) -> None:
        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open("data/connections.json", 'r', encoding='utf-8') as f:
            self.connections: dict[str, list[str]] = json.load(f)

    def get_shortest_path(
            self, start_node: str = "start",
            blocked_con: list[tuple[str, str]] | None = None,
            blocked_hubs: list[str] | None = None) -> tuple[int, list[str]]:
        if blocked_con is None:
            blocked_con = []
        if blocked_hubs is None:
            blocked_hubs = []
        queue = deque([[start_node]])
        visited: list[str] = []
        cost: int = 0

        while queue:
            curr_path = queue.popleft()
            curr_node = curr_path[-1]
            visited.append(curr_node)

            if curr_node == 'end':
                for node in curr_path:
                    if node != 'end':
                        if self.data['hub'][node]['zone'] == "restricted":
                            cost += 2
                        else:
                            cost += 1
                return cost, curr_path
            neighbors: list[str] = [i for i in self.connections[curr_node]]
            for node in neighbors:
                if (curr_node, node) in blocked_con or node in blocked_hubs:
                    continue
                if (
                    node not in visited
                    and self.data['hub'][node]['zone'] != 'blocked'
                ):
                    visited.append(node)
                    queue.append(curr_path + [node])
        raise FormatError("ERROR: end is not reachable")

    def get_nb_drones(self) -> Any:
        return self.data['nb_drones']

    def get_max_flow(self) -> int:
        max_flow: int = self.get_nb_drones()

        for node in self.data['hub'].values():
            if node['max_drones'] < max_flow:
                max_flow = node['max_drones']
        for con in self.data['connection'].values():
            if con['max_link_capacity'] < max_flow:
                max_flow = con['max_link_capacity']
        return max_flow
