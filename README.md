#Age of Empires Minimap Resizer


![](http://i.imgur.com/0DHR2ZK.jpg)

###Resizes the Age of Empires II: HD Edition ingame minimap & resizes it into a pygame display, for use on a second monitor

-

##Goals

* Add fullscreen support (means changing from pygame to pyglet or other library)
* Change get_hwnd to use EnumWindows() & regex search for age of empires windows other than the HD edition.
* Figure out a way to keep the aoe2 window in the foreground or in focus (so the game continues playing) without it having mouse focus (causes ingame view to scroll towards mouse position)
* Use py2exe or pyinstaller for a standalone .exe

##Usage

    python Age2MaxiMapper.py 

It will autodetect if the AoE2 window is available, and display it. You can click on the enlarged minimap to send clicks to the actual game, but due to how age of empires doesn't run when it's not in focus/is the foreground window, the minimap will only update when you click back into the game. 