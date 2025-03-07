from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field

__all__ = [
    "ApiMode",
    "QueueMode",
    "StorageMode",
    "Settings",
]


class ApiMode(str, Enum):
    GUARDIAN = "guardian"
    MEDIATOR = "mediator"


class QueueMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class StorageMode(str, Enum):
    LOCAL_STORAGE = "local_storage"
    MONGO = "mongo"


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    API_MODE: ApiMode = ApiMode.MEDIATOR
    QUEUE_MODE: QueueMode = QueueMode.LOCAL
    STORAGE_MODE: StorageMode = StorageMode.LOCAL_STORAGE

    API_V1_STR: str = "/api/v1"
    API_V1_1_STR: str = "/api/v1_1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:3001",
            "http://localhost:3002",
            "https://localhost",
            "https://localhost:8080",
            "https://localhost:3001",
            "https://localhost:3002",
        ]
    )
    PROJECT_NAME: str = "electionguard-api-python"
    MONGODB_URI: str = "mongodb://root:example@localhost:27017"
    MESSAGEQUEUE_URI: str = "amqp://guest:guest@localhost:5672"

    AUTH_ALGORITHM = "HS256"
    # JWT secret that matches AUTH_ALGORITHM. Change this to a valid value.
    AUTH_SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTczODY4Mjc5MCwiaWF0IjoxNzM4NjgyNzkwfQ.x7o98H8qkwJVUDNF2WWo1Fp_pD7QG7o8q8X3OKA0pew"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DEFAULT_ADMIN_USERNAME = "default"
    DEFAULT_ADMIN_PASSWORD = "testingpass"
    # this is a default value that will be moving to the environment settings
    # the default value should not be used for production use

    class Config:
        case_sensitive = True
