import numpy as np
from scorers.scorer_base import RuleBasedScorerBase, ScoredGrid

class Patttern:
  def __init__(self, max_num, base_score, is_self=True) -> None:
    self.max_num = max_num
    self.base_score = base_score
    self.is_self = is_self
    self.opp_weight = 0.5

  def score(self):
    raise "Pattern.score() is not implemented."
  
  def scale_by_opp(self, score):
    return score if self.is_self else score * self.opp_weight

class WinPat(Patttern):
  def score(self):
    return self.scale_by_opp(self.max_num)

class MissingOnePat(Patttern):
  def __init__(self, max_num, base_score, is_self=True, empty_ends=[0, 0]) -> None:
    super(MissingOnePat, self).__init__(max_num, base_score, is_self)
    self.empty_ends = empty_ends
    assert len(empty_ends) == 2
    self.empty_ends = sorted(empty_ends)

  def score(self):
    total_empty_ends = self.empty_ends[0] + self.empty_ends[1]
    if total_empty_ends == 0:
      return 0
    if total_empty_ends >= 1 and not self.is_self:
      return self.max_num / 2

    score = 0
    if self.empty_ends[0] >= 1:
      score = self.max_num / 3
    elif self.empty_ends[1] >= 1:
      score = self.base_score * 50
    return score
    
class MissingTwoPat(Patttern):
  def __init__(self, max_num, base_score, is_self=True, empty_ends=[0, 0]) -> None:
    super(MissingTwoPat, self).__init__(max_num, base_score, is_self)
    self.empty_ends = empty_ends
    assert len(empty_ends) == 2
    self.empty_ends = sorted(empty_ends)

  def score(self):
    total_empty_ends = self.empty_ends[0] + self.empty_ends[1]
    if total_empty_ends < 2:
      return 0
    # one end is not empty or both ends has only one empty
    if self.empty_ends[0] == 0 or self.empty_ends[1] == 1:
      score = self.base_score * 10
    else:
      score = self.base_score * 500
    return self.scale_by_opp(score)

    
class MissingXPat(Patttern):
  def __init__(
    self, max_num, base_score, is_self=True, 
    empty_ends=[0, 0], missing_x=0, patt_len=0,
  ) -> None:
    super(MissingXPat, self).__init__(max_num, base_score, is_self)
    self.empty_ends = empty_ends
    self.missing_x = missing_x
    self.patt_len = patt_len
    assert len(empty_ends) == 2
    self.empty_ends = sorted(empty_ends)

  def score(self):
    total_empty_ends = self.empty_ends[0] + self.empty_ends[1]
    if total_empty_ends < self.missing_x:
      return 0
  
    score = self.base_score * self.patt_len
    if self.empty_ends[0]  >= 1:
      score *= 2
    return self.scale_by_opp(score)

# Bridge example: [0, 1, 1, 0, 1, 1, 0]
class BridgePat(Patttern):
  def __init__(
    self, max_num, base_score, is_self=True, 
    empty_ends=[0, 0], missing_x=0, patt_len=0,
  ) -> None:
    super(BridgePat, self).__init__(max_num, base_score, is_self)
    assert not is_self
    self.empty_ends = empty_ends
    self.missing_x = missing_x
    self.patt_len = patt_len
    assert len(empty_ends) == 2
    self.empty_ends = sorted(empty_ends)

  def score(self):
    total_empty_ends = self.empty_ends[0] + self.empty_ends[1] + 1
    if total_empty_ends < self.missing_x:
      return 0
    
    if self.missing_x == 1:
      return self.max_num / 2

    if self.missing_x == 2:
      if self.empty_ends[0] >= 1:
        score = self.base_score * 20
      else:
        score = self.base_score * 10
      return self.scale_by_opp(score)

    score = self.base_score * self.patt_len
    if self.empty_ends[0]  >= 1:
      score *= 2
    return self.scale_by_opp(score)


