from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Any, ClassVar
import sys
import abc
from enum import Enum
import pygame


class FormatError(Exception):
    pass


class Zone(str, Enum):
    normal = "normal"
    restricted = "restricted"
    priority = "priority"
    blocked = "blocked"


class Processor(abc.ABC):
    map: ClassVar[dict[str,
                       dict[str,
                            dict[str, Any]]]] = {'hub': {}, 'connection': {}}

    @abc.abstractmethod
    def ingest(self) -> None:
        pass

    def check_map(self) -> None:
        if "start" not in self.map['hub']:
            raise FormatError("ERROR: no start point")
        if "end" not in self.map['hub']:
            raise FormatError("ERROR: no end point")
        for con in self.map['connection'].values():
            if (
                con['zone_a'] not in self.map['hub']
                or con['zone_b'] not in self.map['hub']
            ):
                raise FormatError("ERROR: trying to connect unknown hub")


class Hub(BaseModel, Processor):
    name: str
    coord: tuple[int, int]
    zone: Optional[Zone] = Field(default=Zone.normal)
    color: Optional[str] = Field(default="grey")
    max_drones: Optional[int] = Field(default=1, ge=0)
    nb_drones: int = Field(ge=0)

    def __init__(self, info: dict[str, Any]) -> None:
        super().__init__(**info)
        self.ingest()

    @field_validator('coord', mode='before')
    @classmethod
    def coord_to_tuple(cls, value: str) -> tuple[int, int]:
        try:
            return (int(value[0]), int(value[1]))
        except ValueError:
            print("ERROR: coords must be integers", file=sys.stderr)
            sys.exit(1)

    @model_validator(mode='after')
    def validate_model(self) -> 'Hub':
        if '-' in self.name:
            raise ValueError("ERROR: Hub's name must not contain '-'")
        if not pygame.Color(self.color):
            raise ValueError("ERROR: Hub's color must be a"
                             " single valid string with no ' '")
        if self.name in self.map['hub']:
            raise ValueError("ERROR: Hub's name must be unique")
        if self.name == "start" or self.name == "end":
            self.max_drones = self.nb_drones
        return self

    def ingest(self) -> None:
        data = {self.name: self.model_dump(mode='json',
                                           exclude={'name', 'nb_drones'})}
        self.map['hub'].update(data)


class Connection(BaseModel, Processor):
    name: str
    zone_a: str
    zone_b: str
    max_link_capacity: Optional[int] = Field(default=1, ge=0)

    def __init__(self, info: dict[str, Any]) -> None:
        super().__init__(**info)
        self.ingest()

    @model_validator(mode='after')
    def validate_model(self) -> 'Connection':
        for con in self.map['connection'].values():
            if ((self.zone_a == con['zone_a']
                 and self.zone_b == con['zone_b'])
                or (self.zone_a == con['zone_b']
                    and self.zone_b == con['zone_a'])):
                raise ValueError("ERROR: connections must only appear once")
        return self

    def ingest(self) -> None:
        data = {self.name: self.model_dump(exclude={'name'})}
        self.map['connection'].update(data)


class CheckMap(Processor):
    def ingest(self) -> None:
        pass
