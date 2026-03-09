# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool that monitors folder sizes and sends notifications (Discord or Telegram) when folders exceed configured size limits. Runs as a long-lived polling process.

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

- **monitor.py** — Main entry point. Polls configured folders on an interval, computes sizes via `os.walk`, and calls `notifiers.notify()` when a folder exceeds its limit.
- **notifiers.py** — Notification dispatch. Routes messages to Discord (webhook) or Telegram (bot API) based on `config.notification.method`.
- **config_editor.py** — Interactive CLI for editing `config.json` (add/edit/remove folders, set notification method and interval).

## Configuration

Runtime config lives in `config.json` (gitignored — contains secrets). Copy `config.example.json` to `config.json` to get started. Size limits use human-readable strings like `500MB`, `1.5GB`, `100KB`.
