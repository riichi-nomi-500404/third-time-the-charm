# Import Modules
import os # Contains methods for interacting with the OS.

# Retrieves and stores all files and directories in the current directory.
def run(**args): # **args can accept any number of keyword arguments, but are not used for this function.
    print("[*] In dirlister module.") # Prints out a message for debugging/logging purpose.
    files = os.listdir('.') # Retrieves and stores of all files and directories in the current directory. 
    return str(files) # Returns the file variable as a string which is a list of directory contents.