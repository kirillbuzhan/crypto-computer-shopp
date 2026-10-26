"""Настройки приложения из переменных окружения.

Все параметры необязательны — значения по умолчанию подходят для
локального запуска. При развёртывании на сайте обычно задают
ROOT_PATH (если сайт открывается не с корня домена) и сведения о
кафедре/авторах для подвала и страницы «О проекте».
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
FREQUENCY_FILE = BASE_DIR / "frequency.json"


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


# Префикс, под которым сайт опубликован за обратным прокси,
# например "/crypto-lab" для https://university.ru/crypto-lab/.
ROOT_PATH = _env("ROOT_PATH", "").rstrip("/")

SITE_TITLE = _env("SITE_TITLE", "Криптография и теория информации")
SITE_SUBTITLE = _env("SITE_SUBTITLE", "Интерактивная лаборатория: кодирование, помехоустойчивые коды, шифры и теория чисел")
ORGANIZATION = _env("SITE_ORGANIZATION", "")
AUTHORS = _env("SITE_AUTHORS", "")
CONTACT_EMAIL = _env("SITE_CONTACT_EMAIL", "")

# Ограничения ввода — защищают сервер от слишком тяжёлых запросов.
MAX_MESSAGE_LENGTH = _env_int("MAX_MESSAGE_LENGTH", 500)
MAX_ELGAMAL_MESSAGE_LENGTH = _env_int("MAX_ELGAMAL_MESSAGE_LENGTH", 200)

# Версия статики: меняется при обновлении, чтобы браузеры не держали старые файлы.
STATIC_VERSION = _env("STATIC_VERSION", "17")
