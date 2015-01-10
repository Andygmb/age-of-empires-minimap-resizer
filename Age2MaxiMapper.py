import sys
import time
import pygame
import win32gui
import win32api
import win32ui
import cStringIO
from PIL import Image, ImageGrab
from pygame.locals import *
from ctypes import windll


class MaxiMap:
	def __init__(self, pygame):
		self.pygame = pygame
		self.border_width = win32api.GetSystemMetrics(32)
		self.screen = None
		self.aoe_window = None
		self.map_bbox = None
		self.map_w, self.map_h = 350, 175
		self.window_size = 700, 350

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
		if self.aoe_window != 0:
			# GetWindowRect returns the top left x/y and bottom right x/y co-ords
			# Take the bottom right co-ords and minus the map size / window border width
			# to get the map square bbox
			try:
				map_bbox = win32gui.GetWindowRect(self.aoe_window)
				map_bbox = [
				map_bbox[2] - self.map_w,
				map_bbox[3] - self.map_h,
				map_bbox[2] - self.border_width,
				map_bbox[3] - self.border_width
				]
				return map_bbox

			except (pywintypes.error) as e:
				print e
				return False
		else:
			return False

	def resize_window(self, event):
		self.window_size = event.dict['size']
		self.set_screen(self.window_size)
		if self.map_bbox:
			self.screen.blit(self.pygame.image.load(self.screengrab()),(0,0))
		else:
			self.display_text("Could not find Age of Empires II Window")

	def set_screen(self, window_size):
		self.screen = self.pygame.display.set_mode(window_size,HWSURFACE|DOUBLEBUF|RESIZABLE)

	def screengrab(self):
		# Change the line below depending on whether you want the whole window
		# or just the client area. 
		#left, top, right, bot = win32gui.GetClientRect(hwnd)
		hwnd = self.aoe_window
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

		# Change the line below depending on whether you want the whole window
		# or just the client area. 
		#result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
		result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
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



def main():
	running = True
	Map = MaxiMap(pygame)
	Map.pygame_setup()

	while True:
		Map.map_bbox = Map.set_map_bbox()
		for event in Map.pygame.event.get():
			if event.type == Map.pygame.QUIT:
				running = False
				Map.pygame.quit(); 
				sys.exit();

			if event.type == VIDEORESIZE:
				Map.resize_window(event)
				Map.pygame.display.flip()

 		if Map.map_bbox:
			Map.screen.blit(Map.pygame.image.load(Map.screengrab()), (0,0))
			Map.pygame.display.flip()

		# If no map bbox could be found, no window for age of empires II could be found.
		else:
			Map.display_text("Could not find Age of Empires II Window")
			Map.pygame.display.flip()

		Map.clock.tick(30)



main()
pygame.quit()