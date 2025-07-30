from pathlib import Path

import toml

DEFAULT_CONFIG = {
    "default_path": str(Path.cwd()),  # defaults to current working directory
    "ignored_smells": [],
    "output_format": "text",  # default CLI output (not JSON)
    "short_response": False,  # default short response mode
}

CONFIG_FILE_NAMES = [".goblinrc", "goblin.toml"]

def load_config():
    # Search order: project dir (all names), then home dir (.goblinrc)
    config_paths = [Path.cwd() / name for name in CONFIG_FILE_NAMES]
    config_paths.append(Path.home() / ".goblinrc")

    config_data = {}
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r") as file:
                    config_data = toml.load(file)
                break  # Use the first found config
            except Exception as e:
                print(f"⚠️ Failed to load config from {config_path}: {e}")

    return {**DEFAULT_CONFIG, **config_data}
