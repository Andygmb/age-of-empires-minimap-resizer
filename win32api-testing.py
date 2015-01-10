import win32api, win32gui, time, pywintypes


#http://docs.activestate.com/activepython/2.6/pywin32/win32gui__FindWindowEx_meth.html 
#http://docs.activestate.com/activepython/2.6/pywin32/win32gui__GetWindowRect_meth.html
while True:
	print win32api.GetSystemMetrics(32)
	aoe_window = win32gui.FindWindow(None, "Age of Empires II: HD Edition") # defaults to 0 if not found
	try:
		co_ords = win32gui.GetWindowRect(aoe_window)
	except (pywintypes.error) as e:
		print e[2]
		print e
	# print co_ords
	time.sleep(5)