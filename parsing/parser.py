from .processors import Hub, Connection
from pydantic import ValidationError
from typing import Any, Protocol
import traceback
import sys
import re


class FormatError(Exception):
    pass


class Formatter(Protocol):
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str]) -> dict[str, Any]:
        pass


class FormatHub:
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str]) -> dict[str, Any]:
        info: dict[str, Any] = {}

        try:
            if name == "start_hub":
                info['name'] = "start"
            elif name == "end_hub":
                info['name'] = "end"
            else:
                info['name'] = data[0]
            info['coord'] = [data[1], data[2]]
            for i in range(0, len(metadata)):
                k, v = metadata[i].split('=')
                if k == "color":
                    info['color'] = v
                elif k == "zone":
                    info['zone'] = v
                elif k == "max_drones":
                    info['max_drones'] = v
                else:
                    raise FormatError(f"ERROR: unknown key ({k})")

        except IndexError:
            print("ERROR: missing required info", file=sys.stderr)
            sys.exit(1)
        except FormatError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        return info


class FormatCon:
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str]) -> dict[str, Any]:
        info: dict[str, Any] = {}

        try:
            info['name'] = name
            if "-" not in data[0]:
                raise FormatError("ERROR: zones should be connected by '-")
            info['zone_a'], info['zone_b'] = data[0].split('-')
            for i in range(0, len(metadata)):
                k, v = metadata[i].split('=')
                if k == "max_link_capacity":
                    info['max_link_capacity'] = v
                else:
                    raise FormatError(f"ERROR: unknown key ({k})")
        except IndexError:
            print("ERROR: missing required info", file=sys.stderr)
            sys.exit(1)
        except FormatError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        return info


class ParseMap:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.nb_con: int = 0
        self.content: list[str]

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

        self.content = info.split('\n')
        for line in self.content:
            if not line.strip() or line.startswith("#"):
                continue
            elif line.startswith("nb_drones:"):
                break
            else:
                sys.exit("ERROR: <nb_drones> must be the first line")

        for line in self.content:
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
                      "with HUB: Info []", file=sys.stderr)
                sys.exit(1)

            if line.count('[') > 1 or line.count(']') > 1:
                print("ERROR: *.txt should have lines "
                      "with HUB: Info []", file=sys.stderr)
                sys.exit(1)

            k, v = line.split(":")
            self.process_line(k, v.strip())

    def process_line(self, key: str, info: str) -> None:
        try:
            if key == "nb_drones":
                v = int(info)
                if v <= 0:
                    raise ValueError(f"ERROR: {key} must be a"
                                     "positive int: <{info}>")
                self.nb_drones = v
            elif "hub" in key or key == "connection":
                match: list[str] = re.findall(r'\[(.*?)\]', info)
                metadata: list[str] = match[0].split() if match else []
                info = info.replace(match[0], '') if match else info
                if "hub" in key:
                    hub_info: dict[str, Any] = FormatHub.format(
                        key, info.split(), metadata)
                    if key == "start_hub":
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                info.split()[0], "start")
                    if key == "end_hub":
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                info.split()[0], "end")
                    hub_info['nb_drones'] = self.nb_drones
                    Hub(hub_info)
                else:
                    self.nb_con += 1
                    con_info: dict[str, Any] = FormatCon.format(
                        str(self.nb_con), info.split(), metadata)
                    Connection(con_info)
            else:
                print(f"ERROR: undefined key ({key})", file=sys.stderr)
                sys.exit(1)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except ValidationError as e:
            print("ERROR:", e.errors()[0]["msg"])
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(1)
