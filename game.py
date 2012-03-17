import random
import string

from google.appengine.api import memcache


class Game(object):
    def __init__(self, id):
        self._id = id
        self._first_player = None
        self._second_player = None
        self._board = [[0 for y in range(3)]
                       for x in range(3)]
        self._moves_made = 0
        self._winner = 0

    def Id(self):
        return self._id

    def Join(self, player):
        if self._first_player is None:
            self._first_player = '1'
            return 1
        if self._second_player is None:
            self._second_player = '2'
            return 2
        return 0

    def GetOponent(self, player):
        if self._first_player == player:
            return self._second_player
        else:
            return self._first_player

    def Move(self, player, x, y):
        if self._winner:
            return False
        if x < 0 or x > 2 or y < 0 or y > 2:
            return False

        if player == self._first_player:
            player_id = 0
        elif player == self._second_player:
            player_id = 1
        else:
            return False

        if player_id % 2 != self._moves_made % 2:
            return False

        if self._board[x][y]:
            return False

        self._board[x][y] = self._moves_made + 1
        self._moves_made += 1
        self._winner = self._FindWinner()
        return True

    def Winner(self):
        return self._winner

    def _FindWinner(self):
        winner = 0
        for i in range(3):
            winner = winner or (self._AreSame(i, 0, i, 1, i, 2) or
                                self._AreSame(0, i, 1, i, 2, i))
        winner =  (self._AreSame(0, 0, 1, 1, 2, 2) or
                   self._AreSame(0, 2, 1, 1, 2, 0))
        if not winner:
            return 0
        if winner % 2 == 1:
            return 1
        else:
            return 2
        
    
    def _AreSame(self, x1, y1, x2, y2, x3, y3):
        if not self._board[x1][y1] * self._board[x2][y2] * self._board[x3][y3]:
            return False
        if self._board[x1][y1] % 2 != self._board[x2][y2] % 2:
            return False
        if self._board[x1][y1] % 2 != self._board[x3][y3] % 2:
            return False
        return self._board[x1][y1]


def New(id=None):
    if not id:
        id = _GenerateUniqueId(30)
    return Game(id)


def Load(id):
    game = memcache.get(id)
    if not game:
        game = New(id)
    return game


def Save(game):
    memcache.set(game.Id(), game)


def _GenerateUniqueId(length):
    return ''.join(random.choice(string.digits + string.letters)
                   for i in range(length))
