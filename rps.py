from player import Player


class GameWrapper:
    def __init__(self):
        """ Wrap a game, to enable multiple games/rounds with one connection """
        self.game = Game()  # the game being wrapped
        self.game.until = 3  # set up "goal" of the game
        self.gameNum = 0  # this .. i think is not actually used
        self.names = [None, None]  # names of each player
        self.agree = [None, None]  # whether each player has agreed to another round

    def set_new_game(self):
        """ Set up new game (after the first game) """
        self.names = self.game.names
        self.game = Game()
        self.game.until = 3  # until i can figure out a better way
        for i in range(len(self.names)):
            self.game.update_player_name(self.names[i], i)
        return

    def get_wrapper_status_for_player(self, player_idx):
        """ What it says on the tin.
        :param player_idx: index of the player """
        opp_idx = 1 - player_idx
        return self.agree[player_idx], self.agree[opp_idx]


class Game:
    def __init__(self):
        """ Execute logic of rock paper scissors game """
        self.players = [Player(None), Player(None)]  # player objects
        self.names = [None, None]  # names of players
        self.hasEnded = False  # whether the game has ended
        self.bothGone = False  # whether both players have gone (i suspect this is not used)
        self.until = -1  # goal of the game (to be set later)
        self.winner = -1  # winner of the game
        self.round = 0  # how many rounds are done (this is important)
        self.scores = [0, 0]
        self.notUpdated = [True, True]  # whether each player has not been informed of a change in the game
        self.oldMoves = [None, None]  # for use in printing - old moves of a previous round
        self.stage = 0  # which stage the game is in (i.e. name stage, or playing the game stage for now)
        self.untilAgree = [False,
                           False]  # whether these players have agreed on "until" (goal of the game) or not (not used currently)

    def update_player_name(self, name: str,
                           p_idx: int) -> None:  # this has nothing to do with notUpdated. I should rename these variables.
        """ What it says on the tin.
        :param name: desired player name
        :param p_idx: player index of the player to change the name of"""
        self.players[p_idx] = Player(name)
        self.names[p_idx] = name
        for i in self.players:
            if i is None:
                return
        self.stage = 1
        print("stage 0 finished, stage 1 begun")

    def play_round(self) -> None:
        """ Play a round of the game, depending on the existing moves recorded. """
        winner = self.determine_winner(self.players[0].move, self.players[1].move)
        if winner != -1:
            self.players[winner].add_point()
            self.scores[winner] += 1
            if self.scores[winner] == self.until:
                self.hasEnded = True
                self.winner = winner
        self.oldMoves = [self.players[i].move for i in range(2)]
        if not self.hasEnded:
            for i in range(2):
                self.players[i].reset_move()
        self.round += 1

    def get_game_status_for_player(self, p_idx: int) -> tuple:  # wonder if I should make a type for game status
        """ What it says on the tin.
        :param p_idx: the player index to get information for
        :returns: long tuple. 0: whether the game has changed from the last update to this player (kinda broken rn),
            1: current player's move (prev round, for printing purposes), 2: opponent's move (prev round, for printing
            purposes, 3: current player's score, 4: opponent's score, 5: current round (broken-ish but not as much
            as 0), 6: whether the game has ended, 7: whether the winner is the current player, 8: the stage of the game,
            9: current player's name, 10: opponent's name"""
        opp_idx = 1 - p_idx
        has_changed = self.notUpdated[p_idx]
        self.notUpdated[p_idx] = False
        return has_changed, self.oldMoves[p_idx], self.oldMoves[opp_idx], \
            self.scores[p_idx], self.scores[opp_idx], self.round, self.hasEnded, \
            (self.winner == p_idx), self.stage, self.names[p_idx], self.names[opp_idx]

    def update_game(self, p_idx: int, move: str) -> None:
        """ Update game based on move done by player
        :param p_idx: Current player index
        :param move: the move done """
        self.players[p_idx].perform_move(move)
        self.bothGone = (self.players[0].hasGone and self.players[1].hasGone)
        if self.bothGone:
            self.play_round()
        self.notUpdated = [True, True]

    def determine_winner(self, move0: str, move1: str) -> int:
        """ Determine winner based on 2 moves
        :param move0: move done by player 0 (presumably)
        :param move1: move done by player 1
        :returns: the index of the winning player"""
        if move0 == move1:
            return -1
        order = ['r', 'p', 's']
        if (move0 not in order) or (move1 not in order):
            return -1
        move0_idx = order.index(move0)
        move1_idx = order.index(move1)
        if (move0_idx - move1_idx == 1) or (move0_idx - move1_idx == -2):
            return 0
        else:
            return 1
