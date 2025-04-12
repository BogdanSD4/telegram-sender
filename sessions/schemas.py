from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionRequest:
    name: str
    phone: str
    password: str
    code_hash: Optional[str] = None
    code: Optional[int] = None


@dataclass
class SessionResponse:
    value: Optional[str] = None
    error: Optional[str] = None



