#Age of Empires Minimap Resizer

##Resizes the Age of Empires II: HD Edition ingame minimap & resizes it into a pygame display, for use on a second monitor

![](http://i.imgur.com/0DHR2ZK.jpg)

-

##Goals

* Add fullscreen support (means changing from pygame to pyglet or other library)
* Change get_hwnd to use EnumWindows() & regex search for age of empires windows other than the HD edition.
* Figure out a way to keep the aoe2 window in the foreground or in focus (so the game continues playing) without it having mouse focus (causes ingame view to scroll towards mouse position)

