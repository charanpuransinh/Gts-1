import logging


class NotificationManager:
    """Multi-Channel Alert System: Telegram Bot, Webhook & Local Logger"""

    def __init__(self, telegram_token: str = "", telegram_chat_id: str = ""):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("GTS_Alerts")

    def send_log_alert(self, title: str, message: str, level: str = "INFO"):
        alert_msg = f"[{title}] {message}"
        if level.upper() == "WARNING":
            self.logger.warning(alert_msg)
        elif level.upper() == "CRITICAL":
            self.logger.critical(alert_msg)
        else:
            self.logger.info(alert_msg)

    def trigger_telegram_alert(self, title: str, message: str) -> bool:
        """Placeholder for Real-Time Telegram Push Alert"""
        full_text = f"🚨 *{title}* 🚨\n{message}"
        if not self.telegram_token or not self.telegram_chat_id:
            self.send_log_alert(title, f"(Simulated Telegram Push): {message}")
            return False
        return True
