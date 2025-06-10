import cv2
import numpy as np
import pyautogui
import time
import keyboard
# import winsound
import json

from src.game_controller import GameController
from src.game_player import GamePlayer

pyautogui.FAILSAFE = False

def load_coords_from_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data["x1"], data["y1"], data["x2"], data["y2"]

coords = load_coords_from_json("selected_area.json")

grid_side_length = coords[2]-coords[0]

start_x = coords[0]
start_y = coords[1]

board_size = 20

true_color = (0, 0, 255)
false_color = (0, 60, 0)


def play_game():
    gameController = GameController(board_size, start_x, start_y, grid_side_length)
    player = GamePlayer(board_size, gameController)
    while True:
        can_make_something, lose, win = player.make_a_play_step()
        if win:
            return True, False
        if lose:
            return False, False
        if not can_make_something:
            break
        if keyboard.is_pressed('e'):
            print("pressed e")
            return False, True
    return True, False
    


# def make_random_move(game_state, mine_map):
#     all_closed = get_all_closed_in_the_grid(game_state, mine_map)
#     i, j = random.choice(all_closed)
#     click_at(i, j)


# def create_image(game_state, mine_map):
#     bool_array = np.array(mine_map, dtype=np.uint8)
#     image = np.where(bool_array[..., None], np.array(true_color, dtype=np.uint8), np.array(false_color, dtype=np.uint8))
#     image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_NEAREST)
#     for i in range(board_size):
#         for j in range(board_size):
#             text = str(game_state[i][j]) if game_state[i][j] != -1 else "#"
#             position = (j * 32 + 9, i * 32 + 18)
#             cv2.putText(image, text, position, cv2.FACE_RECOGNIZER_SF_FR_COSINE, 0.4, (255, 255, 255), 1)
#     return image

def main():
    print("Press 's' to start...")

    # Wait for the 's' key to be pressed
    keyboard.wait("s")

    print("Starting...")

    # for game_stapes in range(board_size * board_size):
    while True:
        
        # cv2.imshow('Original Screenshot', screenshot)
        # cv2.waitKey(0)
        # exit()
        win, end = play_game()
        if end:
            break
        elif not win:
            pyautogui.click(1486, 915)
            time.sleep(0.5)
            pyautogui.moveTo(50, 50)
        else:
            print("you win!!")
            break
        # player.print()
            
        # if keyboard.is_pressed('e'):
        #     print("pressed e")
        #     break

        # result_image = create_image(game_state, mine_map)
        # cv2.imshow('Mine Image', result_image)
        # cv2.moveWindow('Mine Image', 100, 100)
        # cv2.waitKey(1)

    # if game_state == board_size * board_size - 1:
    #     print("exit loop freely")

    # cv2.imshow('Original Screenshot', screenshot)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
