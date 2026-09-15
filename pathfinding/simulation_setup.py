from parsing import FormatError
from collections import deque
from typing import Any
import json


class SimulationSetup:
    """
    Provides the data and configuration required for the simulation.

    Loads the processed map and its connections from JSON files and provides
    methods to calculate shortest paths and the maximum number of drones
    that can be handled by the map.
    """

    def __init__(self) -> None:
        """
        Initializes the simulation setup.

        Loads the processed map data from 'data/map.json' and the
        adjacency information from 'data/connections.json'.
        """

        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open("data/connections.json", 'r', encoding='utf-8') as f:
            self.connections: dict[str, list[str]] = json.load(f)

    def get_shortest_path(
            self, start_node: str = "start",
            blocked_con: list[tuple[str, str]] | None = None,
            blocked_hubs: list[str] | None = None) -> tuple[int, list[str]]:
        """
        Finds the shortest available path from a node to the end.

        Uses a breadth-first search to find a path from 'start_node' to
        the 'end' node while avoiding blocked connections, blocked hubs
        and hubs belonging to the 'blocked' zone.

        The path cost depends on the zone of each hub. Entering a
        'restricted' zone costs two turns, while entering any other
        allowed zone costs one turn.

        Args:
            start_node: Name of the node from which the search starts.
                Defaults to 'start'.
            blocked_con: List of connections that cannot be used during
                the search. Each connection is represented as a tuple
                containing its two node names.
            blocked_hubs: List of hub names that cannot be visited during
                the search.

        Returns:
            A tuple containing the total cost of the path and the list of
            nodes that make up the path.

        Raises:
            FormatError: If the 'end' node cannot be reached from the
                starting node.
        """

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
            neighbors.sort(key=lambda
                           node: self.data['hub'][node]['zone'] != 'priority')
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
        """
        Returns the total number of drones in the map.

        Returns:
            The number of drones defined in the map.
        """

        return self.data['nb_drones']

    def get_max_flow(self) -> int:
        """
        Calculates the maximum number of drones the map can handle.

        The maximum flow is limited by the smallest capacity among all
        hubs and connections, as well as by the total number of drones.

        Returns:
            The maximum number of drones that can simultaneously be
            handled according to the map's hub and connection capacities.
        """

        max_flow: int = self.get_nb_drones()

        for node in self.data['hub'].values():
            if node['max_drones'] < max_flow:
                max_flow = node['max_drones']
        for con in self.data['connection'].values():
            if con['max_link_capacity'] < max_flow:
                max_flow = con['max_link_capacity']
        return max_flow
