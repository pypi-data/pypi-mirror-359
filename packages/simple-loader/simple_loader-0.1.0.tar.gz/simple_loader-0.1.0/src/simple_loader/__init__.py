import os
import json
import yaml
from dotenv import load_dotenv

_env_data = {}
_json_data = {}
_yaml_data = {}

def load(envFile: str=None, jsonFile: str=None, yamlFile: str=None) -> None:
    global _env_data, _json_data, _yaml_data

    if envFile:
        load_dotenv(envFile)
        _env_data = dict(os.environ)

    if jsonFile:
        with open(jsonFile, "r", encoding="utf-8") as f:
            _json_data = json.load(f)

    if yamlFile:
        with open(yamlFile, "r", encoding="utf-8") as f:
            _yaml_data = yaml.safe_load(f)

def get_env(key, fallback=None):
    return _env_data.get(key, fallback)

def get_json():
    return _json_data

def get_yaml():
    return _yaml_data
