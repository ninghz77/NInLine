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

  # Cross pattern
  # 1      1
  #   1  1
  #     0
class CrossPat(Patttern):
  def __init__(self, max_num, base_score, is_self, m, cross_cands=None) -> None:
    super(CrossPat, self).__init__(max_num, base_score, is_self)
    self.m = m
    self.cross_cands = cross_cands

  def score(self):
    if not self.cross_cands or len(self.cross_cands) < 2:
      return 0

    good_cand = 0
    for cand in self.cross_cands:
      if cand.num_tokens < self.m - 3:
        continue
      empty_ends = sorted(cand.empty_ends)
      # assume we have not put token at the current pos, so we need +1
      total_empty_ends = empty_ends[0] + empty_ends[1] + 1
      if cand.num_tokens + total_empty_ends < self.m:
        continue
      if (cand.num_tokens >= self.m - 2) or \
        (cand.num_tokens == self.m - 3 and empty_ends[0] >= 1 and total_empty_ends >= 4):
        good_cand += 1

    score = self.max_num / 4 if good_cand >= 2 else 0
    return self.scale_by_opp(score)
    
class PattInfo:
  def __init__(
    self, 
    num_tokens, 
    empty_ends, 
    is_self, 
    is_bridge=False,
    cross_candidate=False,
  ) -> None:
    self.num_tokens = num_tokens
    self.empty_ends = empty_ends
    self.is_self = is_self
    self.is_bridge = is_bridge
    self.cross_candidate = cross_candidate

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
    patterns = []
    self.find_patts_from_4_lines(full_lines, patterns)
    score = 0
    for pat in patterns:
      score += pat.score()
    return score, False

  # return: PattInfo
  def one_side_patt_info(self, side):
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

    return PattInfo(num_tokens, [num_empty, 0], is_self)

  def create_a_single_seg_patt(self, patt_info, patterns):
    if patt_info.num_tokens == self.m:
      patterns.append(WinPat(self.max_num, self.base_score, patt_info.is_self))
    elif patt_info.num_tokens == self.m - 1:
      patterns.append(
        MissingOnePat(
          self.max_num, 
          self.base_score, 
          patt_info.is_self, 
          patt_info.empty_ends,
        ),
      )
    elif patt_info.num_tokens == self.m - 2:
      patterns.append(
        MissingTwoPat(
          self.max_num, 
          self.base_score, 
          patt_info.is_self, 
          patt_info.empty_ends,
        ),
      )
    else:
      patterns.append(
        MissingXPat(
          self.max_num, self.base_score, patt_info.is_self, patt_info.empty_ends,
          self.m - patt_info.num_tokens, patt_info.num_tokens
        ))

  def create_cross_patt(self, cross_cands, is_self, patterns):
    if not cross_cands:
      return
    patterns.append(CrossPat(
      self.max_num, 
      self.base_score, 
      is_self,
      self.m,
      cross_cands,
    ))

  def create_a_bridge_patt(self, patt_info, patterns):
    patterns.append(
      BridgePat(
        self.max_num, self.base_score, patt_info.is_self, patt_info.empty_ends,
        self.m - patt_info.num_tokens, patt_info.num_tokens
      ))

  def find_opponent_bridge_patt(self, patt_info_r, patt_info_l, patterns):
    # if both sides are not self
    if not patt_info_l.is_self and patt_info_l.num_tokens > 0 and not patt_info_r.is_self and patt_info_r.num_tokens > 0:
      self.create_a_bridge_patt(
        PattInfo(
          patt_info_l.num_tokens + patt_info_r.num_tokens, 
          [patt_info_l.empty_ends[0], patt_info_r.empty_ends[0]], 
          False, 
        ),
        patterns,
      )

  def num_empty_other_side(self, patt_info_other):
    num_empty = 1 # current pos
    if patt_info_other.num_tokens <= 0:
      num_empty += patt_info_other.empty_ends[0]
    return num_empty

  def find_opponent_side_patt(self, patt_info, patt_info_other, patterns):
    if patt_info.num_tokens > 0 and not patt_info.is_self:
      self.create_a_single_seg_patt(
        PattInfo(
          patt_info.num_tokens, 
          [patt_info.empty_ends[0], self.num_empty_other_side(patt_info_other)], 
          False,
        ), 
        patterns,
      )

  def find_self_patt(self, patt_info_r, patt_info_l, patterns):
    patt_info = PattInfo(
      num_tokens=1, # myself in the middle of the line
      empty_ends=[0.0, 0.0],
      is_self=True,
    )
    if patt_info_l.is_self:
      patt_info.num_tokens += patt_info_l.num_tokens
      patt_info.empty_ends[0] = patt_info_l.empty_ends[0]
    elif patt_info_l.num_tokens <= 0:
      patt_info.empty_ends[0] = patt_info_l.empty_ends[0]

    if patt_info_r.is_self:
      patt_info.num_tokens += patt_info_r.num_tokens
      patt_info.empty_ends[1] = patt_info_r.empty_ends[0]
    elif patt_info_r.num_tokens <= 0:
      patt_info.empty_ends[1] += patt_info_r.empty_ends[0]

    self.create_a_single_seg_patt(patt_info, patterns)
    return patt_info

  # side of a cross like
  # 1      1
  #   1  1
  #     0
  # assume we have not put token at the current pos
  def cross_candidate_info(self, patt_info_r, patt_info_l, cross_cands):
    if patt_info_l.num_tokens > 0 and patt_info_r.num_tokens > 0:
      if patt_info_l.is_self != patt_info_r.is_self:
        cross_cands += [patt_info_l, patt_info_r]
      else:
        # it is bridge
        cross_cands.append(PattInfo(
            patt_info_l.num_tokens + patt_info_r.num_tokens, 
            [patt_info_l.empty_ends[0], patt_info_r.empty_ends[0]], 
            patt_info_l.is_self, 
            is_bridge=True,
        ))
    elif patt_info_l.num_tokens > 0:
      cross_cands.append(PattInfo(
          patt_info_l.num_tokens, 
          [patt_info_l.empty_ends[0], patt_info_r.empty_ends[0]], 
          patt_info_l.is_self, 
      ))
    else:
      cross_cands.append(PattInfo(
          patt_info_r.num_tokens, 
          [patt_info_r.empty_ends[0], patt_info_l.empty_ends[0]], 
          patt_info_r.is_self, 
      ))

  def split_cross_candidates(self, cross_cands):
    self_cands = []
    opp_cands = []
    for cand in cross_cands:
      if cand.is_self:
        self_cands.append(cand)
      else:
        opp_cands.append(cand)
    return self_cands, opp_cands

  def find_patts_from_one_line(self, line, patterns, cross_cands):
    line_len = len(line)
    assert line_len == self.m * 2 + 1
    assert line[self.m] == self.player

    # look at right side seg
    patt_info_r = self.one_side_patt_info(line[self.m+1:])
    # look at left side seg
    patt_info_l = self.one_side_patt_info(line[:self.m][::-1])

    self.find_opponent_side_patt(patt_info_r, patt_info_l, patterns)
    self.find_opponent_side_patt(patt_info_l, patt_info_r, patterns)
    
    # look at the seg of itself
    patt_info = self.find_self_patt(patt_info_r, patt_info_l, patterns)

    self.find_opponent_bridge_patt(patt_info_r, patt_info_l, patterns)

    self.cross_candidate_info(patt_info_r, patt_info_l, cross_cands)
    return patt_info.num_tokens >= self.m

  def find_patts_from_4_lines(self, lines, patterns):
    cross_cands = []
    for full_line in lines:
      win = self.find_patts_from_one_line(full_line, patterns, cross_cands)
      if win:
        return self.max_num, True
    
    self_cands, opp_cands = self.split_cross_candidates(cross_cands)
    self.create_cross_patt(self_cands, True, patterns)
    self.create_cross_patt(opp_cands, False, patterns)
