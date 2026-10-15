from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_data_root(config):
    data_root = Path(config["data"]["root"])

    if not data_root.is_absolute():
        data_root = (PROJECT_ROOT / data_root).resolve()

    return data_root


if __name__ == "__main__":
    config = load_config()
    data_root = get_data_root(config)

    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("DATA_ROOT:", data_root)
    print("Existe:", data_root.exists())