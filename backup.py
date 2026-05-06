import os
import difflib
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


def get_last_backup(name):
    if not os.path.exists(BACKUP_DIR):
        return None
    files = sorted(f for f in os.listdir(BACKUP_DIR) if f.startswith(name + "_"))
    if not files:
        return None
    with open(f"{BACKUP_DIR}/{files[-1]}") as f:
        return f.read()


def diff_configs(name, old, new):
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="previous", tofile="current"))
    if diff:
        print(f"  [{name}] config changed:")
        # cap output so it doesn't flood the terminal on big changes
        for line in diff[:60]:
            print("   " + line, end="")
        if len(diff) > 60:
            print(f"\n   ... and {len(diff) - 60} more lines")
    else:
        print(f"  [{name}] no changes since last backup")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="devices.yaml")
    args = parser.parse_args()

    devices = load_devices(args.config)

    for device in devices:
        name = device["name"]
        print(f"connecting to {name} ({device['host']})...")
        try:
            last = get_last_backup(name)
            config = pull_config(device)
            saved = save_config(name, config)
            print(f"  saved -> {saved}")
            if last:
                diff_configs(name, last, config)
        except Exception as e:
            print(f"  failed: {e}")


if __name__ == "__main__":
    main()
