import win32api
import win32con
import win32gui
import time
import random

def RGB2Int(red, green, blue):
    return red + green * 256 + blue * 256 * 256

def Int2RGB(rgb):
	red = (rgb >> 16) & 255
	green = (rgb >> 8) & 255
	blue = rgb & 255
	return (red, green, blue)

def click(hWnd, action):
    delay_time = 0.1
    if action == "enterRoom":
        x, y = 650, 200
        delay_time = 3
    elif action == "clickPractice":
        x, y = 650, 200
    elif action == "clickStart":
        x, y = 650, 200
    elif action == "exitRoom": # 点右上角的乂，退出房间
        x, y = 780, 10
    elif action == "resort": # 重排
        x, y = 650, 200        
        delay_time = 8 + random.random() * 3 #等待提示文字消失，否则会影响下一步判断
    else:
        print("Wrong action string input, exiting...")
        exit()
    lParam = win32api.MAKELONG(x, y) 
    win32gui.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, 0, lParam)
    win32gui.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, lParam)
    time.sleep(delay_time)

