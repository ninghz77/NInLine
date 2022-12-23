import heapq
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
    hm = math.ceil(self.m/2)
    if sz[0] <= 2 * hm or sz[1] <= 2 * hm:
      return math.floor(sz[0] / 2), math.floor(sz[1] / 2)

    i = np.random.randint(low=hm, high=sz[0] - hm)
    j = np.random.randint(low=hm, high=sz[1] - hm)
    return i, j

  def opponent_player(self, player):
    if player == 0:
      return 0
    return 2 if player == 1 else 1
  
  def is_token(self, grid_val):
    return grid_val == self.player or grid_val == self.opponent

class ScoredGrid:
  def __init__(self, score, grid) -> None:
    self.score = score
    self.grid = grid
    self.win = False

  def __lt__(self, other):
    return self.score > other.score

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

  def top_n_grids(self, n):
    pruned_grids = self.prune_grids()
    gridq = []
    for grid in pruned_grids:
      i, j = grid
      if self.grids[i, j] != 0:
        continue
      scored_grid = self.score_grid(i, j)
      heapq.heappush(gridq, scored_grid)
    top_n = []
    for k in range(min(n, len(gridq))):
        top_n.append(heapq.heappop(gridq))

    return top_n

  # return ScoredGrid
  def score_grid(self, i, j):
    raise "{}.score_grid() NOT implemented.".format(self.name)

  