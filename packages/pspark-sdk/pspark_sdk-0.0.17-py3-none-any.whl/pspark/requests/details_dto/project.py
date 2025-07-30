from dataclasses import dataclass
from typing import Optional

from ..abstract_request import AbstractRequest
from ...validators import validate_url


@dataclass
class Project(AbstractRequest):
    url: Optional[str] = None

    def __post_init__(self):
        validate_url(self.url)
