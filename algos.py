# file for holding client bot algorithms

from rps import determine_winner


class AlgoWrapper:
    def __init__(self, algo_num: int):
        self.algo_num = algo_num
        self.own_moves = []
        self.opp_moves = []
        self.wins = []
        self.algo_type_dict = [self.algo_type_1, self.algo_type_2]
        self.algo = self.algo_type_dict[self.algo_num] # is this right. what is happening

    def update_moves(self, own_move, opp_move):
        self.own_moves.append(own_move)
        self.opp_moves.append(opp_move)
        #todo: determine winner and update self.wins based on that
    def get_move(self):
        return 'r'

    def algo_type_1(self):
        return 's'

    def algo_type_2(self):
        return 's'
