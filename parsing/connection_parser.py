from typing import Any
import json


class ParseCon():
    """
    Parses map connections from a JSON file into an adjacency dictionary.

    This class reads the map data from 'data/map.json', extracts the
    connections between zones, converts them into an adjacency dictionary,
    and saves the result to 'data/connections.json'.
    """

    def __init__(self) -> None:
        """
        Initializes the connection parser and processes the map data.

        The initialization loads the map data, converts its connections into
        an adjacency dictionary, and writes the resulting data to a JSON file.
        """

        self.connections: dict[str, list[str]] = {}
        self.data: dict[str, Any] = {}
        self.extract_from_json()
        self.convert_connections()
        self.convert_to_json()

    def extract_from_json(self) -> None:
        """
        Loads map data from the input JSON file.

        Reads the map information stored in 'data/map.json' and saves it
        in the 'data' instance attribute.

        Returns:
            None
        """

        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def convert_connections(self) -> None:
        """
        Converts map connections into an adjacency dictionary.

        Each connection is represented in both directions. For example, if
        zone A is connected to zone B, then B is added to A's list of
        connections and A is added to B's list.

        Returns:
            None
        """

        for c in self.data['connection'].values():
            if c['zone_a'] not in self.connections:
                self.connections[c['zone_a']] = []
            if c['zone_b'] not in self.connections[c['zone_a']]:
                self.connections[c['zone_a']].append(c['zone_b'])
            if c['zone_b'] not in self.connections:
                self.connections[c['zone_b']] = []
            if c['zone_a'] not in self.connections[c['zone_b']]:
                self.connections[c['zone_b']].append(c['zone_a'])

    def convert_to_json(self) -> None:
        """
        Saves the converted connections to a JSON file.

        Writes the adjacency dictionary stored in 'connections' to
        'data/connections.json' using an indented JSON format.

        Returns:
            None
        """
        with open("data/connections.json", 'w', encoding='utf-8') as f:
            json.dump(self.connections, f, indent=4)
