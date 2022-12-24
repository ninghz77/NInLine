import numpy as np
from scorers.scorer_base import RuleBasedScorerBase, ScoredGrid


class HalfLineScorer(RuleBasedScorerBase):

  def __init__(self, grids, m, player):
    super(HalfLineScorer, self).__init__(grids, m, player)
    self.name = "HalfLineScorer"
    self.author = "ninghz"
    self.base_score = 10

  def init_grid(self):
    return self.rand_init_grid()

  def best_grid(self):
    top_grids = self.top_n_grids(1)
    return top_grids[0] if top_grids else ScoredGrid(0, (-1, -1))

  def score_grid(self, i, j):
    sz = self.grids.shape
    max_len = self.m + 1
    scored_grid = ScoredGrid(0, (i, j))

    def score_half_line_wrapper(hl, n):
      hl = np.pad(hl, (0, max_len - n), 'constant', constant_values=(0, -1))
      s, w = self.score_half_line(hl)
      scored_grid.score += s
      scored_grid.win = w

    # column down
    n = min(max_len, sz[0] - i)
    hl = self.grids[i:i + n, j]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # column up
    n = min(max_len, i + 1)
    hl = self.grids[i - n + 1:i + 1, j][::-1]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # row right
    n = min(max_len, sz[0] - j)
    hl = self.grids[i, j:j + n]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # row left
    n = min(max_len, j + 1)
    hl = self.grids[i, j - n + 1:j + 1][::-1]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # down right
    n = min(max_len, sz[0] - i, sz[1] - j)
    hl = [self.grids[i + k, j + k] for k in range(n)]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # down left
    n = min(max_len, sz[0] - i, j + 1)
    hl = [self.grids[i + k, j - k] for k in range(n)]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # up right
    n = min(max_len, i + 1, sz[1] - j)
    hl = [self.grids[i - k, j + k] for k in range(n)]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    # up left
    n = min(max_len, i + 1, j + 1)
    hl = [self.grids[i - k, j - k] for k in range(n)]
    score_half_line_wrapper(hl, n)
    if scored_grid.win: return scored_grid

    return scored_grid

  def score_half_line(self, half_line):
    l = len(half_line)
    assert l == self.m + 1
    score = 0
    win = False

    # check the neighboring player steps
    for i in range(1, self.m + 1):
      if self.player == half_line[i]:
        score += i * self.base_score
      else:
        break

    # player win
    if i >= self.m:
      score += self.max_num
      win = True

    # check the end of the neighbor
    if half_line[i] == 0:
      score += self.base_score / 2

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
    if i > 1 and half_line[i] == 0:
      score += self.base_score * 0.9 / 2

    return score, win
