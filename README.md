# Storage Notification

A Python tool that monitors folder sizes and drive usage, sends notifications via Discord or Telegram when thresholds are exceeded, and optionally auto-cleans old or large files.

## Features

- Monitor folder sizes against configurable limits (e.g. `500MB`, `1.5GB`)
- Monitor drive usage against percentage thresholds (e.g. 80%)
- Send alerts via **Discord webhook** or **Telegram bot**
- Auto-cleanup: delete files by age, size, or glob pattern when a folder exceeds its limit
- Interactive config editor
- Windows startup support via scheduled task

## Installation

### Prerequisites

- Python 3.10+

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/storage-notification.git
   cd storage-notification
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create your configuration**

   ```bash
   cp config.example.json config.json
   ```

   Edit `config.json` directly, or use the interactive editor:

   ```bash
   python config_editor.py
   ```

4. **Configure notifications**

   Set up either Discord or Telegram in your `config.json`:

   - **Discord**: Create a [webhook](https://support.discord.com/hc/en-us/articles/228383668) in your channel settings and paste the URL into `notification.discord.webhook_url`.
   - **Telegram**: Create a bot via [@BotFather](https://t.me/BotFather), then set `notification.telegram.bot_token` and `notification.telegram.chat_id`.

   Set `notification.method` to `"discord"` or `"telegram"`.

## Usage

### Run the monitor

```bash
python monitor.py
```

The monitor polls on a configurable interval (default: 300 seconds) and sends notifications when:
- A folder exceeds its size limit
- A drive exceeds its usage threshold percentage

### Configuration options

| Field | Description |
|---|---|
| `computer_name` | Identifier prepended to notification messages |
| `check_interval_seconds` | Polling interval in seconds (default: 300) |
| `folders` | List of folders to monitor with `path`, `name`, `size_limit`, and optional `cleanup` |
| `drives` | List of drives to monitor with `path`, `name`, and `threshold_percent` |
| `notification` | Notification method and credentials |

### Auto-cleanup

Add a `cleanup` block to any folder entry to automatically delete files when the folder exceeds its limit:

```json
{
    "path": "/var/log/myapp",
    "name": "App Logs",
    "size_limit": "1GB",
    "cleanup": {
        "enabled": true,
        "max_age_days": 30,
        "max_file_size": "100MB",
        "patterns": ["*.log", "*.jsonl"]
    }
}
```

- `max_age_days` — Delete files older than this (0 to disable)
- `max_file_size` — Delete files larger than this (omit to disable)
- `patterns` — Glob patterns to match (empty list = all files)

### Run on Windows startup

Run `setup_task.bat` as Administrator to create a scheduled task that starts the monitor on logon. Edit the paths in the script to match your Python and project locations.

## License

[GPL-3.0](LICENSE)
