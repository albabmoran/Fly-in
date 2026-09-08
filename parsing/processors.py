from pydantic import (BaseModel, Field, model_validator,
                      field_validator, ValidationInfo, ConfigDict)
from typing import Optional, Any, ClassVar
from enum import Enum
import pygame
import json
import sys
import abc


class FormatError(Exception):
    """
    Exception raised when the map format is invalid.
    """

    pass


class Zone(str, Enum):
    """
    Defines the possible zones for a hub.
    """

    normal = "normal"
    restricted = "restricted"
    priority = "priority"
    blocked = "blocked"


class Processor(abc.ABC):
    """
    Base class for processing and validating map data.

    Provides the shared map storage and common operations used by the
    different map processors, such as validating the map structure and
    saving the processed data to a JSON file.
    """

    map: ClassVar[dict[str, Any]] = {'nb_drones': 0,
                                     'hub': {}, 'connection': {}}

    @abc.abstractmethod
    def ingest(self) -> None:
        """
        Adds the processed object to the shared map.

        This method must be implemented by subclasses to define how their
        processed data is stored in the map.
        """

        pass

    def check_map(self) -> None:
        """
        Validates the basic structure and references of the map.

        Checks that the map contains both a start and an end hub and that
        every connection references hubs that exist in the map.

        Raises:
            FormatError: If the map has no start hub, no end hub, or a
                connection references an unknown hub.
        """

        if "start" not in self.map['hub']:
            raise FormatError("ERROR: no start point")
        if "end" not in self.map['hub']:
            raise FormatError("ERROR: no end point")
        for con in self.map['connection'].values():
            if (
                con['zone_a'] not in self.map['hub']
                or con['zone_b'] not in self.map['hub']
            ):
                raise FormatError("ERROR: trying to connect unknown hub"
                                  f" ({con['zone_a']}, {con['zone_b']})")

    def convert_to_json(self) -> None:
        """
        Saves the processed map to a JSON file.

        Writes the shared map data to ``data/map.json`` using an indented
        JSON format.
        """

        with open("data/map.json", 'w', encoding='utf-8') as f:
            json.dump(self.map, f, indent=4)


