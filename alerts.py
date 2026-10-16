"""Telegram delivery with response validation and no credential logging."""
import requests
import config

def send_telegram_alert(message, image_path=None):
    if not config.ALERTS_ENABLED:
        return False, "alerts disabled by configuration"
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return False, "Telegram credentials missing; set them in .env"
    base = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"
    try:
        if image_path:
            with open(image_path, "rb") as photo:
                response = requests.post(
                    f"{base}/sendPhoto",
                    data={"chat_id": config.TELEGRAM_CHAT_ID, "caption": message[:1024]},
                    files={"photo": photo},
                    timeout=25,
                )
        else:
            response = requests.post(
                f"{base}/sendMessage",
                data={"chat_id": config.TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": True},
                timeout=20,
            )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            return False, "Telegram API returned ok=false"
        return True, "sent"
    except (requests.RequestException, ValueError, OSError) as exc:
        # Avoid printing token-bearing URL or secrets.
        return False, f"Telegram send failed: {type(exc).__name__}"
