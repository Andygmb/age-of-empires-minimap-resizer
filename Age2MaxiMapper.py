import sys
import pygame
import win32gui
import win32con
import win32api
import win32ui
import cStringIO
import threading
import time
import Queue
from math import floor
from PIL import Image
from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, VIDEORESIZE
from ctypes import windll


class MaxiMap:
	def __init__(self, pygame):
		self.pygame = pygame
		self.border_width = win32api.GetSystemMetrics(32)
		self.screen = None
		self.aoe_hwnd = None
		self.aoe2window = None
		self.map_w, self.map_h = 350, 175
		self.window_size = 700, 350
		self.q = Queue.Queue()

	def pygame_setup(self):
		# Init pygame, create clock, set up display to be resizeable and use hardware acc
		# set up caption/icon
		self.pygame.init()
		self.clock = self.pygame.time.Clock()
		self.set_screen(self.window_size)
		self.pygame.display.set_icon(pygame.image.load("icon.bmp"))
		self.pygame.display.set_caption("Age of empires Minimap resizer")

	def get_hwnd(self):
		# FindWindowEx returns 0 if it cannot find the string arg
		self.aoe_hwnd = win32gui.FindWindowEx(None, 0, None, "Age of Empires II: HD Edition")
		if self.aoe_hwnd:
			return True
		else:
			return False

	def resize_window(self, event):
		self.window_size = event.dict['size']
		self.set_screen(self.window_size)
		if self.aoe_hwnd:
			self.screen.blit(self.pygame.image.load(self.screengrab()),(0,0))
		else:
			self.display_text("Could not find Age of Empires II Window")

	def set_screen(self, window_size):
		self.screen = self.pygame.display.set_mode(window_size,HWSURFACE|DOUBLEBUF|RESIZABLE)

	def print_window(self, hwnd, saveDC):
		result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
		return result

	def screengrab(self):
		hwnd = self.aoe_hwnd
		left, top, right, bot = win32gui.GetClientRect(hwnd)
		w = right - left
		h = bot - top
		#returns the device context (DC) for the entire window, including title bar, menus, and scroll bars.
		hwndDC = win32gui.GetWindowDC(hwnd)
		#Creates a DC object from an integer handle.
		mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
		#Creates a memory device context (DC) compatible with the specified device.
		saveDC = mfcDC.CreateCompatibleDC()
		saveDC.SetWindowOrg((w - self.map_w,h - self.map_h))
		#Creates bitmap Object
		saveBitMap = win32ui.CreateBitmap()
		#Creates a bitmap object from a HBITMAP.
		saveBitMap.CreateCompatibleBitmap(mfcDC, self.map_w, self.map_h)

		saveDC.SelectObject(saveBitMap)
		NewThread(self.print_window, hwnd, saveDC, self.q).start()
		saveDC, result = self.q.get()
		# Change the line below depending on whether you want the whole window
		# or just the client area. 
		#result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
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
			tmp = cStringIO.StringIO()
			im = im.resize(self.window_size)
			im.save(tmp, "bmp")
			tmp.seek(0)
			return tmp

		# # Create cStringIO file object
		# tmp = cStringIO.StringIO()
		# # Grab image, save to temp file object
		# screengrab = ImageGrab.grab(bbox=self.map_bbox).resize(self.window_size)
		# screengrab.save(tmp, "bmp")
		# # Seeking tells the file object to start at byte 0
		# tmp.seek(0)
		# return tmp

	def display_text(self, text):
		font = pygame.font.Font(None, 30)
		text = font.render(text, False, (255,255,255))
		self.screen.fill((0,0,0))
		self.screen.blit(text, (10, 10))

	def translate_co_ord(self, co_ord, scaled_value, original_value):
  		percentage = 100 * float(co_ord)/float(scaled_value)
  		return int(floor((percentage * original_value) / 100.0))

	def mouse_click(self, (x, y), button):
		if self.aoe_hwnd:
			left, top, right, bot = win32gui.GetClientRect(self.aoe_hwnd)
			x = (right - self.map_w) + (self.translate_co_ord(x, self.window_size[0], self.map_w))
			y = (bot - self.map_h) + (self.translate_co_ord(y, self.window_size[1], self.map_h))
			aoe2window = self.make_pycwnd(self.aoe_hwnd)
			pygamewindow = self.make_pycwnd(win32gui.FindWindowEx(None, 0, None, "Age of empires Minimap resizer"))
			lParam = y << 16 | x
			#print lParam & 0xF777, lParam >> 16
			#self.aoe2window.SetCapture()
			try:
				aoe2window.SetForegroundWindow()
			except win32ui.error as e:
				print e
				self.aoe_hwnd = None
			if button == 1:
				aoe2window.SendMessage(win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
				aoe2window.SendMessage(win32con.WM_LBUTTONUP, 0, lParam)
			elif button == 3:
				aoe2window.SendMessage(win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
				aoe2window.SendMessage(win32con.WM_RBUTTONUP, 0, lParam)
			aoe2window.UpdateWindow()
			#self.aoe2window.ReleaseCapture()
			try:
				pygamewindow.SetForegroundWindow()
			except win32ui.error as e:
				print e
				self.aoe_hwnd = None
			pygamewindow.UpdateWindow()

	def make_pycwnd(self,hwnd):
		PyCWnd = win32ui.CreateWindowFromHandle(hwnd)
		return PyCWnd

# HWND h = (hwnd of window)

# WORD mouseX = 10;// x coord of mouse

# WORD mouseY = 10;// y coord of mouse

# PostMessage(hWnd,WM_LBUTTONDOWN,0,MAKELPARAM(mouseX,mouseY));


class NewThread(threading.Thread):
	def __init__(self, print_window, hwnd, saveDC, queue):
		threading.Thread.__init__(self)
		self.__queue = queue 
		self.hwnd = hwnd
		self.saveDC = saveDC
		self.function = print_window

	def run(self):
		result = self.function(self.hwnd,self.saveDC)
		self.__queue.put((self.saveDC, result),1 )



def main():
	running = True
	Map = MaxiMap(pygame)
	Map.pygame_setup()
	while running:
		Map.pygame.event.pump()
		Map.get_hwnd()
		for event in Map.pygame.event.get():
			if event.type == Map.pygame.QUIT:
				running = False
				Map.pygame.quit()
				sys.exit()

			if event.type == VIDEORESIZE:
				Map.resize_window(event)
				Map.pygame.display.flip()

			if event.type == pygame.MOUSEBUTTONDOWN:
				Map.mouse_click(event.pos, event.button)

 		if Map.aoe_hwnd:
			Map.screen.blit(Map.pygame.image.load(Map.screengrab()), (0,0))
			Map.pygame.display.flip()

		# If no window for age of empires II could be found.
		else:
			Map.display_text("Could not find Age of Empires II Window")
			Map.pygame.display.flip()
		Map.clock.tick(30)



main()