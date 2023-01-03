class PattInfo:
  def __init__(
    self, 
    num_tokens, 
    empty_ends, 
    is_self, 
    is_bridge=False,
    ext_tokens=0,
    ext_empties=0,
    bridge_empties=0,
    bridge_inner_pos=True,
    block_dist=0,
    empties_at_pos=1,
  ) -> None:
    self.num_tokens = num_tokens
    self.empty_ends = empty_ends
    self.is_self = is_self
    self.is_bridge = is_bridge
    self.ext_tokens = ext_tokens
    self.ext_empties = ext_empties   
    self.bridge_empties = bridge_empties
    self.bridge_inner_pos = bridge_inner_pos
    self.block_dist = block_dist
    self.empties_at_pos = empties_at_pos

  def get_inner_tokens(self):
    return self.num_tokens if self.num_tokens > 0 else self.ext_tokens

  def get_inner_empties(self):
    return self.empty_ends[0] if self.num_tokens > 0 else self.ext_empties

class Patttern:
  def __init__(self, max_num, base_score, m, is_self=True) -> None:
    self.max_num = max_num
    self.base_score = base_score
    self.m = m
    self.is_self = is_self
    self.opp_weight = 0.5

  def score(self):
    raise "Pattern.score() is not implemented."
  
  def scale_by_opp(self, score):
    return score if self.is_self else score * self.opp_weight

# is self
#                 blocked one side, two sides empty
#   missing one:  500               max_num / 3
#   missing two:  20                500
#   bridge (m1):              400
#   bridge (m2):  20                400
# not self
#                 blocked one side, two sides empty
#   missing one:             max_num / 2
#   missing two:  10                max_num / 20
#   bridge (m1):  0                 max_num / 2
#   bridge (m2):  10                max_num / 20

class WinPat(Patttern):
  def score(self):
    return self.scale_by_opp(self.max_num)

# if is_self = True, assume we already place token on the current position
class MissingOnePat(Patttern):
  def __init__(self, max_num, base_score, m, patt_info:PattInfo) -> None:
    super(MissingOnePat, self).__init__(max_num, base_score, m, patt_info.is_self)
    self.patt_info = patt_info

  def score(self):
    empty_ends = sorted(self.patt_info.empty_ends)
    total_empty_ends = empty_ends[0] + empty_ends[1]
    if total_empty_ends == 0:
      return 0
    if not self.is_self:
      return self.max_num / 2 if self.patt_info.block_dist == 0 else 0

    score = 0
    if empty_ends[0] >= 1:
      score = self.max_num / 3
    elif empty_ends[1] >= 1:
      score = self.base_score * 500
    return score
    
class MissingTwoPat(Patttern):
  def __init__(self, max_num, base_score, m, patt_info:PattInfo) -> None:
    super(MissingTwoPat, self).__init__(max_num, base_score, m, patt_info.is_self)
    self.patt_info = patt_info

  def score(self):
    if not self.is_self and self.patt_info.block_dist >= 1:
      return 0
    empty_ends = sorted(self.patt_info.empty_ends)
    total_empty_ends = empty_ends[0] + empty_ends[1]
    if total_empty_ends < 2:
      return 0
    # one end is not empty or both ends has only one empty
    if empty_ends[0] == 0 or empty_ends[1] == 1:
      score = self.base_score * 25
    else:
      score = self.base_score * 500 if self.is_self else self.max_num / 10

    return self.scale_by_opp(score)

    
class MissingXPat(Patttern):
  def __init__(self, max_num, base_score, m, patt_info:PattInfo) -> None:
    super(MissingXPat, self).__init__(max_num, base_score, m, patt_info.is_self)
    self.patt_info = patt_info

  def score(self):
    if not self.is_self and self.patt_info.block_dist >= 1:
      return 0
    empty_ends = sorted(self.patt_info.empty_ends)
    patt_len = self.patt_info.num_tokens
    missing_x = self.m - self.patt_info.num_tokens
    total_empty_ends = empty_ends[0] + empty_ends[1]
    if total_empty_ends < missing_x:
      return 0
  
    score = self.base_score * patt_len * patt_len
    if empty_ends[0] >= 1:
      score *= 2
    return self.scale_by_opp(score)

# Bridge example: [0, 1, 1, 0, 1, 1, 0]
# if is_self = True, assume we already place token on the current position
class BridgePat(Patttern):
  def __init__(self, max_num, base_score, m, patt_info:PattInfo) -> None:
    super(BridgePat, self).__init__(max_num, base_score, m, patt_info.is_self)
    self.patt_info = patt_info
    assert(self.patt_info.bridge_empties == 1)

  def score(self):
    empty_ends = sorted(self.patt_info.empty_ends)
    patt_len = self.patt_info.num_tokens
    missing_x = self.m - self.patt_info.num_tokens
    total_empty_ends = \
      empty_ends[0] + empty_ends[1] + self.patt_info.bridge_empties
    if total_empty_ends < missing_x:
      return 0
    
    if missing_x <= 1:
      if self.is_self:
        return self.base_score * 400 
      else:
        return self.max_num / 2 if self.patt_info.bridge_inner_pos else 0

    if missing_x == 2:
      if empty_ends[0] >= 1:
        score = self.base_score * 400 if self.is_self else self.max_num / 10
      else:
        score = self.base_score * 20
      return self.scale_by_opp(score)

    score = self.base_score * patt_len * patt_len * 0.5
    if empty_ends[0] >= 1:
      score *= 2
    return self.scale_by_opp(score)

  # Cross pattern
  # 1      1
  #   1  1
  #     0
class CrossPat(Patttern):
  def __init__(self, max_num, base_score, m, is_self, cross_cands=None) -> None:
    super(CrossPat, self).__init__(max_num, base_score, m, is_self)
    self.cross_cands = cross_cands

  def is_good_cand(cand, m):
    if cand.num_tokens < m - 3:
      return False
    empty_ends = sorted(cand.empty_ends)
    # assume we have not put token at the current pos, so we need +1
    total_empty_ends = empty_ends[0] + empty_ends[1] + cand.bridge_empties
    if cand.num_tokens + total_empty_ends < m:
      return False
    if (cand.num_tokens >= m - 2):
      return True
    else:
      good_pos = (cand.empties_at_pos - cand.block_dist >= 2) \
        or cand.bridge_inner_pos
      return (
        cand.num_tokens == m - 3
        and empty_ends[0] >= 1
        and good_pos
        and total_empty_ends >= 4
      )

  def score(self):
    good_cand = len(self.cross_cands)
    score = self.max_num / 4 if good_cand >= 2 else 0
    return self.scale_by_opp(score)
