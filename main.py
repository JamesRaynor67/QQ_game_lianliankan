import win32gui
import win32api
import time
from util import RGB2Int
from util import Int2RGB
from util import click
from util import display_room_rect
from solve import solve_game_by_brute_force


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
		print("进入游戏房间失败，退出程序")
		exit()

def debug():
	print("In debug")
	# display_room_rect(3,3,100,30)
	enter_room_from_lobby()
	# hWnd = win32gui.FindWindow(None, "连连看")
	
def main():
	solve_game_by_brute_force()

if __name__ == '__main__':
	solve_game_by_brute_force()