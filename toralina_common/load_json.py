import json
from pathlib import Path
JSON_FILE = 'network.json'

ROOT_DIR = Path(__file__)


def full_path(file: str) -> Path:
    return ROOT_DIR.parent.joinpath(file)


def load_config() -> tuple:
    try:
        with open(full_path(JSON_FILE)) as conf:
            data = json.loads(conf.read())

        ds = data.get('ds')
        return ds["ip"], ds["port"]

    except FileNotFoundError as file_error:
        print(f'[!] {file_error} doesnt exist!')
