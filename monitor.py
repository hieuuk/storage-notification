import json
import os
import shutil
import time
import sys

from notifiers import notify
from cleanup import expand_path, cleanup_folder

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


def check_drives(config: dict) -> None:
    """Check all configured drives and send notifications if usage exceeds threshold."""
    for drive in config.get("drives", []):
        path = expand_path(drive["path"])
        threshold = drive["threshold_percent"]

        try:
            usage = shutil.disk_usage(path)
        except OSError:
            print(f"Warning: cannot access drive: {path}")
            continue

        used_percent = (usage.used / usage.total) * 100

        if used_percent >= threshold:
            message = (
                f"Drive Alert: '{drive.get('name', path)}'\n"
                f"Drive: {path}\n"
                f"Usage: {used_percent:.1f}% "
                f"({format_size(usage.used)} / {format_size(usage.total)})\n"
                f"Threshold: {threshold}%\n"
                f"Free: {format_size(usage.free)}"
            )
            print(f"ALERT: {message}")
            try:
                notify(config, message)
            except Exception as e:
                print(f"Failed to send notification: {e}")
        else:
            print(
                f"OK: '{drive.get('name', path)}' - "
                f"{used_percent:.1f}% used ({format_size(usage.free)} free)"
            )


def run_cleanup(folder: dict, path: str, current_size: int, config: dict) -> None:
    """Run auto-cleanup for a folder if configured."""
    cleanup_cfg = folder.get("cleanup")
    if not cleanup_cfg or not cleanup_cfg.get("enabled"):
        return

    max_age = cleanup_cfg.get("max_age_days", 0)
    max_file_size = parse_size(cleanup_cfg["max_file_size"]) if cleanup_cfg.get("max_file_size") else 0
    patterns = cleanup_cfg.get("patterns", [])

    reasons = []
    if max_age > 0:
        reasons.append(f"older than {max_age} days")
    if max_file_size > 0:
        reasons.append(f"larger than {format_size(max_file_size)}")
    print(f"Running cleanup on '{path}' ({' or '.join(reasons)})...")
    files_deleted, bytes_freed = cleanup_folder(path, max_age, patterns, max_file_size)

    if files_deleted > 0:
        message = (
            f"Cleanup Complete: '{folder.get('name', path)}'\n"
            f"Path: {path}\n"
            f"Deleted: {files_deleted} file(s)\n"
            f"Freed: {format_size(bytes_freed)}\n"
            f"Was: {format_size(current_size)} → Now: {format_size(current_size - bytes_freed)}"
        )
        print(message)
        try:
            notify(config, message)
        except Exception as e:
            print(f"Failed to send cleanup notification: {e}")
    else:
        print(f"Cleanup: no files older than {max_age} days to remove.")


def check_folders(config: dict) -> None:
    """Check all configured folders and send notifications if over limit."""
    for folder in config["folders"]:
        path = expand_path(folder["path"])
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

            run_cleanup(folder, path, current_size, config)
        else:
            print(
                f"OK: '{folder.get('name', path)}' - "
                f"{format_size(current_size)} / {folder['size_limit']}"
            )


def main() -> None:
    config = load_config()

    drives = config.get("drives", [])
    folders = config.get("folders", [])

    if not folders and not drives:
        print("No folders or drives configured. Run config_editor.py to set up.")
        sys.exit(1)

    interval = config.get("check_interval_seconds", 300)
    computer_name = config.get("computer_name", "")
    print(f"Storage monitor started. Checking every {interval} seconds.")
    if computer_name:
        print(f"Computer: {computer_name}")
    print(f"Monitoring {len(drives)} drive(s) and {len(folders)} folder(s).")

    while True:
        check_drives(config)
        check_folders(config)
        time.sleep(interval)


if __name__ == "__main__":
    main()
