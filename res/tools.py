# /res/tools.py
# generic nice-to-have minitools that might be useful to some people

# functions should only take strings as arguments, and return a string / None
# to make it easier to integrate them into clients


from . import encryption
from inspect import getfullargspec as getspec


def hello_world():
    """
    "Hello world" tool example!
    ADDED: v0.2.1-ALPHA
    
    Proof of concept function to test basic functionality of this system
    
    Takes:   nothing
    Returns: a string
    """
    return "World, hello!"


_all = [hello_world]
_args = {i.__name__: getspec(i).args for i in _all}
_all = {i.__name__: i for i in _all}
