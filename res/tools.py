# /res/tools.py
# generic nice-to-have minitools that might be useful to some people

# functions should only take strings as arguments, and return a string / None
# to make it easier to integrate them into clients


from . import encryption
from . import wordip
from inspect import getfullargspec as getspec
from time import sleep


# to include this, add hello_world to _all list at the bottom
def hello_world():
    """
    "Hello world" tool example!
    ADDED: v0.2.1-ALPHA
    
    Proof of concept function to test basic functionality of this system.
    Waits 1 second before returning a funny phrase
    
    (this is here for testing during development. will be unlisted later)
    
    Takes:   nothing
    Returns: a string
    """
    sleep(1)
    return "World, hello!"

def wordip_interface(bitarray_or_wordip):
    """
    Tool interface for interacting with wordip functions
    ADDED: v0.2.1-ALPHA
    
    Is a fancy way to represent bits in words.
    Put your server address here to see its raw content!
    
    Takes:   bitarray "0101" or list of valid words
    Returns: wordip encoded / decoded bitarray
    """
    bitarray_valid = {"0", "1"}
    if set(bitarray_or_wordip) | bitarray_valid == bitarray_valid:
        # bitarray -> wordip
        return wordip.encode(bitarray_or_wordip)
    if all(i in wordip.wordbase for i in bitarray_or_wordip.lower().split()):
        # wordip -> bitarray most likely
        return wordip.decode(bitarray_or_wordip)
    raise TypeError("Invalid input, expected bitarray or list of valid words.\
 Make sure the spelling is correct")


_all = [hello_world, wordip_interface]
_args = {i.__name__: getspec(i).args for i in _all}
_all = {i.__name__: i for i in _all}
