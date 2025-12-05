from pydantic import BaseModel


class SoupState(BaseModel):
    running: bool = False
    current_soup: dict = None

    def __init__(self, **data):
        super().__init__(**data)
