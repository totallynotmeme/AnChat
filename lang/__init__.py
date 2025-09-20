# /res/blueberry/lang/__init__.py



__all__ = [
    "en",
    "ru",
]

from . import *


langmap = {i: eval(i) for i in __all__}
default = langmap["en"]

