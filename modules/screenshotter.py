import win32api 
import win32con  
import win32gui
import win32ui

# Retrieves the dimension of the entire screen.
def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

# The function that handles the process of taking a screenshot and saving it to a file.
def screenshot(name='screenshot'):
    hdesktop = win32gui.GetDesktopWindow() # Gets the handle to the desktop window.
    width, height, left, top = get_dimensions() # Sets the dimensions of the screen.

    desktop_dc = win32gui.GetWindowDC(hdesktop) # Allows drawing on the desktop.
    img_dc = win32ui.CreateDCFromHandle(desktop_dc) # Creates a device context from the desktop's DC.
    mem_dc = img_dc.CreateCompatibleDC() # Create a memory device compatible with the desktop DC. Stores the image capture before writing to file.

    screenshot = win32ui.CreateBitmap() # Create a bitmap object set to the device context of our desktop.
    screenshot.CreateCompatibleBitmap(img_dc, width, height) # Resizes the bitmap to match the screen dimensions.
    mem_dc.SelectObject(screenshot) # Points the bitmap to the memory DC.
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp') # Saves the captured bitmap as a file.
    
    mem_dc.DeleteDC() # Deletes the memory dc to free up resources.
    win32gui.DeleteObject(screenshot.GetHandle()) # Deletes the bitmap obect to free resources.

# Calls the screenshot() function and returns the img file.
def run():
        screenshot()
        # Opens the screenshot file and convert the data into bytes and store it in a variable.
        with open('screenshot.bmp', 'rb') as img_file:
            img_bytes = img_file.read()
        return img_bytes # Returns the stored variable.

'''
Below is not needed while being runned as a module.

# Checks if the script is being run directly to start its execution.  
if __name__ == '__main__':
    screenshot()
'''
