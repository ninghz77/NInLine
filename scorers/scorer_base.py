import numpy as np
import math


class ScorerBase:

  def __init__(self, grids, m, player):
    self.name = "ScorerBase"
    self.author = "ninghz"
    self.player = player
    self.opponent = 2 if player == 1 else 1
    self.grids = grids
    self.m = m
    self.max_num = 10e6

  def best_grid(self):
    pass

  def init_grid(self):
    sz = self.grids.shape
    return math.floor(sz[0] / 2), math.floor(sz[1] / 2)

  def rand_init_grid(self):
    sz = self.grids.shape
    i = np.random.randint(low=self.m - 1, high=sz[0] - self.m)
    j = np.random.randint(low=self.m - 1, high=sz[1] - self.m)
    return i, j


class StupidScorer(ScorerBase):

  def __init__(self, grids, m, player):
    super(StupidScorer, self).__init__(grids, m, player)
    self.name = "StupidScorer"
    self.author = "ninghz"

  def best_grid(self):
    sz = self.grids.shape

    for i in range(sz[0]):
      for j in range(sz[1]):
        if self.grids[i, j] == 0:
          return i, j

    return -1, -1


class RandomScorer(ScorerBase):

  def __init__(self, grids, m, player):
    super(RandomScorer, self).__init__(grids, m, player)
    self.name = "RandomScorer"
    self.author = "ninghz"

  def best_grid(self):
    sz = self.grids.shape

    valid_grids = []
    for i in range(sz[0]):
      for j in range(sz[1]):
        if self.grids[i, j] == 0:
          valid_grids.append((i, j))

    n = np.random.randint(len(valid_grids))

    return valid_grids[n]
