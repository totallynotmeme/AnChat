# /res/blueberry/lang/__init__.py



__all__ = [
    "en",
    "ru",
]

# from . import * # pyinstaller spaghetti refuses to work with this
from . import en, ru


langmap = {i: eval(i) for i in __all__}
default = langmap["en"]


