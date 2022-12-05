import numpy as np
from scorers.scorer_base import ScorerBase


class HalfLineScorer2(ScorerBase):

  def __init__(self, grids, m, player):
    super(HalfLineScorer2, self).__init__(grids, m, player)
    self.name = "HalfLineScorer2"
    self.author = "ninghz"
    self.base_score = 10

  def init_grid(self):
    return self.rand_init_grid()

  def best_grid(self):
    sz = self.grids.shape
    max_score = -1
    max_grid = (-1, -1)
    for i in range(sz[0]):
      for j in range(sz[1]):
        if self.grids[i, j] != 0:
          continue
        score = self.score_half_line_at_grid(i, j)
        if max_score < score:
          max_score = score
          max_grid = (i, j)
    return max_grid

  def score_half_line_at_grid(self, i, j):
    sz = self.grids.shape
    max_len = self.m + 1
    score = 0

    # column down
    n = min(max_len, sz[0] - i)
    hl = self.grids[i:i + n, j]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # column up
    n = min(max_len, i + 1)
    hl = self.grids[i - n + 1:i + 1, j][::-1]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # row right
    n = min(max_len, sz[0] - j)
    hl = self.grids[i, j:j + n]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # row left
    n = min(max_len, j + 1)
    hl = self.grids[i, j - n + 1:j + 1][::-1]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # down right
    n = min(max_len, sz[0] - i, sz[1] - j)
    hl = [self.grids[i + k, j + k] for k in range(n)]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # down left
    n = min(max_len, sz[0] - i, j + 1)
    hl = [self.grids[i + k, j - k] for k in range(n)]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # up right
    n = min(max_len, i + 1, sz[1] - j)
    hl = [self.grids[i - k, j + k] for k in range(n)]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    # up left
    n = min(max_len, i + 1, j + 1)
    hl = [self.grids[i - k, j - k] for k in range(n)]
    hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
    score += self.score_half_line(hl)

    return score

  def score_half_line(self, half_line):
    l = len(half_line)
    assert l == self.m + 1
    score = 0

    # check the neighboring player steps
    for i in range(1, self.m + 1):
      if self.player == half_line[i]:
        score += i * self.base_score
      else:
        break

    # player win
    if i >= self.m:
      score += self.max_num

    # check the end of the neighbor
    for j in range(i, min(i + 2, self.m)):
      if half_line[j] == 0:
        score += (j - i + 1) * self.base_score

    # check the neighboring opponent steps
    for i in range(1, self.m + 1):
      if self.opponent == half_line[i]:
        score += i * self.base_score * 0.9
      else:
        break

    # opponent might win
    if i >= self.m:
      score += self.max_num / 2

    # check the end of the neighbor
    if i > 1:
      for j in range(i, min(i + 2, self.m)):
        if half_line[j] == 0:
          score += (j - i + 1) * self.base_score * 0.9 / 2

    return score
