import sys
import cStringIO
import threading
import Queue
from math import floor
from ctypes import windll

import win32gui
import win32con
import win32ui
import pygame
from PIL import Image
from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, VIDEORESIZE

class MaxiMap:
	def __init__(self):
		self.screen = None
		self.aoe_hwnd = None
		self.map_w, self.map_h = 350, 175
		# Pygame window size
		self.window_size = self.map_w * 2, self.map_h * 2
		self.q = Queue.Queue()

	def get_hwnd(self, hwnd_string):
		# FindWindowEx returns 0 if it cannot find the string arg
		self.aoe_hwnd = win32gui.FindWindowEx(None, 0, None, hwnd_string)
		return bool(self.aoe_hwnd)

	def resize_window(self, event, screen):
		self.window_size = event.dict['size']
		set_screen(self.window_size)

		if self.aoe_hwnd:
			self.screengrab(screen)
		else:
			self.display_text("Could not find Age of Empires II Window", screen)

	def print_window(self, hwnd, saveDC):
		return windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

	def screengrab(self, screen):
		hwnd = self.aoe_hwnd
		left, top, right, bot = win32gui.GetClientRect(hwnd)
		self.aoe2_window_w = right - left
		self.aoe2_window_h = bot - top
		# Returns the device context (DC) for the entire window, 
		# including title bar, menus, and scroll bars.
		hwndDC = win32gui.GetWindowDC(hwnd)
		# Creates a DC object from an integer handle.
		mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
		# Creates a memory device context (DC) compatible with the specified device.
		saveDC = mfcDC.CreateCompatibleDC()
		# Setting window origin to the top left hand corner of the minimap
		saveDC.SetWindowOrg((self.aoe2_window_w - self.map_w,self.aoe2_window_h - self.map_h))
		#Creates bitmap Object
		saveBitMap = win32ui.CreateBitmap()
		#Creates a bitmap object from a HBITMAP.
		saveBitMap.CreateCompatibleBitmap(mfcDC, self.map_w, self.map_h)
		saveDC.SelectObject(saveBitMap)
		# Spawn a new thread seperate to main thread for the PrintWindow function 
		# because PrintWindow is a synchronous blocking function that can cause hanging if
		# ran in the same thread as the display code
		NewThread(self.print_window, hwnd, saveDC, self.q).start()
		# Get the DC from the queue along with the bool result.
		saveDC, result = self.q.get()
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
			screen.blit(pygame.image.load(tmp),(0,0))
		else:
			self.display_text("Could not grab game window to display", screen)

	def display_text(self, text, screen):
		font = pygame.font.Font(None, 30)
		text = font.render(text, False, (255,255,255))
		screen.fill((0,0,0))
		screen.blit(text, (10, 10))

	def translate_co_ord(self, co_ord, scaled_value, original_value, window_dimension):
  		percentage = 100 * float(co_ord)/float(scaled_value)
  		return (window_dimension - original_value) + int(floor((percentage * original_value) / 100.0))

	def mouse_click(self, (x, y), button):
		x = self.translate_co_ord(x, self.window_size[0], self.map_w, self.aoe2_window_w)
		y = self.translate_co_ord(y, self.window_size[1], self.map_h, self.aoe2_window_h)
		aoe2_pycwnd = self.make_pycwnd(self.aoe_hwnd)
		pygame_pycwnd = self.make_pycwnd(win32gui.FindWindowEx(None, 0, None, PYGAME_WINDOW_NAME))
		lParam = y << 16 | x
		#print lParam & 0xF777, lParam >> 16
		try:
			aoe2_pycwnd.SetForegroundWindow()
		except:
			pass

		if button == 1:
			aoe2_pycwnd.SendMessage(win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
			aoe2_pycwnd.SendMessage(win32con.WM_LBUTTONUP, 0, lParam)
		elif button == 3:
			aoe2_pycwnd.SendMessage(win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
			aoe2_pycwnd.SendMessage(win32con.WM_RBUTTONUP, 0, lParam)
		aoe2_pycwnd.UpdateWindow()

		try:
			pygame_pycwnd.SetForegroundWindow()
		except:
			pass
		pygame_pycwnd.UpdateWindow()

	def make_pycwnd(self,hwnd):
		PyCWnd = win32ui.CreateWindowFromHandle(hwnd)
		return PyCWnd


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

def pygame_setup(window_size):
	# Init pygame, create clock, set up display to be resizeable and use hardware acc
	# set up caption/icon
	pygame.init()
	clock = pygame.time.Clock()
	screen = set_screen(window_size)
	icon = pygame.image.load("icon.png")
	pygame.display.set_icon(icon)
	pygame.display.set_caption(PYGAME_WINDOW_NAME)
	return screen, clock, pygame

def set_screen(window_size):
	screen = pygame.display.set_mode(window_size,HWSURFACE|DOUBLEBUF|RESIZABLE)
	return screen
	

PYGAME_WINDOW_NAME = "Age of empires Minimap resizer"

def main():
	Map = MaxiMap()
	window_size = Map.window_size
	screen, clock, pygame = pygame_setup(window_size)
	running = True
	mouse_states = {
	1:False,
	2:False,
	3:False
	}
	while running:
		pygame.event.pump()
		Map.get_hwnd("Age of Empires II: HD Edition")
		for button, value in mouse_states.iteritems():
			if value and Map.aoe_hwnd:
				Map.mouse_click(pygame.mouse.get_pos(), value)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				sys.exit()

			if event.type == VIDEORESIZE:
				Map.resize_window(event, screen)

			if event.type == pygame.MOUSEBUTTONDOWN:
				if Map.aoe_hwnd:
					Map.mouse_click(event.pos, event.button)
				mouse_states[event.button] = True

			if event.type == pygame.MOUSEBUTTONUP:
				mouse_states[event.button] = False


		if Map.aoe_hwnd:
			Map.screengrab(screen)

		# If no window for age of empires II could be found.
		else:
			Map.display_text("Could not find Age of Empires II Window", screen)
		
		pygame.display.flip()
		clock.tick(30)



main()
