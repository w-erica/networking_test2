from player import Player


class GameWrapper:
    def __init__(self):
        """ Wrap a round, to enable multiple games/rounds with one connection """
        self.round = Round()  # the game being wrapped
        self.round.until = 3  # set up "goal" of each game
        self.roundNum = 0  # this is not actually used
        self.roundScores = [0, 0]
        self.names = [None, None]  # names of each player
        self.agree_continue = [None, None]  # whether each player has agreed to another round
        self.connected = [False, False]
        self.bothConnectedLater = True # starts off true bc neither are connected to start
        self.stage = -1

    def set_new_round(self):
        """ Set up new round (after the first round) """
        # update scores from previous round (no display on client side but this is for fun I guess)
        self.roundScores[self.round.winner] += 1
        # set up new round
        self.round = Round()
        self.round.until = 3
        self.roundNum += 1
        return

    # handlers to update things within each game stages (the other one is update_round (within the round thing..))
    def update_player_name(self, name: str, p_idx: int) -> None:
        """ What it says on the tin.
        :param name: desired player name
        :param p_idx: player index of the player to change the name of"""
        self.round.players[p_idx] = Player(name)
        self.round.names[p_idx] = name
        self.names[p_idx] = name
        for i in self.names:
            if i is None:
                return
        self.stage = 0
        print("stage 1 (name) finished, stage 0 (game round) begun")

    def update_connected(self, connect: bool, player_idx: int):
        self.connected[player_idx] = connect
        for i in self.connected:
            if not i:
                return
        self.bothConnectedLater = True
        self.stage = 1  # move to name stage

    def update_continue(self, agreement: str, player_idx: int):
        if agreement not in ["y", "n"]:
            print("wrong agreement input: ", agreement)
            return
        self.agree_continue[player_idx] = (agreement == "y")
        for i in self.agree_continue:
            if not i:
                return
            if i == "n":
                self.bothConnectedLater = False
                print("setting self both connected later to false")
                return
        self.stage = 0
        self.agree_continue = [None, None]
        self.set_new_round()

    # gets game status to send to client
    def get_game_status_for_player(self, player_idx):
        """ What it says on the tin.
        :param player_idx: index of the player """
        opp_idx = 1 - player_idx
        stage_info = None
        # print("current game stage: ", self.stage) # this is for debugging
        if self.stage == 0:  # round playing stage
            stage_info = self.round.get_round_status_for_player(player_idx)
        elif self.stage == 1:  # name setup stage
            stage_info = ((self.names[player_idx] is not None), (self.names[opp_idx] is not None))
        elif self.stage == -1:
            stage_info = (self.connected[player_idx], self.connected[opp_idx])
        elif self.stage == 2:
            stage_info = (self.agree_continue[player_idx], self.agree_continue[opp_idx])
        return self.stage, stage_info, self.bothConnectedLater


class Round:
    def __init__(self):
        """ Execute logic of rock paper scissors game """
        self.players = [Player(None), Player(None)]  # player objects
        self.names = [None, None]  # names of players
        self.hasEnded = False  # whether the game has ended
        self.bothGone = True  # whether both players have gone (i suspect this is not used)
        self.until = -1  # goal of the game (to be set later)
        self.winner = -1  # winner of the game
        self.trick = 0  # how many tricks are done (this is important)
        self.scores = [0, 0]
        self.notUpdated = [True, True]  # whether each player has not been informed of a change in the game
        self.oldMoves = [None, None]  # for use in printing - old moves of a previous round
        self.stage = 0  # which stage the game is in (i.e. name stage, or playing the game stage for now)

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
        self.trick += 1

    def get_round_status_for_player(self, p_idx: int) -> tuple:  # wonder if I should make a type for game status
        """ What it says on the tin.
        :param p_idx: the player index to get information for
        :returns: long tuple. 0: whether the game has changed from the last update to this player (kinda broken rn),
            1: current player's move (prev round, for printing purposes), 2: opponent's move (prev round, for printing
            purposes, 3: current player's score, 4: opponent's score, 5: current round (broken-ish but not as much
            as 0), 6: whether the game has ended, 7: whether the winner is the current player, 8: the stage of the game,
            9: current player's name, 10: opponent's name, 11: whether this player has gone,
            12: whether both players have gone"""
        opp_idx = 1 - p_idx
        has_changed = self.notUpdated[p_idx]
        return has_changed, self.oldMoves[p_idx], self.oldMoves[opp_idx], \
            self.scores[p_idx], self.scores[opp_idx], self.trick, self.hasEnded, \
            (self.winner == p_idx), self.stage, self.names[p_idx], self.names[opp_idx], \
            self.players[p_idx].hasGone, self.bothGone


    def mark_updated(self, p_idx: int):
        """ Mark player as updated (with latest information) """
        self.notUpdated[p_idx] = False
        return


    def update_round(self, move: str, p_idx: int) -> None:
        """ Update round based on move done by player
        :param p_idx: Current player index
        :param move: the move done """
        self.players[p_idx].perform_move(move)
        self.bothGone = (self.players[0].hasGone and self.players[1].hasGone)
        if self.bothGone:
            self.play_round()
        self.notUpdated = [True, True]


    def determine_winner(self, move0: str, move1: str) -> int:
        """ Determine winner of a single trick based on 2 moves
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
