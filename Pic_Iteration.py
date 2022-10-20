import os
import cv2 as cv
import numpy as np
import pandas as pd
import json


def resize(frame, scale=0.75):
    # print(f'this is shape[0] (tinggi) :{frame.shape[0]} ')
    # print(f'this is shape[1] (tinggi) :{frame.shape[1]} ')
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimension = (width, height)
    return cv.resize(frame, dimension, interpolation=cv.INTER_AREA)


def add_transparent_image(background, foreground, x_offset=None, y_offset=None):
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_channels == 3, f'background image should have exactly 3 channels (RGB). found:{bg_channels}'
    assert fg_channels == 4, f'foreground image should have exactly 4 channels (RGBA). found:{fg_channels}'

    # Posisi secara default 'center'
    if x_offset is None: x_offset = (bg_w - fg_w) // 2
    if y_offset is None: y_offset = (bg_h - fg_h) // 2

    w = min(fg_w, bg_w, fg_w + x_offset, bg_w - x_offset)
    h = min(fg_h, bg_h, fg_h + y_offset, bg_h - y_offset)

    if w < 1 or h < 1: return

    # cliping foreground and background images kepada daerah yang ingin disatukan
    bg_x = max(0, x_offset)
    bg_y = max(0, y_offset)
    fg_x = max(0, x_offset * -1)
    fg_y = max(0, y_offset * -1)
    foreground = foreground[fg_y:fg_y + h, fg_x:fg_x + w]
    background_subsection = background[bg_y:bg_y + h, bg_x:bg_x + w]

    # memisahkan channel alfa dari foto .png dan menormalisasikannya
    foreground_colors = foreground[:, :, :3]
    alpha_channel = foreground[:, :, 3] / 255  # 0-255 => 0.0-1.0

    # membuat massk dari channel alpha
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # menggabungkan overlay dengan mask
    composite = background_subsection * (1 - alpha_mask) + foreground_colors * alpha_mask

    # mengganti bagian background dengan gambar overlay
    background[bg_y:bg_y + h, bg_x:bg_x + w] = composite

directory = os.getcwd() + '\photo'
list_dir = os.listdir(directory)
backround_dir = directory+'\desain_ktm'


background_fis = cv.imread(backround_dir+'\s1Fisika.jpg')
background_tb = cv.imread(backround_dir+'\s1TB.jpg')


# pos = [round(x) for x in [125.04864325999984, 393.0595408797299, 263.73002444453533, 878.2347153372391]]
# pos_min = (pos[0], pos[2])
# pos_max = (pos[1], pos[3])
start_point = (179, 290)
end_point = (634,877)


i = 0
for files in list_dir:
    if files.endswith(".JPG"):

        dir = os.path.join(directory, files)
        img = cv.imread(dir)
        # img = resize(img, scale=0.12)

        lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)
        a_channel = lab[:, :, 1]
        _, thresh = cv.threshold(a_channel, 127, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        masked = cv.bitwise_and(img, img, mask=thresh)
        # new_image = img - masked

        image = masked.copy()
        # Hapus bagian hitam yang tidak diperlukan
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        black_filter = gray[np.any(gray != 0, axis=-1)]

        # Menyesuaikan dimensi filter dengan gambar asli
        height = image.shape[0] - black_filter.shape[0]
        width = image.shape[1] - black_filter.shape[1]
        crop = image[height:, width:]

        # Transparasi Background gambar
        _, alpha = cv.threshold(black_filter, 0, 255, cv.THRESH_BINARY)
        b, g, r = cv.split(crop)
        rgba = [b, g, r, alpha]
        transparent = cv.merge(rgba, 4)

        overlay = transparent.copy()

        # Optimalisassi ukuran gambar
        h = end_point[1] - start_point[1]
        w = end_point[0] - start_point[0]
        background = background_fis.copy()
        origin_h, origin_w = background[start_point[1]:start_point[1] + h, start_point[0]:start_point[0] + w].shape[:2]

        origin_ratio = origin_w / origin_h
        design_height, design_width = list(overlay.shape[:2])
        design_ratio = design_width / design_height

        if origin_w * design_height > design_width * origin_h:
            design_height = (design_width * origin_h) / origin_w
        else:
            design_width = (design_height * origin_w) / origin_h

        still_large = True
        while still_large:
            if origin_h + 35 < design_height:
                overlay = cv.resize(overlay, (int(design_width), int(design_height * 0.9)), interpolation=cv.INTER_AREA)
            elif origin_w + 35 < design_width:
                overlay = cv.resize(overlay, (int(design_width * 0.9), int(design_height)), interpolation=cv.INTER_AREA)
            else:
                still_large = False
            design_height, design_width = overlay.shape[:2]

        bg_h, bg_w, bg_channels = background.shape
        fg_h, fg_w, fg_channels = overlay.shape

        x_offset = (bg_w - fg_w) // 2
        y_offset = (bg_h - fg_h) // 2

        # Edge Smoothing
        height, width = overlay.shape[:2]
        color = overlay[:, :, :3]
        alpha_mask = overlay[:, :, 3]

        blur_alpha = cv.GaussianBlur(alpha_mask, ksize=None, sigmaX=2)
        overlay = np.dstack([color, blur_alpha])

        # Blend to Background
        bottom_off = img.shape[0] - h
        # Menyesuaikan posisi gambar
        position = True
        while position:
            range_y = y_offset + h + 8
            range_x = x_offset + w + 8
            if range_y < end_point[1]:
                y_offset += 1
            elif range_x < end_point[0]:
                x_offset += 1
            else:
                #Fisika
                back_fis = background_fis.copy()
                add_transparent_image(back_fis, overlay, x_offset, y_offset)
                cv.imwrite(os.path.join(directory + '\hasil\Fisika', files), back_fis)

                # Teknik Biomedis
                back_tb = background_tb.copy()
                add_transparent_image(back_tb, overlay, x_offset, y_offset)
                cv.imwrite(os.path.join(directory + '\hasil\TB', files), back_tb)

                position = False
        i += 1
        print(f' [Foto ke:{i} ,nama:{files}, status:Sukses]')