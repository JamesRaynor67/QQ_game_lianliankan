import win32api
import win32con
import win32gui
import time
import random
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

class GameState(Enum):
	GS_INGAME = 1 #处在游戏中
	GS_OVER = 2 #游戏超时，等待其他玩家完成消除并结束一场游戏
	GS_INROOM = 3 #在房间里等待游戏开始
	GS_CLOSED = 4 #游戏窗口被关闭（主动关闭或者被踢出房间
	GS_MINIMIZED = 5 #游戏窗口被最小化（无法获取颜色值）
	GS_INLOBBY = 6 # 在游戏大厅中
	GS_UNKNOWN = 7 #未定义状态(这是错误)

def RGB2Int(red, green, blue):
	return red + green * 256 + blue * 256 * 256

def Int2RGB(rgb):
	red = (rgb >> 16) & 255
	green = (rgb >> 8) & 255
	blue = rgb & 255
	return (red, green, blue)

BACK_COLOR = RGB2Int(0x30,0x4C,0x70)
DEBUG = True
g_lobby_hWnd = 0

def enter_room_from_lobby():
	# 因为有title为 连连看 的隐藏窗口存在导致之前
	# 无法getPixel即发送鼠标信息失败问题
	# 我们需要获取visible的title为 连连看 的窗口
	while True:
		hWnd = get_lobby_hWnd()
		win32gui.SetForegroundWindow(hWnd)
		win32gui.SetActiveWindow(hWnd)
		click(hWnd, "enterRoom")
		hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
		if hWnd == 0:
			print("进入游戏房间失败，重新尝试进入")
		else:
			break

def exit_room():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "exitRoom")
	time.sleep(3)

def click_start():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "clickStart")

def click(hWnd, action):
	delay_time = 0.1
	# 注意这里的点都是考虑过IDP拉伸后的位置
	if action == "enterRoom":
		x, y = 270, 152
		delay_time = 5
	elif action == "clickStart":
		x, y = 650, 570
	elif action == "exitRoom": # 点右上角的乂，退出房间
		x, y = 780, 10
	elif action == "resort": # 重排
		x, y = 650, 200
		delay_time = 8 + random.random() * 3 #等待提示文字消失，否则会影响下一步判断
	elif action == "click_dialog_yes":
		x, y = 820, 280
		# x, y = 0, 0
	else:
		print("Wrong action string input, exiting...")
		exit()
	print("Clicked: {}".format(win32gui.ClientToScreen(hWnd, (x, y))))
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
	return g_lobby_hWnd

def scan_game_board():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	win32api.SetCursorPos((10, 10)) # 移开鼠标防止潜在干扰(也许鼠标根本不会干扰？)

	hDC = win32gui.GetWindowDC(hWnd)
	board_width, board_height = 19, 11
	board = [[0 for w in range(board_width)] for h in range(board_height)]
	ptns = []

	idx = 0
	for i in range(11):
		for j in range(19):
			# 每个方块取 4*4 个像素点
			ptn = [0 for j in range(16)]
			is_ptn = False
			for k in range(4):
				for l in range(4):
					ptn[k * 4 + l] = win32gui.GetPixel(hDC, 9 + j * 31 + 13 + l, 180 + i * 35 + 13 + k)
					if ptn[k * 4 + l] != BACK_COLOR:
						is_ptn = True
			# 判断是否为背景色
			if is_ptn is True:
				try:
					idx = ptns.index(ptn)
					board[i][j] = idx + 1
				except ValueError:
					ptns.append(ptn)
					board[i][j] = len(ptns)
	if DEBUG is True:
		print("共计图案种类: " + str(len(ptns)))
		for i in range(len(board)):
			print(board[i])
	return board, len(ptns) # 权宜之计，为准确判断room状态提供线索

def get_status():
	# 按照道理，这个函数中不应该调用 win32gui.SetForegroundWindow(hWnd)
	# 和 win32gui.SetActiveWindow(hWnd) 这两个函数。因为函数名中的get
	# 暗示这个函数是没有副作用的
	# 但是考虑到我们希望room窗口存在即在最前，若room窗口不存在则lobby应该
	# 在最前。从这个角度看，这个函数中的行为又是没有问题的。
	# 但总归这样的设计是不利于未来改变/拓展的，目前先这么用吧。
	if win32gui.FindWindow(None, "QQ游戏 - 连连看角色版") != 0:
		hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
		win32gui.SetForegroundWindow(hWnd)
		win32gui.SetActiveWindow(hWnd)
		hDC = win32gui.GetWindowDC(hWnd)
		while True:
			try:
				if win32gui.GetPixel(hDC, 10, 10) != RGB2Int(0xFF, 0xFF, 0xFF):
					break
			except:
				print("In get_status wait for 1 second...")
			time.sleep(1) # 有时会抽风，此时等待图像恢复
		# 判断右上角星球图案像素是否存在来判断是否在房间中
		if win32gui.GetPixel(hDC, 560, 74) == RGB2Int(144, 152, 72):
			return GameState.GS_INROOM
		# 判断右下角方框边缘像素是否存在来判断是否在游戏中			
		elif win32gui.GetPixel(hDC, 605, 588) == RGB2Int(24, 52, 80):
			return GameState.GS_INGAME
		elif win32gui.GetPixel(hDC, 200, 315) == RGB2Int(0xF0, 0xF4, 0x00):
			return GameState.GS_OVER
		else:
			return GameState.GS_UNKNOWN
	elif get_lobby_hWnd() != 0:
		hWnd = get_lobby_hWnd()
		win32gui.SetForegroundWindow(hWnd)
		win32gui.SetActiveWindow(hWnd)
		return GameState.GS_INLOBBY
	else:
		return GameState.GS_UNKNOWN

def debug():
	print("In debug util.py")
	for_debug()


def for_debug():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	hDC = win32gui.GetWindowDC(hWnd)

	print(Int2RGB(win32gui.GetPixel(hDC, 605, 588)))
	print(get_status())
	win32gui.ReleaseDC(hWnd, hDC)

# def enumDialogHandler(hWnd, lParam):
# 	if win32gui.GetWindowText(hWnd) == "提示信息":
# 		print(win32gui.GetWindowText(hWnd))
# 		print(hWnd)

# def show_dialog_hWnd():
# 	# 在enumHandler中设置了g_lobby_hWnd作为返回值
# 	win32gui.EnumWindows(enumDialogHandler, None)	


if __name__ == '__main__':
	debug()