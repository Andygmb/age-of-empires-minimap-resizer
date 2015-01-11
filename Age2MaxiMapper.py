import sys
import time
import pygame
import win32gui
import win32api
import win32ui
import cStringIO
import threading
import Queue
import random 
from PIL import Image, ImageGrab
from pygame.locals import *
from ctypes import windll


class MaxiMap:
	def __init__(self, pygame):
		self.pygame = pygame
		self.border_width = win32api.GetSystemMetrics(32)
		self.screen = None
		self.aoe_hwnd = None
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
		MyThread(self.print_window, hwnd, saveDC, self.q).start()
		saveDC = self.q.get()
		result = 1
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


class MyThread(threading.Thread):
	def __init__(self, print_window, hwnd, saveDC, queue):
		threading.Thread.__init__(self)
		self.__queue = queue 
		self.hwnd = hwnd
		self.saveDC = saveDC
		self.cb = print_window

	def run(self):
		result = self.cb(self.hwnd,self.saveDC)
		print self.saveDC
		self.__queue.put(self.saveDC,random.randint(0, 1000) )


def main():
	running = True
	Map = MaxiMap(pygame)
	Map.pygame_setup()

	while running:
		print threading.active_count()
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


 		if Map.aoe_hwnd:
			Map.screen.blit(Map.pygame.image.load(Map.screengrab()), (0,0))
			Map.pygame.display.flip()

		# If no window for age of empires II could be found.
		else:
			Map.display_text("Could not find Age of Empires II Window")
			Map.pygame.display.flip()
		Map.clock.tick(30)



main()