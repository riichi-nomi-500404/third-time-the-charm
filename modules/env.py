# Import Modules
import os # Contains methods for interacting with the OS.

# Returns all enviroment variables that could potentially include information
# like PATH, HOME, directory, system language, and more.
def run(**args): # **args can accept any number of keyword arguments, but are not used for this function.
    print("[*] In environment module") # Prints out a message for debugging/logging purpose.
    return os.environ # The command that returns all the enviroment variables.
