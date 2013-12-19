
import sys, select  # for timing out input


'''
This is the overall idea of the game's main logic:

stack = []  # last value is the top of the stack

while not gameOver:
    if stack is empty:
        stack = [ nextEvent() ]

    # stack now has at least one element
    top = stack[-1]
    imminent(top)   # this may modify the stack
    if stack and stack[-1] == top:  # nothing else wants to precede us
        top.apply() # this may modify gameOver
'''


def imminent(event):
    # see whether there are any cards that want to be used here
    pass

def stackAppend(event):
    global stack
    stack.append(event)

# ====== Events ======

class Event(object):
    def apply(self):
        pass

class GameStarted(Event):
    pass

class TurnStart(Event):
    def __init__(self, player):
        self.player = player

    def apply(self):
        global currentPlayer
        currentPlayer = self.player
        print 'It is now {0}s turn.'.format(self.player)

class TurnEnd(Event):
    def __init__(self, player):
        self.player = player

    def apply(self):
        global currentPlayer
        currentPlayer = None

class PlayerTimeOut(Event):
    def __init__(self, player):
        self.player = player

    def apply(self):
        print str(self.player) + ' timed out.'

class PlayerWin(Event):
    def __init__(self, player):
        self.player = player

    def apply(self):
        global winner
        winner = self.player
        stackAppend(GameOver()) # That's right, we don't even directly set it here

class PlayerDrawCard(Event):
    def __init__(self, player):
        self.player = player

    def apply(self):
        pass # TODO: cards

class UnitNoHealth(Event):
    def __init__(self, unit):
        self.unit = unit

    def apply(self):
        stackAppend(UnitDeath(self.unit))

class UnitTakeDamadge(Event):
    def __init__(self, *args):
        self.unit, self.damadge = args

    def apply(self):
        stackAppend(UnitHealthChanged(self.unit, -self.damadge))

class UnitHealthChanged(Event):
    def __init__(self, *args):
        self.unit, self.change = args

    def apply(self):
        self.unit.health += self.change
        if self.unit.health <= 0:
            self.unit.onNoHealth()

class UnitNoHealth(Event):
    def __init__(self, unit):
        self.unit = unit

    def apply(self):
        self.unit.die()

class GameOver(Event):
    def apply(self):
        global gameOver
        gameOver = True
        print 'game over man, game over!'

# ====== Units ======

# A unit is anything that has health and dies when it's health goes to, or below zero
class Unit(object):
    def __init__(self):
        self.health = 0

    def onNoHealth(self):
        stackAppend(UnitNoHealth(self))

    def die(self):
        print str(self) + ' died.'
        pass

class Player(Unit):
    def __init__(self, name):
        self.name = name
        self.health = 30

    def __str__(self):
        return '{0}(health:{1})'.format(self.name, self.health)

    def die(self):
        stackAppend(GameOver())

# returns an Event within a finite time
def playerControl(player):
    timeout = 10
    print "You have {0} seconds to answer!".format(timeout)

    # TODO: allow for multiple choices
    # select allows for a timout
    # stackoverflow.com/questions/1335507/
    inputStreams, ignored, ignored2 = select.select([sys.stdin], [], [], timeout)

    if (inputStreams):
        playerInput = sys.stdin.readline()
        print "echo: ", playerInput
        # TODO: actually use the playerInput
    else:
        yield PlayerTimeOut(player)

# a infinite iterator returning Events in finite time
def makeGameEvents():
    global gameOver, players

    yield GameStarted()
    while True:
        for player in players:
            yield TurnStart(player)
            yield UnitTakeDamadge(player, 10)
            yield PlayerDrawCard(player)
            for event in playerControl(player):
                yield event
            yield TurnEnd(player)


# global variables
stack = []
currentPlayer = None
winner = None
gameEvents = makeGameEvents()
gameOver = False
players = [ Player('Player 1'), Player('Player 2')]

while not gameOver:
    # safeguard for cards interrupting each other
    if len(stack) > 9000:
        stack = []
        print 'the stack is too large. moving on to the next event'

    if not stack:
        stack = [ gameEvents.next() ]


    # stack now has at least one element
    top = stack[-1]
    # print 'processing event: ' + str(top)
    imminent(top)   # this may modify the stack
    if stack and stack[-1] == top:  # nothing else wants to precede us
        stack.pop()
        top.apply() # this may modify gameOver

print str(winner) + ' wins!'
