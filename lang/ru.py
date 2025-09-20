# /res/blueberry/lang/ru.py
# Russian localization for this client



WINDOW_TITLE = "AnChat - Клиент Blueberry"
CORE_VERSION = "Версия ядра: {}"
CLIENT_VERSION = "Версия клиента: {}"

FIELD_USERNAME = "Ваше имя (Anon)"
FIELD_ADDRESS = "Адрес сервера"
CONNECT_BUTTON = "Подключиться"

STATUS_TEXT_DEFAULT = "Заполните поля и нажмите Подключиться"
STATUS_TEXT_TRYING = "Пытаемся подключиться, подождите..."
STATUS_TEXT_FAILED = "Ошибка: {}"
STATUS_TEXT_BADIP = "Плохой формат IP адреса: {}"

OPTIONS_TITLE = "Настройки"
OPTIONS_LANGUAGE = "Язык"
OPTIONS_RESOLUTION = "Размер окна"
OPTIONS_FONT = "Шрифт"
OPTIONS_FONT_WARN = "Это экспериментальная настройка"
OPTIONS_APPLY = "Применить"


TASK_UNKNOWN = "Неизвестный текст статуса '{}' для задания {}"

TASK_STREAM_RUNNING = "Транслируем файл {} (#{}/{} кусков  {}%)"
TASK_STREAM_DONE = "Трансляция файла {} завершена ({} кусков)"
TASK_STREAM_FAILED = "Трансляция не удалась на куске #{}/{} (проверьте консоль для дополнительной информации)"

TASK_CONNECT_RUNNING = "Пытаемся подключиться к серверу"
TASK_CONNECT_DONE = "Подключение успешно!"
TASK_CONNECT_FAILED = "Не удалось подключиться"


MESSAGE_CONNECTED = "Подключён к серверу, введите /disconnect чтобы вернуться в меню"
MESSAGE_DISCONNECTED = "Отключён от сервера"
MESSAGE_DUMPED = "История сообщений была сохранена в {}"
MESSAGE_STREAMING_START = "Передаём файл '{}' участникам чата"
MESSAGE_STREAMING_END = "Передача завершена."
MESSAGE_STREAMING_FAIL = "Не удалось начать передачу файла: {}"
MESSAGE_STREAMING_WARN = """Передача файлов пока что не работает должным образом. Это будет исправлено в будущем.
Если вы уверены, что хотите передать данный файл, перетащите его в окно чата ещё раз"""

CHATBOX_FIELD = "Напишите своё сообщение здесь"
CONNECTION_ERROR = "Ошибка соединения: {}"

ERROR_CODES = {
    b"BADPACKET": "Получен неправильный пакет сообщения",
    b"WRONGHASH": "Сообщение не прошло проверку хеша, пакет повреждён",
    b"DUPESALT": "Получено сообщение с дубликатом соли. Возможная атака повтора пакета?",
}
