import os
import json
import copy

CONFIG_PATH = os.path.expanduser('~/.config/neurokrunner.json')
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

DEFAULT_CONFIG = {
    "auto_sub": {
        "neuro": False,
        "evil": False,
        "vedal": False,
        "twins": False,
        "collab": False,
        "all": False
    },
    "icons": {
        "schedule": os.path.join(ASSETS_DIR, 'neuro.png'),
        "vedal": os.path.join(ASSETS_DIR, 'vedal.png'),
        "neuro": os.path.join(ASSETS_DIR, 'neuro.png'),
        "evil": os.path.join(ASSETS_DIR, 'evil.png'),
        "twins": os.path.join(ASSETS_DIR, 'twins.png')
    },
    "behavior": {
        "direct_to_twitch": False
    },
    "ignored_streams": []
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, 'r') as f:
            user_config = json.load(f)
            # Use deepcopy so nested objects don't share memory references
            config = copy.deepcopy(DEFAULT_CONFIG)
            for k, v in user_config.items():
                if isinstance(v, dict) and k in config:
                    config[k].update(v)
                else:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")
