from player import Player

class GameWrapper():
    def __init__(self):
        self.game = None
        self.gameNum = 0
        self.players = [None, None]
        self.names = [None, None]
    def setFirstGame(self):
        self.game = Game()
    def setNewGame(self):

class Game():
    def __init__(self):
        self.players = [None, None]
        self.names = [None, None]
        self.hasEnded = False
        self.bothGone = False
        self.until = -1
        self.winner = -1
        self.round = 0
        self.scores = [0, 0]
        self.notUpdated = [True, True]
        self.oldMoves = [None, None]
        self.stage = 0
        self.untilAgree = [False, False] # whether these players have agreed on "until" or not

    def updatePlayer(self, name, playeridx):
        self.players[playeridx] = Player(name)
        self.names[playeridx] = name
        for i in self.players:
            if i is None:
                return
        self.stage = 1
        print("stage 0 finished, stage 1 begun")

    def playARound(self):
        winner = self.determineWinner(self.players[0].move, self.players[1].move)
        if winner != -1:
            self.players[winner].addPoint()
            self.scores[winner] += 1
            if self.scores[winner] == self.until:
                self.hasEnded = True
                self.winner = winner
        self.oldMoves = [self.players[i].move for i in range(2)]
        if not self.hasEnded:
            for i in range(2):
                self.players[i].resetMove()
        self.round += 1

    def getGameStatusForPlayer(self, playerIdx):
        # return whether this has changed from the previous sending
        # each player's current move (self first), each players score (self first), current round #,
        # whether the game is over, whether the indicated player has won
        # note moves are only relevant to the previous round..
        opp_idx = 1 - playerIdx
        has_changed = self.notUpdated[playerIdx]
        self.notUpdated[playerIdx] = False
        return has_changed, self.oldMoves[playerIdx], self.oldMoves[opp_idx], \
            self.scores[playerIdx], self.scores[opp_idx], self.round, self.hasEnded, \
            (self.winner == playerIdx), self.stage, self.names[playerIdx], self.names[opp_idx]

    def updateGame(self, playerIdx, move):
        self.players[playerIdx].performMove(move)
        self.bothGone = (self.players[0].hasGone and self.players[1].hasGone)
        if self.bothGone:
            self.playARound()
        self.notUpdated = [True, True]

    def determineWinner(self, move0, move1):
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
