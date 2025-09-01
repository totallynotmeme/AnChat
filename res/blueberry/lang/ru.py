# /res/blueberry/lang/ru.py
# Russian localization for this client



WINDOW_TITLE = "AnChat - Клиент Blueberry"
CORE_VERSION = "Версия ядра: {}"
CLIENT_VERSION = "Версия клиента: {}"

FIELD_USERNAME = "Ваше имя"
FIELD_ADDRESS = "Адрес сервера"
CONNECT_BUTTON = "Подключиться"

STATUS_TEXT_DEFAULT = "Заполните поля и нажмите Подключиться"
STATUS_TEXT_TRYING = "Пытаемся подключиться, подождите..."
STATUS_TEXT_FAILED = "Ошибка: {}"

OPTIONS_TITLE = "Настройки"
OPTIONS_LANGUAGE = "Поменять язык (нужен перезапуск)"


MESSAGE_CONNECTED = "Подключён к серверу, введите /disconnect чтобы вернуться в меню"
MESSAGE_DISCONNECTED = "Отключён от сервера"
MESSAGE_DUMPED = "История сообщений была сохранена в {}"
MESSAGE_STREAMING_START = "Передаём файл '{}' участникам чата"
MESSAGE_STREAMING_END = "Передача завершена."

CHATBOX_FIELD = "Напишите своё сообщение здесь"
CONNECTION_ERROR = "Ошибка соединения: {}"

ERROR_CODES = {
    b"BADPACKET": "Получен неправильный пакет сообщения",
    b"WRONGHASH": "Сообщение не прошло проверку хеша, пакет повреждён",
    b"DUPESALT": "Получено сообщение с дубликатом соли. Возможная атака повтора пакета?",
}
