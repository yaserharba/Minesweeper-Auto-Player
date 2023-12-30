import random
import time

import cv2
import pyautogui
import numpy as np
import keyboard
import winsound

grid_side_length = 760

start_x = 1022
start_y = 220

true_color = (0, 0, 255)
false_color = (0, 60, 0)


def take_screenshot():
    global grid_side_length
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_cv2 = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    return screenshot_cv2[start_y:start_y + grid_side_length, start_x:start_x + grid_side_length]


def max_value_that_repeated_more_than(value_channel):
    histogram = cv2.calcHist([value_channel], [0], None, [256], [0, 256])
    valid_indices = np.where(histogram > 10)[0]
    if len(valid_indices) > 0:
        return valid_indices[-1]
    else:
        return None


def process_image(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    ret = []
    for i in range(16):
        lst = []
        for j in range(16):
            lst_size = len(lst)
            roi = hsv_image[(i * grid_side_length) // 16:((i + 1) * grid_side_length) // 16,
                  (j * grid_side_length) // 16:((j + 1) * grid_side_length) // 16]
            hue_channel = roi[:, :, 0]
            saturation_channel = roi[:, :, 1]
            value_channel = roi[:, :, 2]
            saturation_threshold = 100
            high_saturation_mask = (saturation_channel > saturation_threshold)
            num_high_saturation_pixels = np.sum(high_saturation_mask)
            hue_values = hue_channel[high_saturation_mask]
            histogram = cv2.calcHist([hue_values], [0], None, [256], [0, 256])
            max_index = np.argmax(histogram)
            most_repeated_hue = int(max_index)
            if num_high_saturation_pixels > 500:
                if most_repeated_hue == 120:
                    max_index = max_value_that_repeated_more_than(value_channel)
                    if max_index <= 220:
                        lst.append(4)
                    else:
                        lst.append(1)
                elif most_repeated_hue == 0:
                    max_index = max_value_that_repeated_more_than(value_channel)
                    if max_index <= 220:
                        lst.append(5)
                    else:
                        lst.append(3)
                else:
                    lst.append(2)
            else:
                max_index = max_value_that_repeated_more_than(value_channel)
                if max_index <= 220:
                    lst.append(0)
                else:
                    lst.append(-1)
            if len(lst) == lst_size:
                print("cannot read at ", i, j)
        ret.append(lst)
    return ret


def get_neighbors(i, j):
    i_mn = max(i - 1, 0)
    j_mn = max(j - 1, 0)
    i_mx = min(i + 1, 15)
    j_mx = min(j + 1, 15)
    ret = []
    for ii in range(i_mn, i_mx + 1):
        for jj in range(j_mn, j_mx + 1):
            if i != ii or j != jj:
                ret.append((ii, jj))
    return ret


def get_closed(i, j, game_state, mine_map):
    cnt = 0
    for ii, jj in get_neighbors(i, j):
        if game_state[ii][jj] == -1 and not mine_map[ii][jj]:
            cnt += 1
    return cnt


def get_mine(i, j, mine_map):
    cnt = 0
    for ii, jj in get_neighbors(i, j):
        if mine_map[ii][jj]:
            cnt += 1
    return cnt


def get_free_mine_map():
    ret = []
    for i in range(16):
        l = []
        for j in range(16):
            l.append(False)
        ret.append(l)
    return ret


def make_closed_as_mine(i, j, mine_map, game_state):
    for ii, jj in get_neighbors(i, j):
        if game_state[ii][jj] == -1 and not mine_map[ii][jj]:
            mine_map[ii][jj] = True
            winsound.Beep(2000, 500)


def click_at(i, j):
    winsound.Beep(500, 500)
    pyautogui.click(start_x + (j * grid_side_length) // 16 + (grid_side_length // 32),
                    start_y + (i * grid_side_length) // 16 + (grid_side_length // 32))
    pyautogui.moveTo(50, 50)
    time.sleep(1)


def open_all_closed(i, j, game_state, mine_map):
    for ii, jj in get_neighbors(i, j):
        if game_state[ii][jj] == -1 and not mine_map[ii][jj]:
            click_at(ii, jj)
            return True


def play_at(i, j, game_state, mine_map):
    if game_state[i][j] > -1:
        closed = get_closed(i, j, game_state, mine_map)
        mines = get_mine(i, j, mine_map)
        if closed + mines == game_state[i][j] and closed > 0:
            print("m", i, j, game_state[i][j], closed, mines)
            make_closed_as_mine(i, j, mine_map, game_state)
        elif game_state[i][j] == mines and closed > 0:
            print("o", i, j, game_state[i][j], closed, mines)
            return open_all_closed(i, j, game_state, mine_map)
    return False


def make_a_play_step(game_state, mine_map):
    for i in range(0, 16):
        for j in range(0, 16):
            if play_at(i, j, game_state, mine_map):
                return True
    return False


def get_all_closed_in_the_grid(game_state, mine_map):
    ret = []
    for i in range(16):
        for j in range(16):
            if not mine_map[i][j] and game_state[i][j] == -1:
                ret.append((i, j))
    return ret


def make_random_move(game_state, mine_map):
    all_closed = get_all_closed_in_the_grid(game_state, mine_map)
    i, j = random.choice(all_closed)
    click_at(i, j)


def create_image(game_state, mine_map):
    bool_array = np.array(mine_map, dtype=np.uint8)
    image = np.where(bool_array[..., None], np.array(true_color, dtype=np.uint8), np.array(false_color, dtype=np.uint8))
    image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_NEAREST)
    for i in range(16):
        for j in range(16):
            text = str(game_state[i][j]) if game_state[i][j] != -1 else "#"
            position = (j * 32 + 9, i * 32 + 18)
            cv2.putText(image, text, position, cv2.FACE_RECOGNIZER_SF_FR_COSINE, 0.4, (255, 255, 255), 1)
    return image


def get_free_chance_map():
    ret = []
    for i in range(16):
        l = []
        for j in range(16):
            l.append(0.0)
        ret.append(l)
    return ret


def get_chance_map(game_state, mine_map):
    chance_map = get_free_chance_map()
    for i in range(16):
        for j in range(16):
            closed = get_closed(i, j, game_state, mine_map)
            mines = get_mine(i, j, mine_map)
            need_mines = game_state[i][j] - mines
            if game_state[i][j] >= 0 and closed > 0:
                for ii, jj in get_neighbors(i, j):
                    if game_state[ii][jj] == -1:
                        chance_map[ii][jj] += need_mines / closed
    return chance_map


def get_best_place_to_pic(all_closed, chance_map):
    bst_close = random.choice(all_closed)
    for i, j in all_closed:
        if chance_map[bst_close[0]][bst_close[1]] > chance_map[i][j]:
            bst_close = (i, j)
    return bst_close


def new_bst_click(game_state, mine_map):
    all_closed = get_all_closed_in_the_grid(game_state, mine_map)
    chance_map = get_chance_map(game_state, mine_map)
    i, j = get_best_place_to_pic(all_closed, chance_map)
    click_at(i, j)


def main():
    print("Press 's' to start...")

    # Wait for the 's' key to be pressed
    keyboard.wait("s")

    print("Starting...")

    mine_map = get_free_mine_map()
    for game_stapes in range(16 * 16):
        screenshot = take_screenshot()

        # cv2.imshow('Original Screenshot', screenshot)
        # cv2.waitKey(0)
        # exit()

        game_state = process_image(screenshot)
        if not make_a_play_step(game_state, mine_map):
            print("new bst click")
            new_bst_click(game_state, mine_map)
        if keyboard.is_pressed('e'):
            print("pressed e")
            break

        result_image = create_image(game_state, mine_map)
        cv2.imshow('Mine Image', result_image)
        cv2.moveWindow('Mine Image', 100, 100)
        cv2.waitKey(1)

    if game_state == 16 * 16 - 1:
        print("exit loop freely")

    for i in range(16):
        for j in range(16):
            print(int(mine_map[i][j]), end=" ")
        print()

    cv2.imshow('Original Screenshot', screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
