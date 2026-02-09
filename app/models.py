from dataclasses import dataclass
from typing import Optional

@dataclass
class Record:
    id: Optional[int] = None
    name: str = ""
    value: float = 0.0
    category: str = ""
    description: str = ""