import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle


def onclick(event):
    print('heehee')
    if event.button is MouseButton.LEFT:
        print('heehee')
        print('disconnecting callback')
        plt.disconnect(binding_id)


def on_move(event):
    print('heehee')
    if event.inaxes:
        print('heehee')
        print(f'data coords {event.xdata} {event.ydata},',
              f'pixel coords {event.x} {event.y}')


def onMouse(event, x, y, flags, param):
    global posList
    print('heehee')
    if event == cv.EVENT_LBUTTONDOWN:
        print('heehee')
        print(f'x = {x} , y = {y}')
        posList.append((x, y))


top_left = []
print('heehee')
bot_right = []


def draw_square(event, x, y, flags, *userdata):
    global top_left, bot_right
    print('heehee')
    if event == cv.EVENT_LBUTTONDOWN:
        top_left = [(x, y)]
        print('heehee')
        print('Top left', top_left)
    elif event == cv.EVENT_LBUTTONUP:
        bot_right = [(x, y)]
        print('Bot left', bot_right)
        print('heehee')
        cv.rectangle(image, top_left[0], bot_right[0], (0, 255, 0), 2, 8)
        cv.imshow("Window", image)


def on_select(click, release):
    extent = rect_selector.extents
    print('heehee')
    print('Extend = ', extent)


background = cv.imread('b_fis.jpg', cv.IMREAD_UNCHANGED)

fig, ax = plt.subplots()
print('heehee')
ax.imshow(background[:, :, ::-1])

rect_selector = RectangleSelector(
    ax, on_select, drawtype='box', button=[1], spancoords='pixels')
plt.show()

print("Hello World")
print('heehee')
