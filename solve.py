import win32api
import win32con
import win32gui
import time
import random
import matplotlib.pyplot as plt
import numpy as np
import math
from util import GameState
from util import get_status
from util import RGB2Int
from util import click
from util import scan_game_board

BURTE_FORCE_GAME_SPEED = 0.1
GRACE_GAME_SPEED_CORRECTOR = 1

def click_piece(x, y, speed_corrector):
	hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")	
	win32gui.SetForegroundWindow(hWnd)
	win32gui.SetActiveWindow(hWnd)
	transferred_x, transferred_y = 9 + x * 31 + 13, 180 + y * 35 + 13
	lParam = win32api.MAKELONG(transferred_x, transferred_y)
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, 0, lParam)
	win32gui.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, lParam)
	time.sleep(BURTE_FORCE_GAME_SPEED + random.random() * speed_corrector)

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
						piece_num = 11*19 - sum(row.count(0) for row in board)
						# 当piece_num>100时,其实程序的效率可能很低，应该加快尝试速度
						speed_corrector = 0
						if piece_num > 100:
							speed_corrector = -0.8 * BURTE_FORCE_GAME_SPEED
						elif piece_num > 40:
							speed_corrector = ((piece_num - 40)*(piece_num - 100) / -2700) - (0.8 * BURTE_FORCE_GAME_SPEED)
						else:
							speed_corrector = 0.4 # 后期适当降速
						click_piece(pos_x[first], pos_y[first], speed_corrector)
						click_piece(pos_x[second], pos_y[second], speed_corrector)
				
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
		board, _ = scan_game_board()
		solve_at_least_one_pair(board)
		# 设置sleep(1)可能会遇到重排等情况导致new_board出现暂时性错误
		# 但是这种情况下多重复while循环几次即可
		time.sleep(1)
		if get_status() != GameState.GS_INGAME:
			break
		new_board, _ = scan_game_board()
		if if_all_zeros(new_board):
			print("全部方块已被消除完毕")
			print(new_board)
			break
		if board == new_board:
			print("无解，需要进行重排")
			resort()
			time.sleep(8)

def search(board, visited, i, j, pre_direction, conner_count, target_i, target_j):
	if i < 0 or i > 10 or j < 0 or j > 18:
		return False, -1, -1
	if visited[i][j] is True or conner_count > 2 or (board[i][j] != board[target_i][target_j] and board[i][j] != 0):
		return False, -1, -1
	# 先确认是否i,j,conner_count合法再确认是否配对。
	# 注意最开始进入函数时不能立刻返回方块与自身配对。
	if board[i][j] == board[target_i][target_j] and (i != target_i or j != target_j):
		return True, i, j

	visited[i][j] = True
	# -1 first point; 0 up; 1 down; 2 left; 3 right
	if pre_direction == -1:
		solved_one, pair_i, pair_j = search(board, visited, i-1, j, 0, conner_count, target_i, target_j)
		if solved_one is True:
			return solved_one, pair_i, pair_j
		solved_one, pair_i, pair_j = search(board, visited, i+1, j, 1, conner_count, target_i, target_j)
		if solved_one is True:
			return solved_one, pair_i, pair_j
		solved_one, pair_i, pair_j = search(board, visited, i, j-1, 2, conner_count, target_i, target_j)
		if solved_one is True:
			return solved_one, pair_i, pair_j
		solved_one, pair_i, pair_j = search(board, visited, i, j+1, 3, conner_count, target_i, target_j)
		if solved_one is True:
			return solved_one, pair_i, pair_j
	else:
		if pre_direction == 0:
			solved_one, pair_i, pair_j = search(board, visited, i-1, j, 0, conner_count, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		else:
			solved_one, pair_i, pair_j = search(board, visited, i-1, j, 0, conner_count+1, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		if pre_direction == 1:
			solved_one, pair_i, pair_j = search(board, visited, i+1, j, 1, conner_count, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		else:
			solved_one, pair_i, pair_j = search(board, visited, i+1, j, 1, conner_count+1, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		if pre_direction == 2:
			solved_one, pair_i, pair_j = search(board, visited, i, j-1, 2, conner_count, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		else:
			solved_one, pair_i, pair_j = search(board, visited, i, j-1, 2, conner_count+1, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		if pre_direction == 3:
			solved_one, pair_i, pair_j = search(board, visited, i, j+1, 3, conner_count, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
		else:
			solved_one, pair_i, pair_j = search(board, visited, i, j+1, 3, conner_count+1, target_i, target_j)
			if solved_one is True:
				return solved_one, pair_i, pair_j
	visited[i][j] = False
	return False, -1, -1

def solve_one_pair_with_grace(board):
	for i in range(len(board)):
		for j in range(len(board[0])):
			if board[i][j] != 0:
				# 开始搜索棋盘进行尝试消除
				visited = [[False for j in range(19)] for i in range(11)]
				pre_direction = -1 # -1 first point, 0 up, 1 down, 2 left, 3 right
				conner_count = 0
				solved_one, pair_i, pair_j = search(board, visited, i, j, pre_direction, conner_count, i, j)
				if solved_one is True:
					piece_num = 11*19 - sum(row.count(0) for row in board)
					factor = max(1.2, 3.0*math.cos((piece_num-160)/(160/(math.pi/2))))
					click_piece(j, i, GRACE_GAME_SPEED_CORRECTOR * factor * random.random())
					click_piece(pair_j, pair_i, GRACE_GAME_SPEED_CORRECTOR * factor * random.random())
					board[i][j], board[pair_i][pair_j] = 0, 0 # 消去的方块置零
					return True
	return False


def solve_game_with_grace():
	board, _ = scan_game_board()
	check_status_ticker = 1
	while True:
		solved_one = solve_one_pair_with_grace(board)
		if if_all_zeros(board):
			print("全部方块已被消除完毕")
			break
		elif solved_one is False:
			for row in board:
				print(row)
			print("无解，需要重排列")
			resort()
			time.sleep(8) #需要等待提示文字消失，或者干脆让这盘输掉比较好？
			board, _ = scan_game_board()
		elif check_status_ticker % 20 == 0:
			status = get_status()
			if status != GameState.GS_INGAME:
				print("游戏中出现未知问题，现状态为{}".format(status))
				break
		else:
			check_status_ticker += 1

def debug():
	solve_game_with_grace()

if __name__ == '__main__':
	debug()