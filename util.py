import win32api
import win32con
import win32gui
import time
import random
import matplotlib.pyplot as plt
import numpy as np

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
		x, y = 270, 152
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
	print("Clicked {} and {}".format(x,y))
	win32api.SetCursorPos((x, y)) # important to make click valide
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

def debug():
	print("In debug util.py")
	colorInt = 16711680 # left red
	# colorInt = 65280 # mid green
	# colorInt = 255 # right blue
	
	print(Int2RGB(colorInt))
	import matplotlib.pyplot as plt
	import numpy as np
	image = np.zeros((10, 10, 3))
	for y in range(10):
		for x in range(10):
			image[y, x] = np.asarray(Int2RGB(colorInt))/255
	print(image.shape)
	plt.imshow(image)
	plt.show()
	print(image)


if __name__ == '__main__':
	debug()