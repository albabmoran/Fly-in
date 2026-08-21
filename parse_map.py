from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Optional
from enum import Enum
import sys
import traceback


class Zone(Enum):
    normal = "normal"
    restricted = "restricted"
    priority = "priority"
    blocked = "blocked"


class HubType(Enum):
    start_hub = "start_hub"
    hub = "hub"
    end_hub = "end_hub"


class Hub(BaseModel):
    h_type: HubType
    name: str
    c_x: int
    c_y: int
    zone: Optional[Zone] = Field(default=Zone.normal)
    color: Optional[str] = Field(default="grey")
    max_drones: Optional[int] = Field(default=1, ge=0)

    @model_validator(mode='after')
    def validate_hub(self) -> 'Hub':
        if "-" in self.name:
            raise ValidationError("Hub's name must not contain '-'")
        if " " in self.color:
            raise ValidationError("Hub's color must not contain ' '")
        return self


class Connection(BaseModel):
    start: str
    end: str
    max_link_capacity: Optional[int] = Field(ge=0)


class ParseMap:
    def __init__(self):
        self.hubs: list[Hub] = []
        self.connection: list[Connection] = []
        self.nb_drones: int = 0

    def validate_hub(self, h_type: str, content: str) -> None:
        info = content.split(" ")
        zone: str = ""
        color: str = ""
        max_drones: str = ""
        for i in range(0, len(info)):
            if "=" in info[i]:
                index = info[i].find("=")
                new_line = info[i][index + 1:]
                if "]" in new_line:
                    new_line.replace("]", "")
                if info[i][:index] == "color":
                    color = new_line
                if info[i][:index] == "zone":
                    zone = new_line
                if info[i][:index] == "max_drones":
                    max_drones = new_line
                new_line = info[i][index + 1:]
                info[i] = new_line
        try:
            new_hub = (Hub(h_type = HubType(h_type),
                                 name = info[0],
                                 c_x = info[1],
                                 c_y = info[2],
                                 zone = Zone(zone) if zone else None,
                                 color = color if color else None,
                                 max_drones = max_drones if max_drones else None
                                )
                            )
            for i in self.hubs:
                if i.name == new_hub.name:
                    raise ValueError("ERROR: each zone must have a unique name")
            self.hubs.append(new_hub)
        except ValidationError as e:
            print("ERROR:", e.errors()[0]["msg"])
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(e)
            print(traceback.format_exc()[35:], file=sys.stderr)
            sys.exit(1)


    def validate_connection(self, content: str) -> None:
        print("connection")

    def read_and_validate(self) -> None:
        if len(sys.argv) != 2:
            print("ERROR: invalid number of arguments. "
                  "<Usage: python3 fly-in.py *txt>", file=sys.stderr)
            sys.exit(2)

        try:
            with open(sys.argv[1], "r") as file:
                info = file.read()
        except OSError as e:
            print(f"ERROR reading file: {e}", file=sys.stderr)
            sys.exit(e.errno)

        content = info.split("\n")
        hub_types: list[HubType] = []
        for line in content:
            if not line.strip() or line.startswith("#"):
                continue

            index = line.find(":")
            if (
                index < 0
                or index != line.rfind(":")
                or not line[:index]
                or not line[index + 1:]
            ):
                print("ERROR: *.txt should have lines "
                      "with HUB: Info", file=sys.stderr)
                sys.exit(1)

            k, v = line.split(":")
            v = v.strip()
            if k == "nb_drones":
                try:
                    value = int(v)
                    if value <= 0:
                        raise ValueError
                    self.nb_drones = value
                except ValueError:
                    print(f"ERROR: {k} must be a positive int: <{v}>", file=sys.stderr)
                    sys.exit(1)
            elif "hub" in k:
                if (k == "start_hub" or k == "end_hub") and k in hub_types:
                    print(f"ERROR: duplicated {k}", file=sys.stderr)
                    sys.exit(1)
                hub_types.append(k)
                self.validate_hub(hub_types[-1], v)
            elif k == "connection":
                self.validate_connection(v)

        print("finish")


def main():
    test = Hub(h_type=HubType.start_hub, name="hola", c_x=0, c_y=1, zone=Zone.normal)
    print(test.h_type, test.name, test.c_x, test.c_y, test.zone, test.color, test.max_drones)
    map = ParseMap()
    map.read_and_validate()


main()