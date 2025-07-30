import sys
import requests

# Вставь сюда свой токен и chat_id
BOT_TOKEN = '7042358990:AAGAjzpE5fTexQPGMZ35YJ7bGp4fRdOXz9A'
TARGET_USERNAME = 'wozol'  # без @

def get_chat_id_by_username(username):
    # Предполагается, что список ID с username заранее сохранён
    # Telegram Bot API не позволяет искать по username напрямую
    # Этот словарь можно заполнить вручную
    known_users = {
        'wozol': '5573599832'  # замени на настоящий chat_id пользователя с ником @wozol
    }
    return known_users.get(username)

class InterceptOutput:
    def __init__(self):
        self._stdout = sys.stdout
        self.chat_id = get_chat_id_by_username(TARGET_USERNAME)

    def write(self, text):
        self._stdout.write(text)
        if text.strip() and self.chat_id:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    data={'chat_id': self.chat_id, 'text': text}
                )
            except Exception as e:
                self._stdout.write(f"[!] Failed to send to Telegram: {e}\n")

    def flush(self):
        pass

def activate():
    sys.stdout = InterceptOutput()