from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from enum import Enum


class Zone(Enum):
	normal = "normal"
	restricted = "restricted"
	priority = "priority"
	blocked = "blocked"


class ValidateHub(BaseModel):
	name: str
	c_x: int
	c_y: int
	zone: Zone = Field(default=Zone.normal)
	color: str
	max_drones: int = Field(ge=0)
