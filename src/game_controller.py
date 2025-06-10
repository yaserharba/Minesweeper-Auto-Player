import pyautogui
import os
import time
import cv2
import numpy as np

class GameController:
    def __init__(self, board_size, start_x, start_y, grid_side_length):
        self.board_size = board_size
        self.start_x = start_x
        self.start_y = start_y
        self.grid_side_length = grid_side_length

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        return screenshot_cv2[self.start_y:self.start_y + self.grid_side_length, self.start_x:self.start_x + self.grid_side_length]

    @staticmethod
    def max_value_that_repeated_more_than(value_channel):
        histogram = cv2.calcHist([value_channel], [0], None, [256], [0, 256])
        valid_indices = np.where(histogram > 10)[0]
        if len(valid_indices) > 0:
            return int(valid_indices[-1])
        else:
            return None
        
    def get_val_hue_grid(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        ret = []
        for i in range(self.board_size):
            lst = []
            for j in range(self.board_size):
                roi = hsv_image[(i * self.grid_side_length) // self.board_size:((i + 1) * self.grid_side_length) // self.board_size,
                    (j * self.grid_side_length) // self.board_size:((j + 1) * self.grid_side_length) // self.board_size]
                roi_BGR = image[(i * self.grid_side_length) // self.board_size:((i + 1) * self.grid_side_length) // self.board_size,
                    (j * self.grid_side_length) // self.board_size:((j + 1) * self.grid_side_length) // self.board_size]
                # cv2.imwrite(f"rois/{i} {j}.png", roi_BGR)
                hue_channel = roi[:, :, 0]
                saturation_channel = roi[:, :, 1]
                value_channel = roi[:, :, 2]
                saturation_threshold = 50
                high_saturation_mask = (saturation_channel > saturation_threshold)
                num_high_saturation_pixels = np.sum(high_saturation_mask) / (roi.shape[0] * roi.shape[1])
                # v_max_index = GameController.max_value_that_repeated_more_than(value_channel)

                histogram = cv2.calcHist([value_channel], [0], None, [256], [0, 256])
                v_max_index = int(np.argmax(histogram))

                if num_high_saturation_pixels < 0.01:
                    lst.append((v_max_index, None))
                else:
                    hue_values = hue_channel[high_saturation_mask]
                    histogram = cv2.calcHist([hue_values], [0], None, [256], [0, 256])
                    h_max_index = int(np.argmax(histogram))
                    lst.append((v_max_index, h_max_index))
            ret.append(lst)
        return ret
    
    def process_image(self, image):
        val_hue_grid = self.get_val_hue_grid(image)
        ret = []
        mp = {
            104: 1,
            60: 2,
            6: 3,
            126: 4,
            7: 5,
            105: 6,
            23: 7,
            30: 10,
            65: 11
        }
        for i in range(self.board_size):
            lst = []
            for j in range(self.board_size):
                # print(val_hue_grid[i][j], end="\t")
                if val_hue_grid[i][j][1] is None:
                    lst.append(-1 if val_hue_grid[i][j][0] < 200 else 0)
                else:
                    lst.append(mp.get(val_hue_grid[i][j][1], -1))
            ret.append(lst)
            # print()
        return ret

    def get_game_state(self):
        screenshot = self.take_screenshot()
        game_state = self.process_image(screenshot)
        return game_state

    def click_at(self, i, j):
        # winsound.Beep(500, 500)
        # os.system('beep -f 500 -l 500')
        pyautogui.click(self.start_x + (j * self.grid_side_length) // self.board_size + (self.grid_side_length // 32),
                        self.start_y + (i * self.grid_side_length) // self.board_size + (self.grid_side_length // 32))
        pyautogui.moveTo(50, 50)
        # print("click_at", i, j)
        time.sleep(0.1)