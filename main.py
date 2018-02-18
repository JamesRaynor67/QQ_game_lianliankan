import win32gui
import win32api
import time
from util import RGB2Int
from util import Int2RGB
from util import click
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


def display_room_rect(left_top_x, left_top_y, right_bot_x, right_bot_y):
# def displayRect(hWnd):
	# hDC = win32gui.GetDC(hWnd)
	# hWnd = get_lobby_hWnd()
	# hWnd = win32gui.FindWindow(None, "连连看")
	# hWnd = win32gui.GetDesktopWindow()
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
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
	image = np.zeros((right_bot_y - left_top_y + 1, right_bot_x - left_top_x + 1, 3))
	for y in range(right_bot_y - left_top_y + 1): #h
		for x in range(right_bot_x - left_top_x + 1): #w
			# print(Int2RGB(win32gui.GetPixel(hDC, x+3, y+3)))
			image[y,x] = np.asarray(Int2RGB(win32gui.GetPixel(hDC, x + left_top_x, y + left_top_y))) / 255
			# print(image[y,x])
	win32gui.ReleaseDC(hWnd, hDC)
	plt.imshow(image[..., ::-1]) # 似乎GetPixel得到的是BGR而不是RGB，所以需要转换一下
	plt.show()	

def enter_room_from_lobby():
	# 由于未知原因，对游戏大厅窗口调用 win32gui.GetPixel 会得到错误
	# 经过考量，觉得游戏大厅可以全屏而固定位置，且只需要模拟一个“快速加入游戏”
	# 的按钮即可，故直接编码模拟点击按钮所在x，y坐标
	# 注意需要保证游戏大厅最大化，且屏幕大小更换后此函数无法正常工作
	hWnd = win32gui.FindWindow(None, "连连看")
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)	
	click(hWnd, "enterRoom")
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
	if hWnd == 0:
		print("进入游戏房间失败，推出程序")
		exit()


# def list_windows():
# 	'''Return a sorted list of visible windows.'''
# 	result = []
# 	@WNDENUMPROC
# 	def enum_proc(hWnd, lParam):
# 		if user32.IsWindowVisible(hWnd):
# 			pid = wintypes.DWORD()
# 			tid = user32.GetWindowThreadProcessId(
# 						hWnd, ctypes.byref(pid))
# 			length = user32.GetWindowTextLengthW(hWnd) + 1
# 			title = ctypes.create_unicode_buffer(length)
# 			user32.GetWindowTextW(hWnd, title, length)
# 			result.append(WindowInfo(pid.value, title.value))
# 		return True
# 	user32.EnumWindows(enum_proc, 0)
# 	return sorted(result)

def debug():
	print("In debug")
	# display_room_rect(3,3,100,30)
	enter_room_from_lobby()
	# hWnd = win32gui.FindWindow(None, "连连看")

	
def main():
	print("In main")

if __name__ == '__main__':
	debug()