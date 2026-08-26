from typing import Any
import json


class ParseCon():

    def __init__(self) -> None:
        self.connections: dict[str, list[str]] = {}
        self.data: dict[str, Any] = {}

    def extract_from_json(self) -> None:
        with open("data/map.json", 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def convert_connections(self) -> None:
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
        with open("data/connections.json", 'w', encoding='utf-8') as f:
            json.dump(self.connections, f, indent=4)
