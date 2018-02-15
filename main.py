import win32gui
import time
from util import RGB2Int
from util import Int2RGB
import matplotlib.pyplot as plt
import numpy as np

# from ctypes import windll
# def callback(hwnd, extra):
#     rect = win32gui.GetWindowRect(hwnd)
#     x = rect[0]
#     y = rect[1]
#     w = rect[2] - x
#     h = rect[3] - y
#     print "Window %s:" % win32gui.GetWindowText(hwnd)
#     print "\tLocation: (%d, %d)" % (x, y)
#     print "\t    Size: (%d, %d)" % (w, h)

def get_lobby_hWnd():
	hWnd = 0
	while hWnd == 0:
		hWnd = win32gui.FindWindow(None, "连连看")
		print("尝试获取游戏大厅窗口handle")
		time.sleep(3)
	print("已获取大厅窗口handle")		
	return hWnd

def get_room_hWnd():
	hWnd = 0
	while hWnd == 0:
		hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
		print("尝试获取游戏房间窗口handle")
		time.sleep(3)
	print("已获取房间窗口handle")		
	return hWnd


def displayScreen():
	# hDC = win32gui.GetDC(hWnd)
	# hWnd = get_lobby_hWnd()
	# hWnd = win32gui.FindWindow(None, "连连看")
	# hWnd = win32gui.GetDesktopWindow()
	# user32 = windll.user32
	# user32.SetProcessDPIAware()
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
	
	print(hWnd)
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	hDC = win32gui.GetWindowDC(hWnd)

	rect = win32gui.GetWindowRect(hWnd)
	x = rect[0]
	y = rect[1]
	w = rect[2] - x
	h = rect[3] - y
	print("Window name: " + win32gui.GetWindowText(hWnd))
	print("Window hDC: " + str(hDC))
	print("x, y, w, h == " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + " ")
	image = np.zeros((h+4,w+4,3))
	for y in range(h-6):
		for x in range(w-6):
			if y % 20 != 0:
				break
			if x == 0:
				print(x, y)
			# time.sleep(1)
			# print(Int2RGB(win32gui.GetPixel(hDC, x+3, y+3)))
			image[y + 3,x + 3] = np.asarray(Int2RGB(win32gui.GetPixel(hDC, x+3, y+3)))
	# print(Int2RGB(win32gui.GetPixel(hDC, 500, 500)))
	# print(Int2RGB(win32gui.GetPixel(hDC, 11, 11)))
	# print(win32gui.GetPixel(hDC, 10, 10))
	win32gui.ReleaseDC(hWnd, hDC)
	plt.imshow(image)
	plt.show()	


def debug():
	print("In debug")
	# hWnd = get_lobby_hWnd()
	displayScreen()
	# print(get_room_hWnd())

def main():
	print("In main")

if __name__ == '__main__':
	debug()