import win32gui
import win32api
import time
from util import RGB2Int
from util import Int2RGB
from util import click
from util import display_room_rect
from util import enter_room_from_lobby
from util import click_start
from util import exit_room
from solve import solve_game_by_brute_force
from enum import Enum

class GameState(Enum):
	GS_INGAME = 1 #处在游戏中
	GS_OVER = 2 #游戏超时，等待其他玩家完成消除并结束一场游戏
	GS_INROOM = 3 #在房间里等待游戏开始
	GS_CLOSED = 4 #游戏窗口被关闭（主动关闭或者被踢出房间
	GS_MINIMIZED = 5 #游戏窗口被最小化（无法获取颜色值）
	GS_INLOBBY = 6 # 在游戏大厅中
	GS_UNKNOWN = 7 #未定义状态(这是错误)


def debug():
	print("In debug")
	# display_room_rect(3,3,100,30)
	enter_room_from_lobby()
	# hWnd = win32gui.FindWindow(None, "连连看")

def get_status():
	pass
	return 0

if __name__ == '__main__':
	# 这个状态机实际上不健壮，万一出现强制前置弹窗等意外状态，程序即陷入错误
	status = GameState.GS_INLOBBY
	waitting_time = 0
	while True:
		if status == GameState.GS_INLOBBY:
			enter_room_from_lobby()
		elif status == GameState.GS_INROOM:
			if waitting_time == 0:
				click_start()				
			elif waitting_time < 20:
				time.sleep(1)
				waitting_time += 1
				print("等待{}秒...".format(waitting_time))
			else:
				exit_room()
		elif status == GameState.GS_INGAME:
			solve_game_by_brute_force()
			exit_room()

		pre_status = status
		status = get_status()
		# 退出room内等待状态后清零计时
		if pre_status == GameState.GS_INROOM and status != GameState.GS_INROOM:
			waitting_time = 0
		# 遇到未知情况时尝试重新恢复窗口焦点恢复运行，无法保证必然有效
		if status == GameState.GS_UNKNOWN:
			hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
			if hWnd == 0:
				hWnd = win32gui.FindWindow(None, "连连看")
				assert hWnd != 0
				win32gui.SetForegroundWindow(hWnd)
				win32gui.SetActiveWindow(hWnd)
				status = GameState.GS_INLOBBY
				continue
			else:
				win32gui.SetForegroundWindow(hWnd)
				win32gui.SetActiveWindow(hWnd)
				status = GameState.GS_INROOM