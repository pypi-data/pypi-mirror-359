from pydantic import BaseModel


class Resource(BaseModel):

    id: int | None = None


class Facility(Resource):

    name: str
    acronym: str
    description: str
    address: str
    website: str
    country: str
    figure: str = ""
    members: list[str] = []


class AccessCall(Resource):

    title: str
    description: str
    status: str
    closing_date: str
    coordinator: str
    board_chair: str
    board_members: list[str] = []


_TYPE_TO_PATH = {"Facility": "facilities", "AccessCall": "access_calls"}

_PATH_TO_TYPE = {"facilities": Facility, "access_calls": AccessCall}


def get_path_from_item(resource: Resource) -> str:
    return _TYPE_TO_PATH[type(resource).__name__]


def get_path_from_type(item_t) -> str:
    return _TYPE_TO_PATH[item_t.__name__]


def get_type(path: str):
    return _PATH_TO_TYPE[path]
