"""The core can print information through this module."""
# dem/cli/core_cb.py

def core_cb(*args):
    for arg in args:
        print("value: " + str(arg))
        print("type: " + str(type(arg)))
        print("")