import os
import yaml
import argparse
from datetime import datetime
from netmiko import ConnectHandler

BACKUP_DIR = "backups"


def load_devices(path):
    with open(path) as f:
        return yaml.safe_load(f)["devices"]


def pull_config(device):
    conn = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
    )
    config = conn.send_command("show running-config")
    conn.disconnect()
    return config


def save_config(name, config):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{BACKUP_DIR}/{name}_{ts}.txt"
    with open(path, "w") as f:
        f.write(config)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="devices.yaml")
    args = parser.parse_args()

    devices = load_devices(args.config)

    for device in devices:
        name = device["name"]
        print(f"connecting to {name} ({device['host']})...")
        try:
            config = pull_config(device)
            saved = save_config(name, config)
            print(f"  saved -> {saved}")
        except Exception as e:
            print(f"  failed: {e}")


if __name__ == "__main__":
    main()
