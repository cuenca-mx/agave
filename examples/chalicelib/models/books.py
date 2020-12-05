from dataclasses import dataclass
from typing import Dict


@dataclass
class Book:
    name: str
    author: str

    def to_dict(self) -> Dict:
        return dict(name=self.name, author=self.author)
