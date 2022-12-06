import numpy as np
from scorers.scorer_base import ScorerBase

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

    return (-1, -1), 1


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

    return valid_grids[n], 1
