import win32api
import win32con
import win32gui
import time
import random
import matplotlib.pyplot as plt
import numpy as np
from util import GameState
from util import get_status
from util import RGB2Int
from util import click

DEBUG = True
BACK_COLOR = RGB2Int(0x30,0x4C,0x70)
GAME_SPEED = 0.1
GAME_SPEED_VAR = 0

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
	return board

def click_piece(x, y):
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	transferred_x, transferred_y = 9 + x * 31 + 13, 180 + y * 35 + 13
	lParam = win32api.MAKELONG(transferred_x, transferred_y)
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, 0, lParam)
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, lParam)
	time.sleep(GAME_SPEED + random.random() * GAME_SPEED_VAR)

def solve_at_least_one_pair(board):
	# 经过观察，即使积分很高的人消去也很慢，故不考虑效率，选择最简单的穷举法
	# 即点选所有相同的方块试图消去，这样至少可以消去一对（除非已经无解）
	# 这样可能导致消去的效率变化比较大
	# 若想得到稳定解可以考虑进行图的遍历
	# (规则：连接线不多于 3 根直线，就可以成功将对子消除。)
	# 每拐一次弯将深度加一，深度超过2则放弃搜索即可
	tried_ids = []
	for y in range(len(board)):
		for x in range(len(board[0])):
			if board[y][x] != 0 and board[y][x] not in tried_ids:
				# 开始处理一种新图案
				target_id = board[y][x]
				tried_ids.append(target_id)
				pos_x, pos_y = [], []
				# 找到所有此种图案的坐标
				for row_num in range(len(board)):
					indexes = [i for i, ptn_id in enumerate(board[row_num]) if ptn_id == target_id]
					pos_x = pos_x + indexes
					pos_y = pos_y + [row_num for i in range(len(indexes))]
				# 开始尝试组合点击坐标
				assert len(pos_x) == len(pos_y)
				for first in range(len(pos_x)):
					for second in range(first + 1, len(pos_x)):
						# 尝试组合消除
						# print(pos_x[first], pos_y[first], pos_x[second], pos_y[second])						
						assert board[pos_y[first]][pos_x[first]] == board[pos_y[second]][pos_x[second]]
						click_piece(pos_x[first], pos_y[first])
						click_piece(pos_x[second], pos_y[second])
				
def resort():
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	click(hWnd, "resort")

def if_all_zeros(board):
	for row in range(len(board)):
		if any(ele != 0 for ele in board[row]):
			return False
	return True

def solve_game_by_brute_force():
	while True:
		if get_status() != GameState.GS_INGAME:
			break
		board = scan_game_board()
		solve_at_least_one_pair(board)
		time.sleep(8)
		new_board = scan_game_board()
		if if_all_zeros(new_board):
			print("全部方块已被消除完毕")
			print(new_board)
			break
		if board == new_board:
			print("无解，需要进行重排")
			resort()


def debug():
	solve_game_by_brute_force()

if __name__ == '__main__':
	debug()