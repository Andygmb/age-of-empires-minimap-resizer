import win32gui
import win32ui
from ctypes import windll
from PIL import Image

hwnd = win32gui.FindWindow(None, 'Calculator')

# Change the line below depending on whether you want the whole window
# or just the client area. 
#left, top, right, bot = win32gui.GetClientRect(hwnd)
left, top, right, bot = win32gui.GetWindowRect(hwnd)
w = right - left
h = bot - top

#returns the device context (DC) for the entire window, including title bar, menus, and scroll bars.
hwndDC = win32gui.GetWindowDC(hwnd)
#Creates a DC object from an integer handle.
mfcDC  = win32ui.CreateDCFromHandle(hwndDC)

#Creates a memory device context (DC) compatible with the specified device.
saveDC = mfcDC.CreateCompatibleDC()

saveDC.SetViewportOrg((15,10))
saveDC.SetWindowOrg((100,10))

#Creates bitmap Object
saveBitMap = win32ui.CreateBitmap()
#Creates a bitmap object from a HBITMAP.

saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

saveDC.SelectObject(saveBitMap)

# Change the line below depending on whether you want the whole window
# or just the client area. 
#result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)

im = Image.frombuffer(
    'RGB',
    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
    bmpstr, 'raw', 'BGRX', 0, 1)

win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

if result == 1:
    #PrintWindow Succeeded
    im.save("test.bmp")