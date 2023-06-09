from dataclasses import asdict, dataclass
from dotenv import dotenv_values
from pathlib import Path


@dataclass
class Config:
    client_id: str
    client_secret: str
    user_agent: str
    ratelimit_seconds: int = 5

    @classmethod
    def from_dotenv(cls, envfile: str | Path):
        kw = dotenv_values(envfile)
        return cls(**kw)  # type: ignore

    def asdict(self) -> dict[str, str]:
        return asdict(self)
