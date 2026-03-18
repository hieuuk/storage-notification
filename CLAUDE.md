# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool that monitors folder sizes and drive usage, sends notifications (Discord or Telegram) when thresholds are exceeded, and optionally auto-cleans old/large files. Runs as a long-lived polling process.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the monitor (requires config.json)
python monitor.py

# Edit configuration interactively
python config_editor.py
```

## Architecture

- **monitor.py** — Main entry point. Polls configured folders and drives on an interval (`check_interval_seconds`). Folder checks compute size via `os.walk` and trigger cleanup if configured. Drive checks use `shutil.disk_usage` against a percentage threshold. All alerts route through `notifiers.notify()`.
- **notifiers.py** — Notification dispatch. Prepends `computer_name` to messages, then routes to Discord (webhook POST) or Telegram (bot API POST) based on `config.notification.method`.
- **cleanup.py** — Auto-cleanup module. `cleanup_folder()` deletes files matching glob patterns that are too old (`max_age_days`) or too large (`max_file_size`), then removes empty directories bottom-up. Called by `monitor.py` when a folder exceeds its limit and has cleanup enabled.
- **config_editor.py** — Interactive CLI for editing `config.json` (folders, drives, notification settings, interval, computer name).
- **setup_task.bat** — Creates a Windows scheduled task (`StorageMonitor`) to run `monitor.py` on logon via `schtasks`.

## Configuration

Runtime config lives in `config.json` (gitignored — contains secrets). Copy `config.example.json` to `config.json` to get started. Size limits use human-readable strings like `500MB`, `1.5GB`, `100KB`. Drive thresholds use percentage values (e.g. `80` for 80%).

## Key Patterns

- Paths in config support `~` and environment variable expansion via `cleanup.expand_path()`.
- The monitor loop is infinite (`while True` + `time.sleep`); it reloads config only at startup.
