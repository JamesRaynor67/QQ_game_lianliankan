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
from util import get_lobby_hWnd
from util import get_status
from util import GameState
from solve import solve_game_by_brute_force

def debug():
	print("In debug")
	print(get_status())
	exit_room()



def main():
	# 这个状态机实际上不健壮，万一出现强制前置弹窗等意外状态，程序即陷入错误
	status = GameState.GS_INLOBBY
	waitting_time = 0
	while True:
		if status == GameState.GS_INLOBBY:
			enter_room_from_lobby()
		elif status == GameState.GS_INROOM:
			if waitting_time == 0:
				click_start()
				waitting_time = 1
			elif waitting_time < 30:
				time.sleep(1)
				waitting_time += 1
				print("等待{}秒...".format(waitting_time))
			else:
				exit_room()
		elif status == GameState.GS_INGAME:
			print("准备开始游戏")
			time.sleep(2) # 一开始方块没有出现，等待两秒			
			solve_game_by_brute_force()
			time.sleep(6)
			exit_room()

		pre_status = status
		status = get_status()
		print("现在状态：{}".format(status))
		# 退出room内等待状态后清零计时
		if pre_status == GameState.GS_INROOM and status != GameState.GS_INROOM:
			waitting_time = 0
		# 遇到未知情况时尝试重新恢复窗口焦点恢复运行，无法保证必然有效
		if status == GameState.GS_UNKNOWN:
			hWnd = win32gui.FindWindow(None, "QQ游戏 - 连连看角色版")
			if hWnd == 0:
				hWnd = get_lobby_hWnd()
				assert hWnd != 0
				win32gui.SetForegroundWindow(hWnd)
				win32gui.SetActiveWindow(hWnd)
				status = GameState.GS_INLOBBY
				continue
			else:
				win32gui.SetForegroundWindow(hWnd)
				win32gui.SetActiveWindow(hWnd)
				status = GameState.GS_INROOM

if __name__ == '__main__':
	main()