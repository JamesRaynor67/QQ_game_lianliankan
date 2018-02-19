import win32api
import win32con
import win32gui
import time
import random
import matplotlib.pyplot as plt
import numpy as np

g_lobby_hWnd = 0

def RGB2Int(red, green, blue):
	return red + green * 256 + blue * 256 * 256

def Int2RGB(rgb):
	red = (rgb >> 16) & 255
	green = (rgb >> 8) & 255
	blue = rgb & 255
	return (red, green, blue)

def enter_room_from_lobby():
	# 20180219
	# 因为有title为 连连看 的隐藏窗口存在导致之前
	# 无法getPixel即发送鼠标信息失败问题
	# 我们需要获取visible的title为 连连看 的窗口
	hWnd = get_lobby_hWnd()
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "enterRoom")
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
	if hWnd == 0:
		print("进入游戏房间失败，退出程序")
		exit()

def exit_room():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "exitRoom")

def click_start():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "clickStart")

def click(hWnd, action):
	delay_time = 0.1
	if action == "enterRoom":
		# x, y = -100, -80
		x, y = 270, 152
		delay_time = 3
	elif action == "clickStart":
		x, y = 650, 570
	elif action == "exitRoom": # 点右上角的乂，退出房间
		x, y = 780, 10
	elif action == "resort": # 重排
		x, y = 650, 200        
		delay_time = 8 + random.random() * 3 #等待提示文字消失，否则会影响下一步判断
	else:
		print("Wrong action string input, exiting...")
		exit()
	print("Clicked {} and {}".format(x,y))
	# win32api.SetCursorPos((x, y)) # important to make click valide
	print(win32gui.ClientToScreen(hWnd, (x, y)))
	win32api.SetCursorPos(win32gui.ClientToScreen(hWnd, (x, y))) # important to show where is acturally clicked
	lParam = win32api.MAKELONG(x, y) 
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, 0, lParam)
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, lParam)
	time.sleep(delay_time)

def display_room_rect(left_top_x, left_top_y, right_bot_x, right_bot_y):
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
			image[y,x] = np.asarray(Int2RGB(win32gui.GetPixel(hDC, x + left_top_x, y + left_top_y))) / 255
	# print(image)
	win32gui.ReleaseDC(hWnd, hDC)
	plt.imshow(image[..., ::-1]) # GetPixel得到的是BGR而不是RGB，所以需要转换一下
	plt.show()	

def enumHandler(hWnd, lParam):
	if win32gui.IsWindowVisible(hWnd) and win32gui.GetWindowText(hWnd) == "连连看":
		global g_lobby_hWnd
		g_lobby_hWnd = hWnd

def get_lobby_hWnd():
	# 在enumHandler中设置了g_lobby_hWnd作为返回值
	win32gui.EnumWindows(enumHandler, None)	
	# print("g_lobby_hWnd == {}".format(g_lobby_hWnd))
	# hDC = win32gui.GetWindowDC(g_lobby_hWnd)	
	# rect = win32gui.GetWindowRect(g_lobby_hWnd)
	# x = rect[0]
	# y = rect[1]
	# w = rect[2] - x
	# h = rect[3] - y
	# print("Window name: " + win32gui.GetWindowText(g_lobby_hWnd))
	# print("Window hDC: " + str(hDC))
	# print("x, y, w, h == " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + " ")
	# print()
	return g_lobby_hWnd

def debug():
	print("In debug util.py")
	enter_room_from_lobby()
	click_start()

if __name__ == '__main__':
	debug()