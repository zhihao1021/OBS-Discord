from utils import Json

from copy import deepcopy
from datetime import timedelta, timezone
from logging import getLevelName
from os import makedirs
from os.path import abspath, isdir
from pydantic import BaseModel, Field, validator
from typing import Union


def __recursion_update(old_dict: dict, new_dict: dict) -> dict:
    """
    遞迴更新字典。
    """
    for key, value in new_dict.items():
        if type(value) == dict:
            old_value = old_dict.get(key, {})
            old_value = __recursion_update(old_value, value)
            old_dict[key] = old_value
        else:
            old_dict[key] = value
    return old_dict


def path_validator(path: str):
    if not isdir(path := abspath(path)):
        makedirs(path)
    return path

# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET


class LoggingConfig(BaseModel):
    stream_level: Union[int, str] = Field(20, alias="stream-level")
    file_level: Union[int, str] = Field(20, alias="file-level")
    backup_count: int = Field(3, alias="backup-count", ge=0)
    file_name: str = Field(alias="file-name")
    dir_path: str = Field("logs", alias="dir-path")

    @validator("stream_level", "file_level")
    def level_name_validator(cls, value):
        if value if type(value) == int else getLevelName(value) in range(0, 51, 10):
            return value
        raise ValueError(f"Illegal level name: \"{value}\"")

    @validator("dir_path")
    def path_validator(cls, value):
        return path_validator(value)

    class Config:
        extra = "ignore"


class DiscordConfig(BaseModel):
    token: str
    prefixs: list[str]
    channel: int


class OBSConfig(BaseModel):
    host: str
    port: int
    passwd: str = ""


EXAMPLE_CONFIG: dict[str, dict] = {
    "discord": {
        "token": "",
        "prefixs": ["$"],
        "channel": 0
    },
    "obs": {
        "host": "localhost",
        "port": 4455,
        "passwd": ""
    },
    "logging": {
        "main": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 3,
            "file-name": "main",
            "dir-path": "logs"
        },
        "discord": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 3,
            "file-name": "myself",
            "dir-path": "logs"
        },
        "obs": {
            "stream-level": "INFO",
            "file-level": "INFO",
            "backup-count": 3,
            "file-name": "obs",
            "dir-path": "logs"
        }
    },
    "timezone": 8
}


CONFIG: dict[str, Union[dict, str, int]] = ...

# 更新資料
try:
    config = Json.load_nowait("config.json")
except:
    config = deepcopy(EXAMPLE_CONFIG)
CONFIG = __recursion_update(EXAMPLE_CONFIG, config)
Json.dump_nowait("config.json", CONFIG)

TIMEZONE: timezone = timezone(timedelta(hours=CONFIG["timezone"]))
DISCORD_CONFIG = DiscordConfig(**CONFIG["discord"])
OBS_CONFIG = OBSConfig(**CONFIG["obs"])
LOGGING_CONFIG: dict[str, LoggingConfig] = {
    key: LoggingConfig(**value)
    for key, value in CONFIG["logging"].items()
}
MAX_LOGGER_NAME = max(*map(len, LOGGING_CONFIG.keys()))
