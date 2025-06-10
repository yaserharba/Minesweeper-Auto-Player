import random

class GamePlayer:
    def __init__(self, board_size, gameController):
        self.gameController = gameController
        self.board_size = board_size
        self.mine_map = self.get_free_mine_map()
        self.chance_map = self.get_free_chance_map()
        

    def get_all_closed_in_the_grid(self, game_state):
        ret = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if not self.mine_map[i][j] and game_state[i][j] == -1:
                    ret.append((i, j))
        return ret
    
    def get_free_mine_map(self):
        ret = []
        for i in range(self.board_size):
            l = []
            for j in range(self.board_size):
                l.append(False)
            ret.append(l)
        return ret
    
    def get_free_chance_map(self):
        ret = []
        for i in range(self.board_size):
            l = []
            for j in range(self.board_size):
                l.append(0.0)
            ret.append(l)
        return ret
    
    def get_closed(self, i, j, game_state):
        cnt = 0
        for ii, jj in self.get_neighbors(i, j):
            if game_state[ii][jj] == -1 and not self.mine_map[ii][jj]:
                cnt += 1
        return cnt
    
    def get_neighbors(self, i, j):
        i_mn = max(i - 1, 0)
        j_mn = max(j - 1, 0)
        i_mx = min(i + 1, self.board_size - 1)
        j_mx = min(j + 1, self.board_size - 1)
        ret = []
        for ii in range(i_mn, i_mx + 1):
            for jj in range(j_mn, j_mx + 1):
                if i != ii or j != jj:
                    ret.append((ii, jj))
        return ret
    
    def get_mine(self, i, j):
        cnt = 0
        for ii, jj in self.get_neighbors(i, j):
            if self.mine_map[ii][jj]:
                cnt += 1
        return cnt
    
    # TODO: faster!! and another way
    def update_chance_map(self, game_state):
        self.chance_map = self.get_free_chance_map()
        for i in range(self.board_size):
            for j in range(self.board_size):
                closed = self.get_closed(i, j, game_state)
                mines = self.get_mine(i, j)
                need_mines = game_state[i][j] - mines
                if game_state[i][j] >= 0 and closed > 0:
                    for ii, jj in self.get_neighbors(i, j):
                        if game_state[ii][jj] == -1:
                            self.chance_map[ii][jj] += need_mines / closed

    def new_bst_click(self, game_state):
        all_closed = self.get_all_closed_in_the_grid(game_state)
        if len(all_closed) == 0:
            return False
        self.update_chance_map(game_state)
        i, j = self.get_best_place_to_pic(all_closed)
        self.gameController.click_at(i, j)
        return True


    # TODO: faster!!
    def get_best_place_to_pic(self, all_closed):
        bst_close = random.choice(all_closed)
        for i, j in all_closed:
            if self.chance_map[bst_close[0]][bst_close[1]] > self.chance_map[i][j]:
                bst_close = (i, j)
        return bst_close
    
    def open_all_closed(self, i, j, game_state):
        do_something = False
        for ii, jj in self.get_neighbors(i, j):
            if game_state[ii][jj] == -1 and not self.mine_map[ii][jj]:
                self.gameController.click_at(ii, jj)
                do_something = True
        return do_something
            
    def make_closed_as_mine(self, i, j, game_state):
        for ii, jj in self.get_neighbors(i, j):
            if game_state[ii][jj] == -1 and not self.mine_map[ii][jj]:
                self.mine_map[ii][jj] = True
                # winsound.Beep(2000, 500)
                # os.system('beep -f 2000 -l 500')
    

    def play_at(self, i, j, game_state):
        if game_state[i][j] > -1:
            closed = self.get_closed(i, j, game_state)
            mines = self.get_mine(i, j)
            if closed + mines == game_state[i][j] and closed > 0:
                # print("m", i, j, game_state[i][j], closed, mines)
                self.make_closed_as_mine(i, j, game_state)
                return True
            elif game_state[i][j] == mines and closed > 0:
                # print("o", i, j, game_state[i][j], closed, mines)
                return self.open_all_closed(i, j, game_state)
        return False
    
    def check_win(self, game_state):
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if game_state[i][j] == 11:
                    return True
        return False
    
    def check_lose(self, game_state):
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if game_state[i][j] == 10:
                    return True
        return False
    
    def make_a_play_step(self):
        # print("game_state")
        game_state = self.gameController.get_game_state()
        # for i in range(self.board_size):
        #     for j in range(self.board_size):
        #         print(int(game_state[i][j]), end="\t")
        #     print()
        win = self.check_win(game_state)
        if win:
            return False, False, True
        lose = self.check_lose(game_state)
        if lose:
            return False, True, False
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.play_at(i, j, game_state):
                    return True, False, False
        return self.new_bst_click(game_state), False, False
    
    def print(self):
        print("mine_map")
        for i in range(self.board_size):
            for j in range(self.board_size):
                print(int(self.mine_map[i][j]), end=" ")
            print()
    
    