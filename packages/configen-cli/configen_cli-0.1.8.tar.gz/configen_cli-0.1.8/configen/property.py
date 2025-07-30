from platformdirs import user_data_dir
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path
import tomllib
import uuid
import os

load_dotenv()


def _get_property(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Missing required env variable: {name}")
    return value


def _get_app_version():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
    return data["tool"]["poetry"]["version"]


def _get_host_id() -> str:
    db_dir = Path(user_data_dir(CONFIGEN_APP_NAME))
    db_dir.mkdir(parents=True, exist_ok=True)
    id_file = db_dir / "machine.id"

    if id_file.exists():
        return id_file.read_text().strip()

    new_id = str(uuid.uuid4())
    id_file.write_text(new_id)
    return new_id


CONFIGEN_API_KEY = _get_property("CONFIGEN_API_KEY")
CONFIGEN_API_URL = _get_property("CONFIGEN_API_URL")
CONFIGEN_APP_NAME = "configen"
CONFIGEN_APP_VERSION = _get_app_version()

HOST_ID = _get_host_id()

CLI_INPUT_USR_ASK = "USR_ASK"
CLI_INPUT_USR_ANSWER = "USR_ANSWER"
CLI_INPUT_CMD_ERROR = "CMD_ERROR"
CLI_INPUT_CMD_OUTPUT = "CMD_OUTPUT"