class Hub(BaseModel, Processor):
    """
    Represents and validates a hub in the map.

    A hub contains its name, coordinates, zone, color, drone capacity and
    the number of drones in the map. Once validated, the hub is added to
    the shared map.
    """

    model_config = ConfigDict(extra="allow")

    name: str
    coord: tuple[int, int]
    zone: Optional[Zone] = Field(default=Zone.normal)
    color: str = Field(default="grey")
    max_drones: Optional[int] = Field(default=1, ge=0)
    nb_drones: int = Field(ge=0)
    line: int = Field(ge=0)

    def __init__(self, info: dict[str, Any],
                 *args: Any, **kwargs: Any) -> None:
        """
        Initializes and validates a hub from parsed input data.

        The provided information is validated using Pydantic, with the
        input line number passed as validation context for error reporting.
        Once validation succeeds, the hub is added to the shared map.

        Args:
            info: Dictionary containing the hub information to validate.
            *args: Additional positional arguments accepted by the
                initialization process.
            **kwargs: Additional keyword arguments, including the line
                number associated with the hub.
        """

        line = kwargs.get('line', 'Unknown')
        self.__pydantic_validator__.validate_python(
            {**info, **kwargs},
            context={"line": line},
            self_instance=self
        )
        self.ingest()

    @field_validator('coord', mode='before')
    @classmethod
    def coord_to_tuple(cls, value: list[str],
                       info: ValidationInfo) -> tuple[int, int]:
        """
        Converts hub coordinates from strings to integers.

        The coordinates are received as strings during parsing and are
        converted into a tuple of integers for the Pydantic model.

        Args:
            value: List containing the X and Y coordinate values as strings.
            info: Pydantic validation information containing the current
                validation context.

        Returns:
            A tuple containing the X and Y coordinates as integers.

        Raises:
            ValueError: If either coordinate cannot be converted to an
                integer.
        """

        context = info.context or {}
        line = context.get('line', 'unknown')
        try:
            return (int(value[0]), int(value[1]))
        except ValueError:
            print(f"ERROR (line {line}):"
                  " coords must be integers", file=sys.stderr)
            sys.exit(1)

    @model_validator(mode='after')
    def validate_model(self) -> 'Hub':
        """
        Validates the constraints specific to a hub.

        Checks that the hub name does not contain a hyphen, that its color
        is valid, and that its name is unique within the map. Start and end
        hubs automatically receive the total number of drones as their
        maximum capacity.

        Returns:
            The validated 'Hub' instance.

        Raises:
            ValueError: If the hub name contains a hyphen, the color is
                invalid, or the hub name is already in use.
        """

        if '-' in self.name:
            raise ValueError(f"ERROR (line {self.line}):"
                             " Hub's name must not contain '-'")
        if self.color != 'rainbow':
            if not pygame.Color(self.color):
                raise ValueError(f"ERROR (line {self.line}):"
                                 " Hub's color must be a"
                                 " single valid string with no ' '")
        if self.name in self.map['hub']:
            raise ValueError(f"ERROR (line {self.line}):"
                             " Hub's name must be unique")
        if self.name == "start" or self.name == "end":
            self.max_drones = self.nb_drones
        return self

    def ingest(self) -> None:
        """
        Adds the validated hub to the shared map.

        Stores the hub data in the 'hub' section of the map and updates
        the total number of drones stored in the map.
        """

        data = {self.name: self.model_dump(mode='json',
                                           exclude={'name', 'nb_drones'})}
        self.map['hub'].update(data)
        self.map['nb_drones'] = self.nb_drones


class Connection(BaseModel, Processor):
    """
    Validates a connection between two hubs.

    A connection defines the two hubs it links and its maximum link
    capacity. Connections are validated to ensure that the same connection
    does not appear more than once, regardless of its direction.
    """

    name: str
    zone_a: str
    zone_b: str
    max_link_capacity: Optional[int] = Field(default=1, ge=0)
    line: int = Field(ge=0)

    def __init__(self, info: dict[str, Any]) -> None:
        """
        Initializes and validates a connection.

        Args:
            info: Dictionary containing the connection information to
                validate.
        """

        super().__init__(**info)
        self.ingest()

    @model_validator(mode='after')
    def validate_model(self) -> 'Connection':
        """
        Validates that the connection is unique in the map.

        Checks both possible directions of the connection. A connection
        between A and B is considered identical to a connection between
        B and A.

        Returns:
            The validated 'Connection' instance.

        Raises:
            ValueError: If the same connection already exists in the map.
        """

        for con in self.map['connection'].values():
            if ((self.zone_a == con['zone_a']
                 and self.zone_b == con['zone_b'])
                or (self.zone_a == con['zone_b']
                    and self.zone_b == con['zone_a'])):
                raise ValueError(f"ERROR (line {self.line}):"
                                 " connections must only appear once")
        return self

    def ingest(self) -> None:
        """
        Adds the validated connection to the shared map.

        Stores the connection information in the 'connection' section
        of the shared map.
        """

        data = {self.name: self.model_dump(exclude={'name'})}
        self.map['connection'].update(data)


class SaveMap(Processor):
    """
    Validates and saves the complete processed map.

    This processor checks that the map contains the required hubs and valid
    connection references before writing the resulting data to
    'data/map.json'.
    """

    def __init__(self) -> None:
        """
        Validates the map and saves it to the JSON output file.
        """

        self.check_map()
        self.convert_to_json()

    def ingest(self) -> None:
        """
        Provides the required implementation for 'Processor'.

        'SaveMap' does not ingest individual objects because its purpose
        is to validate and save the complete map.
        """

        pass
