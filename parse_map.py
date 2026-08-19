from pydantic import BaseModel, Field, ValidationError


class VaidateMap(BaseModel):
	nb_drones: int = Field(ge = 0)
	start_hub: 