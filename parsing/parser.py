from .processors import Hub, Connection
from pydantic import ValidationError
from typing import Any, Protocol
import sys
import re


class FormatError(Exception):
    """
    Exception raised when the format of the map data is invalid.
    """

    pass


class Formatter(Protocol):
    """
    Protocol defining the interface for data formatters.
    """

    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
        """
        Formats parsed data into a dictionary.

        Args:
            name: Name or type of the element being formatted.
            data: Main data fields extracted from the input line.
            metadata: Additional metadata fields extracted from the input
                line.
            line: Line number where the data was found.

        Returns:
            A dictionary containing the formatted data.
        """

        pass


class FormatHub:
    """
    Formats hub information extracted from the input map file
    """

    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
        """
        Formats hub data into a dictionary.

        Start and end hubs are assigned the names ``start`` and ``end``,
        respectively. Regular hubs use the name provided in the input data.
        Coordinates and supported metadata are also added to the resulting
        dictionary.

        Args:
            name: Type of hub being formatted, such as ``hub``,
                ``start_hub`` or ``end_hub``.
            data: Main hub data, including its name and coordinates.
            metadata: Additional hub metadata, such as color, zone or
                maximum number of drones.
            line: Line number where the hub was found.

        Returns:
            A dictionary containing the formatted hub information.

        Raises:
            FormatError: If an unknown metadata key is found.
            IndexError: If required hub information is missing.
        """
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
                                      f" unknown key ({k})")

        except IndexError:
            print(f"ERROR (line {line}): missing required info",
                  file=sys.stderr)
            sys.exit(1)
        except FormatError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        return info


class FormatCon:
    """
    Formats connection information extracted from the input map file.
    """

    @staticmethod
    def format(name: str, data: list[str],
               metadata: list[str], line: int) -> dict[str, Any]:
        """
        Formats connection data into a dictionary.

        The connection is split into its two connected zones and its
        supported metadata is added to the resulting dictionary.

        Args:
            name: Name assigned to the connection.
            data: Connection data containing the two connected zones.
            metadata: Additional connection metadata, such as maximum
                link capacity.
            line: Line number where the connection was found.

        Returns:
            A dictionary containing the formatted connection information.

        Raises:
            FormatError: If the zones are not connected using '-' or if
                an unknown metadata key is found.
            IndexError: If required connection information is missing.
        """

        info: dict[str, Any] = {}

        try:
            info['name'] = name
            if "-" not in data[0]:
                raise FormatError(f"ERROR (line {line}):"
                                  " zones should be connected by '-'")
            info['zone_a'], info['zone_b'] = data[0].split('-')
            for i in range(0, len(metadata)):
                k, v = metadata[i].split('=')
                if k == "max_link_capacity":
                    info['max_link_capacity'] = v
                else:
                    raise FormatError(f"ERROR (line {line}):"
                                      f" unknown key ({k})")
        except IndexError:
            print(f"ERROR (line {line}): missing required info",
                  file=sys.stderr)
            sys.exit(1)
        except FormatError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        return info


class ParseMap:
    """
    Parses and validates the input map file.

    The parser reads the input file specified through the command line,
    validates its structure, processes each line according to its type,
    and creates the corresponding hubs and connections.
    """

    def __init__(self) -> None:
        """
        Initializes the map parser.

        Initializes the number of drones, the number of connections, the
        input file contents and the current line number before starting
        the parsing and validation process.
        """

        self.nb_drones: int = 0
        self.nb_con: int = 0
        self.content: list[str]
        self.line: int = 1
        self.read_and_validate()

    def read_and_validate(self) -> None:
        """
        Reads the input file and validates its structure.

        Checks that exactly one input file is provided through the command
        line, reads its contents, validates the required 'nb_drones' line,
        and processes each non-empty, non-comment line.

        Raises:
            OSError: If the input file cannot be read.
        """

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
        """
        Processes a single line of parsed map data.

        Identifies the type of element represented by the line, extracts
        metadata when present, formats the information, and creates the
        corresponding 'Hub' or 'Connection' object.

        Args:
            key: Element type specified at the beginning of the line.
                Supported values include 'nb_drones', 'hub',
                'start_hub', 'end_hub' and 'connection'.
            info: Information associated with the element, including its
                main data and optional metadata.

        Raises:
            ValidationError: If the formatted data does not satisfy the
                validation rules defined by the corresponding Pydantic
                model.
            ValueError: If the number of drones is not a positive integer.
        """

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
                      f" undefined key ({key})", file=sys.stderr)
                sys.exit(1)

        except ValidationError as e:
            print(f"ERROR (line {self.line}):",
                  e.errors()[0]["msg"], file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
