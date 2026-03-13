import requests


def send_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    """Send a notification via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    resp = requests.post(url, json=payload, timeout=10)
    return resp.ok


def send_discord(webhook_url: str, message: str) -> bool:
    """Send a notification via Discord webhook."""
    payload = {"content": message}
    resp = requests.post(webhook_url, json=payload, timeout=10)
    return resp.ok


def notify(config: dict, message: str) -> bool:
    """Send notification using the configured method."""
    computer_name = config.get("computer_name", "")
    if computer_name:
        message = f"[{computer_name}] {message}"
    method = config["notification"]["method"]
    if method == "telegram":
        tg = config["notification"]["telegram"]
        return send_telegram(tg["bot_token"], tg["chat_id"], message)
    elif method == "discord":
        dc = config["notification"]["discord"]
        return send_discord(dc["webhook_url"], message)
    else:
        print(f"Unknown notification method: {method}")
        return False
