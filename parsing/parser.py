from .processors import Hub, Connection
from pydantic import ValidationError
from typing import Any, Protocol
import sys
import re


class FormatError(Exception):
    pass


class Formatter(Protocol):
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
        pass


class FormatHub:
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
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
                    raise FormatError(f"ERROR (line {line}):"
                                      " unknown key ({k})")

        except IndexError:
            print(f"ERROR (line {line}): missing required info",
                  file=sys.stderr)
            sys.exit(1)
        except FormatError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        return info


class FormatCon:
    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
        info: dict[str, Any] = {}

        try:
            info['name'] = name
            if "-" not in data[0]:
                raise FormatError(f"ERROR (line {line}):"
                                  " zones should be connected by '-")
            info['zone_a'], info['zone_b'] = data[0].split('-')
            for i in range(0, len(metadata)):
                k, v = metadata[i].split('=')
                if k == "max_link_capacity":
                    info['max_link_capacity'] = v
                else:
                    raise FormatError(f"ERROR (line {line}):"
                                      " unknown key ({k})")
        except IndexError:
            print(f"ERROR (line {line}): missing required info",
                  file=sys.stderr)
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
        self.line: int = 1
        self.read_and_validate()

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
                self.line += 1
                continue

            index = line.find(":")
            if (
                index < 0
                or index != line.rfind(":")
                or not line[:index]
                or not line[index + 1:]
            ):
                print(f"ERROR (line {self.line}): *.txt should have lines "
                      "with HUB: Info []", file=sys.stderr)
                sys.exit(1)

            if line.count('[') > 1 or line.count(']') > 1:
                print(f"ERROR (line {self.line}): *.txt should have lines "
                      "with HUB: Info []", file=sys.stderr)
                sys.exit(1)

            k, v = line.split(":")
            self.process_line(k, v.strip())
            self.line += 1

    def process_line(self, key: str, info: str) -> None:
        try:
            if key == "nb_drones":
                v = int(info)
                if v <= 0:
                    raise ValueError(f"ERROR (line {self.line}):"
                                     f" {key} must be a"
                                     f"positive int: ({info})")
                self.nb_drones = v
            elif key in ['hub', 'start_hub', 'end_hub'] or key == "connection":
                match: list[str] = re.findall(r'\[(.*?)\]', info)
                metadata: list[str] = match[0].split() if match else []
                info = info.replace(match[0], '') if match else info
                if 'hub' in key:
                    hub_info: dict[str, Any] = FormatHub.format(
                        key, info.split(), metadata, self.line)
                    if key == "start_hub":
                        n_change: str = ' ' + info.split()[0] + ' '
                        c_change: str = '-' + info.split()[0]
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                n_change, "start")
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                c_change, "-start")
                    if key == "end_hub":
                        na_change: str = ' ' + info.split()[0] + ' '
                        co_change: str = '-' + info.split()[0]
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                na_change, "end")
                        for i in range(0, len(self.content)):
                            self.content[i] = self.content[i].replace(
                                co_change, "-end")
                    hub_info['nb_drones'] = self.nb_drones
                    Hub(hub_info, line=self.line)
                else:
                    self.nb_con += 1
                    con_info: dict[str, Any] = FormatCon.format(
                        str(self.nb_con), info.split(), metadata, self.line)
                    con_info['line'] = self.line
                    Connection(con_info)
            else:
                print(f"ERROR (line {self.line}):"
                      " undefined key ({key})", file=sys.stderr)
                sys.exit(1)

        except ValidationError as e:
            print(f"ERROR (line {self.line}):",
                  e.errors()[0]["msg"], file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
