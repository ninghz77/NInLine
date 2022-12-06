import numpy as np
import math


class ScorerBase:

  def __init__(self, grids, m, player):
    self.name = "ScorerBase"
    self.author = "common"
    self.player = player
    self.opponent = 2 if player == 1 else 1
    self.grids = grids
    self.m = m
    self.max_num = 10e6

  # return (i, j), score
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

  def opponent_player(self, player):
    if player == 0:
      return 0
    return 2 if player == 1 else 1


class RuleBasedScorerBase(ScorerBase):

  def __init__(self, grids, m, player):
    super(RuleBasedScorerBase, self).__init__(grids, m, player)
    self.name = "RuleBasedScorerBase"
    self.author = "common"
    
  def prune_grids(self):
    sz = self.grids.shape
    t = int(np.ceil(self.m / 2))
    pruned_grids = []
    for i in range(sz[0]):
      for j in range(sz[1]):
        if self.grids[i, j] != 0:
          continue
        u = max(0, i - t + 1)
        d = min(sz[0], i + t)
        l = max(0, j - t + 1)
        r = min(sz[1], j + t)
        block = self.grids[u:d, l:r]
        if np.any(block):
          pruned_grids.append((i, j))
    return pruned_grids
