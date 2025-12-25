# /res/tools.py
# generic nice-to-have minitools that might be useful to some people

# functions should only take strings as arguments, and return a string / None
# to make it easier to integrate them into clients


from . import encryption
from . import wordip
from inspect import getfullargspec as getspec
from time import sleep
import os


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


def split_file(file_path, chunk_size_kbytes):
    """
    Tool for splitting a single file into multiple chunks (or merging them back)
    ADDED: v0.2.1-ALPHA
    
    Please be careful when splitting large files into smaller chunks as it
    might create a LOT of files in a short amount of time.
    
    Takes:   path to file / one of the chunks, chunk size in KB (if splitting)
    Creates: new folder with file chunks / single file in the same directory
    Returns: string with the state of the task
    """
    
    if "\\" not in file_path:
        # maybe they wrote it like C:/Users/... instead of C:\Users\...?
        file_path = file_path.replace("/", "\\")
    
    if not os.path.isfile(file_path):
        raise ValueError("Couldn't find this file, make sure the path is correct")
    
    folder = os.path.dirname(file_path) + "\\"
    
    digits = "0123456789"
    if file_path.rstrip(digits).endswith(".chunk"):
        # chunks to file
        base = file_path.rstrip(digits)
        base_name = base.rsplit("\\", 1)[1]
        real_name = base.removesuffix(".chunk")
        display_name = real_name.rsplit("\\", 1)[1]
        
        files = os.listdir(folder)
        files = [i for i in files if i.rstrip(digits) == base_name]
        data = bytearray()
        for i in files:
            with open(folder + i, "rb") as f:
                data.extend(f.read())
        
        with open(real_name, "wb") as f:
            f.write(data)
        
        return f"Merged {len(files)} chunks into {display_name}!"
    else:
        # file to chunks
        try:
            chunk_size = int(chunk_size_kbytes) * 1024
        except ValueError:
            raise ValueError("Please use a valid number for the chunk size!")
        
        if chunk_size < 1024:
            raise ValueError("Can't split into chunks less than 1kb!")
        
        if "." in file_path:
            name, extension = file_path.rsplit(".", 1)
        else:
            name = file_path
            extension = ""
        only_name = name.rsplit("\\", 1)[1]
        
        chunks_folder = f"{name}-{extension}-chunks\\"
        if not os.path.isdir(chunks_folder):
            os.mkdir(chunks_folder)
        
        with open(file_path, "rb") as f:
            data = f.read()
        chunks = (data[i: i+chunk_size] for i in range(0, len(data), chunk_size))
        
        for ind, i in enumerate(chunks, start=1):
            # SURELY no one will create more than 999 chunks
            chunk_name = f"{only_name}.{extension}.chunk{ind:03}"
            with open(chunks_folder + chunk_name, "wb") as f:
                f.write(i)
        return f"Created {ind} chunks for this file!"


_all = [wordip_interface, split_file]
_args = {i.__name__: getspec(i).args for i in _all}
_all = {i.__name__: i for i in _all}