class FullLineScorer(RuleBasedScorerBase):

  def __init__(self, grids, m, player):
    super(FullLineScorer, self).__init__(grids, m, player)
    self.name = "FullLineScorer"
    self.author = "ninghz"
    self.base_score = 10

  def init_grid(self):
    return self.rand_init_grid()

  def best_grid(self):
    top_grids = self.top_n_grids(1)
    return top_grids[0] if top_grids else ScoredGrid(0, (-1, -1))

  def score_grid(self, i, j):
    sz = self.grids.shape
    max_len = 2 * self.m + 1
    scored_grid = ScoredGrid(0, (i, j))
    full_lines = self.make_full_lines(i, j)
    scored_grid.score, scored_grid.win = self.score_full_lines(full_lines)
    return scored_grid

  def make_full_lines(self, i, j):
    def make_one_full_line(line, n1, n2):
      line = np.pad(
        line, 
        (self.m - n1, self.m - n2), 
        'constant', 
        constant_values=(-1, -1),
      )
      line[self.m] = self.player
      return line

    sz = self.grids.shape
    max_len = 2 * self.m + 1
    full_lines = []

    # up-down
    n1 = min(self.m, i)
    n2 = min(self.m, sz[0] - 1 - i)
    line = self.grids[i-n1:i+n2+1, j]
    full_lines.append(make_one_full_line(line, n1, n2))

    # left-right
    n1 = min(self.m, j)
    n2 = min(self.m, sz[1] - 1 - j)
    line = self.grids[i, j-n1:j+n2+1]
    full_lines.append(make_one_full_line(line, n1, n2))

    # line \
    n1 = min(self.m, i, j)
    n2 = min(self.m, sz[0] - 1 - i, sz[1] - 1 - j)
    line = [self.grids[i+k, j+k] for k in range(-n1, n2+1)]
    full_lines.append(make_one_full_line(line, n1, n2))

    # line /
    n1 = min(self.m, i, sz[1] - 1 - j)
    n2 = min(self.m, sz[0] - 1 - i, j)
    line = [self.grids[i+k, j-k] for k in range(-n1, n2+1)]
    full_lines.append(make_one_full_line(line, n1, n2))

    return full_lines

  def score_full_lines(self, full_lines):
    score = 0
    for full_line in full_lines:
      s, w = self.score_full_line(full_line)
      score += s
      if w:
        return score, True

    return score, False

  def score_full_line(self, full_line):
    patterns = []
    win = self.find_single_seg_patts(full_line, patterns)
    score = 0
    for pat in patterns:
      score += pat.score()
    return score, win

  # return: #tokens, #empty, is_self
  def one_side_of_single_seg(self, side):
    side_len = len(side)
    first = side[0]
    is_self = (first == self.player)
    num_tokens = 0
    if self.is_token(first):
      num_tokens = 1
      for i in range(1, side_len):
        if side[i] == first: 
          num_tokens += 1
        else: 
          break
    num_empty = 0
    for j in range(num_tokens, side_len):
      if side[j] == 0: 
        num_empty += 1
      else:
        break

    return num_tokens, num_empty, is_self

  def create_a_bridge_patt(self, num_tokens, empty_ends, is_self, patterns):
    patterns.append(
      BridgePat(
        self.max_num, self.base_score, is_self, empty_ends,
        self.m - num_tokens, num_tokens
      ))

  def create_a_single_seg_patt(self, num_tokens, empty_ends, is_self, patterns):
    if num_tokens == self.m:
      patterns.append(WinPat(self.max_num, self.base_score, is_self))
    elif num_tokens == self.m - 1:
      patterns.append(
        MissingOnePat(self.max_num, self.base_score, is_self, empty_ends))
    elif num_tokens == self.m - 2:
      patterns.append(
        MissingTwoPat(self.max_num, self.base_score, is_self, empty_ends))
    else:
      patterns.append(
        MissingXPat(
          self.max_num, self.base_score, is_self, empty_ends,
          self.m - num_tokens, num_tokens
        ))

  def find_single_seg_patts(self, line, patterns):
    line_len = len(line)
    assert line_len == self.m * 2 + 1
    assert line[self.m] == self.player

    # look at right side seg
    num_tokens_r, num_empty_r, is_self_r = self.one_side_of_single_seg(
      line[self.m+1:]
    )
    # look at left side seg
    num_tokens_l, num_empty_l, is_self_l = self.one_side_of_single_seg(
      line[:self.m][::-1]
    )
    if num_tokens_r > 0 and not is_self_r:
      original_empty = 1
      if num_tokens_l <= 0:
        original_empty += num_empty_l
      self.create_a_single_seg_patt(
        num_tokens_r, [original_empty, num_empty_r], False, patterns)
    if num_tokens_l > 0 and not is_self_l:
      original_empty = 1
      if num_tokens_r <= 0:
        original_empty += num_empty_r
      self.create_a_single_seg_patt(
        num_tokens_l, [original_empty, num_empty_l], False, patterns)
    
    # look at the seg of itself
    num_tokens = 1 # myself in the middle of the line
    empty_ends = [0.0, 0.0]
    if is_self_l:
      num_tokens += num_tokens_l
      empty_ends[0] = num_empty_l
    elif num_tokens_l <= 0:
      empty_ends[0] = num_empty_l

    if is_self_r:
      num_tokens += num_tokens_r
      empty_ends[1] = num_empty_r
    elif num_tokens_r <= 0:
      empty_ends[1] += num_empty_r

    self.create_a_single_seg_patt(
      num_tokens, empty_ends, True, patterns)

    # if both sides are not self
    if not is_self_l and num_tokens_l > 0 and not is_self_r and num_tokens_r > 0:
      self.create_a_bridge_patt(
        num_tokens_l + num_tokens_r, [num_empty_l, num_empty_r], False, patterns)

    return num_tokens >= self.m