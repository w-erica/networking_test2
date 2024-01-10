class Player():
    def __init__(self, name):
        self.name = name
        self.move = 'n'
        self.hasGone = False
        self.score = 0
        self.roundOn = 0
        self.notupdated = True

    def getName(self):
        return self.name

    def __str__(self):
        return "Player Named " + self.name

    def resetMove(self):
        self.move = 'NO_MOVE'
        self.hasGone = False

    def performMove(self, move_done):
        self.hasGone = True
        self.move = move_done # assuming valid move lol

    def addPoint(self):
        self.score += 1
