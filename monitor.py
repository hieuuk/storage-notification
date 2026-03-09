import json
import os
import time
import sys

from notifiers import notify

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_folder_size(path: str) -> int:
    """Return total size of a folder in bytes."""
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for fname in filenames:
            fp = os.path.join(dirpath, fname)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def parse_size(size_str: str) -> int:
    """Parse a human-readable size string (e.g. '500MB', '1.5GB') to bytes."""
    size_str = size_str.strip().upper()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    for suffix, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(suffix):
            number = float(size_str[: -len(suffix)].strip())
            return int(number * multiplier)
    return int(size_str)


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def check_folders(config: dict) -> None:
    """Check all configured folders and send notifications if over limit."""
    for folder in config["folders"]:
        path = folder["path"]
        if not os.path.isdir(path):
            print(f"Warning: folder does not exist: {path}")
            continue

        limit_bytes = parse_size(folder["size_limit"])
        current_size = get_folder_size(path)

        if current_size >= limit_bytes:
            message = (
                f"Storage Alert: '{folder.get('name', path)}'\n"
                f"Path: {path}\n"
                f"Current size: {format_size(current_size)}\n"
                f"Limit: {folder['size_limit']}"
            )
            print(f"ALERT: {message}")
            try:
                notify(config, message)
            except Exception as e:
                print(f"Failed to send notification: {e}")
        else:
            print(
                f"OK: '{folder.get('name', path)}' - "
                f"{format_size(current_size)} / {folder['size_limit']}"
            )


def main() -> None:
    config = load_config()

    if not config["folders"]:
        print("No folders configured. Run config_editor.py to add folders.")
        sys.exit(1)

    interval = config.get("check_interval_seconds", 300)
    print(f"Storage monitor started. Checking every {interval} seconds.")
    print(f"Monitoring {len(config['folders'])} folder(s).")

    while True:
        check_folders(config)
        time.sleep(interval)


if __name__ == "__main__":
    main()
