import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    print("Configuration saved.")


def list_folders(config: dict) -> None:
    folders = config["folders"]
    if not folders:
        print("\nNo folders configured.\n")
        return
    print(f"\n{'#':<4} {'Name':<25} {'Size Limit':<12} Path")
    print("-" * 80)
    for i, folder in enumerate(folders):
        name = folder.get("name", "(unnamed)")
        print(f"{i:<4} {name:<25} {folder['size_limit']:<12} {folder['path']}")
    print()


def add_folder(config: dict) -> None:
    path = input("Folder path: ").strip()
    if not path:
        print("Cancelled.")
        return
    if not os.path.isdir(path):
        print(f"Warning: '{path}' does not exist or is not a directory.")
        confirm = input("Add anyway? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return
    name = input("Name (optional, press Enter to skip): ").strip()
    size_limit = input("Size limit (e.g. 500MB, 1GB, 100KB): ").strip()
    if not size_limit:
        print("Size limit is required. Cancelled.")
        return

    folder = {"path": path, "size_limit": size_limit}
    if name:
        folder["name"] = name
    config["folders"].append(folder)
    save_config(config)
    print(f"Added folder: {path}")


def remove_folder(config: dict) -> None:
    list_folders(config)
    if not config["folders"]:
        return
    try:
        idx = int(input("Enter folder number to remove: ").strip())
        removed = config["folders"].pop(idx)
        save_config(config)
        print(f"Removed: {removed['path']}")
    except (ValueError, IndexError):
        print("Invalid selection.")


def edit_folder(config: dict) -> None:
    list_folders(config)
    if not config["folders"]:
        return
    try:
        idx = int(input("Enter folder number to edit: ").strip())
        folder = config["folders"][idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    print(f"\nEditing folder #{idx}:")
    print(f"  Path: {folder['path']}")
    print(f"  Name: {folder.get('name', '(none)')}")
    print(f"  Size limit: {folder['size_limit']}")
    print("(Press Enter to keep current value)\n")

    new_path = input(f"Path [{folder['path']}]: ").strip()
    if new_path:
        folder["path"] = new_path

    current_name = folder.get("name", "")
    new_name = input(f"Name [{current_name}]: ").strip()
    if new_name:
        folder["name"] = new_name

    new_limit = input(f"Size limit [{folder['size_limit']}]: ").strip()
    if new_limit:
        folder["size_limit"] = new_limit

    save_config(config)
    print("Folder updated.")


def set_notification(config: dict) -> None:
    current = config["notification"]["method"]
    print(f"\nCurrent method: {current}")
    print("1) Discord")
    print("2) Telegram")
    choice = input("Select method (1/2): ").strip()

    if choice == "1":
        config["notification"]["method"] = "discord"
        url = input(
            f"Discord webhook URL [{config['notification']['discord']['webhook_url'] or '(not set)'}]: "
        ).strip()
        if url:
            config["notification"]["discord"]["webhook_url"] = url
    elif choice == "2":
        config["notification"]["method"] = "telegram"
        token = input(
            f"Bot token [{config['notification']['telegram']['bot_token'] or '(not set)'}]: "
        ).strip()
        if token:
            config["notification"]["telegram"]["bot_token"] = token
        chat_id = input(
            f"Chat ID [{config['notification']['telegram']['chat_id'] or '(not set)'}]: "
        ).strip()
        if chat_id:
            config["notification"]["telegram"]["chat_id"] = chat_id
    else:
        print("Invalid choice.")
        return

    save_config(config)
    print("Notification settings updated.")


def set_interval(config: dict) -> None:
    current = config.get("check_interval_seconds", 300)
    print(f"\nCurrent check interval: {current} seconds")
    try:
        val = input("New interval in seconds (Enter to keep): ").strip()
        if val:
            config["check_interval_seconds"] = int(val)
            save_config(config)
            print(f"Interval set to {config['check_interval_seconds']} seconds.")
    except ValueError:
        print("Invalid number.")


def show_config(config: dict) -> None:
    print("\n" + json.dumps(config, indent=4) + "\n")


def main() -> None:
    if not os.path.exists(CONFIG_PATH):
        print(f"Config file not found at {CONFIG_PATH}")
        sys.exit(1)

    config = load_config()

    menu = (
        "\n=== Storage Notification Config Editor ===\n"
        "1) List folders\n"
        "2) Add folder\n"
        "3) Edit folder\n"
        "4) Remove folder\n"
        "5) Notification settings\n"
        "6) Check interval\n"
        "7) Show full config\n"
        "0) Exit\n"
    )

    while True:
        print(menu)
        choice = input("Choice: ").strip()
        if choice == "1":
            list_folders(config)
        elif choice == "2":
            add_folder(config)
        elif choice == "3":
            edit_folder(config)
        elif choice == "4":
            remove_folder(config)
        elif choice == "5":
            set_notification(config)
        elif choice == "6":
            set_interval(config)
        elif choice == "7":
            show_config(config)
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
