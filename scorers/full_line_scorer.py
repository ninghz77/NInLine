import numpy as np
from scorers.scorer_base import RuleBasedScorerBase, ScoredGrid
from scorers.pattern import (
  Patttern,
  WinPat, 
  MissingOnePat, 
  MissingTwoPat, 
  MissingXPat,
  BridgePat,
  CrossPat,
  PattInfo,
)

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
    scored_grid.score, scored_grid.attack_score, scored_grid.win = \
      self.score_full_lines(full_lines)
    scored_grid.player = self.player
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
    patterns: list[Patttern] = []
    win = self.find_patts_from_4_lines(full_lines, patterns)
    score = 0
    attack_score = 0
    for pat in patterns:
      s = pat.score()
      score += s
      if pat.is_self:
        attack_score += s
    return score, attack_score, win

  # return: PattInfo
  def one_side_patt_info(self, side):
    def get_tokens_empties(s):
      first = s[0]
      side_len = len(s)
      num_tokens = 0
      if self.is_token(first):
        num_tokens = 1
        for i in range(1, side_len):
          if s[i] == first: 
            num_tokens += 1
          else: 
            break
      num_empty = 0
      for j in range(num_tokens, side_len):
        if s[j] == 0: 
          num_empty += 1
        else:
          break
      return first, num_tokens, num_empty

    player, num_tokens, num_empty = get_tokens_empties(side)

    # handle cases like: x 1 0 1 0 0
    ext_player, ext_tokens, ext_empties = 0, 0, 0
    processed = num_tokens + num_empty
    if num_empty == 1 and processed < len(side):
      ext_player, ext_tokens, ext_empties = get_tokens_empties(side[processed:])
      if (self.is_token(player) and (player != ext_player)) or \
        (not self.is_token(player) and not self.is_token(ext_player)):
        ext_player, ext_tokens, ext_empties = 0, 0, 0
    
    is_self = (player == self.player) if self.is_token(player) \
      else (ext_player == self.player)

    return PattInfo(
      num_tokens, 
      [num_empty, 0], 
      is_self=is_self, 
      ext_tokens=ext_tokens, 
      ext_empties=ext_empties,
    )

  def create_a_single_seg_patt(self, patt_info, patterns):
    if patt_info.num_tokens == self.m:
      patterns.append(WinPat(self.max_num, self.base_score, patt_info.is_self))
    elif patt_info.num_tokens == self.m - 1:
      patterns.append(
        MissingOnePat(
          self.max_num, 
          self.base_score, 
          self.m,
          patt_info,
        ),
      )
    elif patt_info.num_tokens == self.m - 2:
      patterns.append(
        MissingTwoPat(
          self.max_num, 
          self.base_score, 
          self.m,
          patt_info,
        ),
      )
    else:
      patterns.append(
        MissingXPat(self.max_num, self.base_score, self.m, patt_info))

  def create_cross_patt(self, cross_cands, is_self, patterns):
    if not cross_cands:
      return
    patterns.append(CrossPat(
      self.max_num, 
      self.base_score, 
      self.m,
      is_self,
      cross_cands,
    ))

  def create_bridge_patt(self, patt_info, patterns):
    patterns.append(
      BridgePat(
        self.max_num, 
        self.base_score, 
        self.m,
        patt_info=patt_info,
      ))

  def create_opponent_bridge_patt(self, patt_info_r, patt_info_l, patterns):
    # if both sides are not self
    if not patt_info_l.is_self and patt_info_l.num_tokens > 0 and not patt_info_r.is_self and patt_info_r.num_tokens > 0:
      self.create_bridge_patt(
        PattInfo(
          patt_info_l.num_tokens + patt_info_r.num_tokens, 
          [patt_info_l.empty_ends[0], patt_info_r.empty_ends[0]], 
          is_self=False,
          is_bridge=True,
          bridge_empties=1,
          bridge_inner_pos=True,
          empties_at_pos=1,
        ),
        patterns,
      )

  def num_empty_other_side(self, patt_info_other):
    num_empty = 1 # current pos
    if patt_info_other.num_tokens <= 0:
      num_empty += patt_info_other.empty_ends[0]
    return num_empty

  def find_patt_info_from_side(self, patt_info, patt_info_other):
    num_tokens = patt_info.num_tokens + patt_info.ext_tokens
    patts = []
    if num_tokens <= 0:
      return patts

    if patt_info.num_tokens > 0:
      empty_ends = [
        patt_info.empty_ends[0], 
        self.num_empty_other_side(patt_info_other)
      ]
      patts.append(PattInfo(
        patt_info.num_tokens, 
        empty_ends, 
        is_self=patt_info.is_self,
        empties_at_pos=empty_ends[1],
        bridge_inner_pos=False,
      ))

    if patt_info.ext_tokens > 0:
      if patt_info.num_tokens == 0: 
        empty_ends = [
          patt_info.ext_empties,
          patt_info.empty_ends[0] + self.num_empty_other_side(patt_info_other), 
        ]
        patts.append(PattInfo(
          patt_info.ext_tokens, 
          empty_ends, 
          is_self=patt_info.is_self,
          block_dist=1,
          empties_at_pos=empty_ends[1],  
          bridge_inner_pos=False,        
        ))
      else: # patt_info.num_tokens > 0:
        empty_ends = [
          patt_info.ext_empties,
          self.num_empty_other_side(patt_info_other), 
        ]
        patts.append(PattInfo(
          num_tokens, 
          empty_ends, 
          is_self=patt_info.is_self,
          is_bridge=True,
          bridge_empties=1,
          bridge_inner_pos=False,
          empties_at_pos=empty_ends[1],          
        ))
    return patts

  def create_opponent_side_patt(self, patt_info, patt_info_other, patterns):
    if patt_info.is_self:
      return
    patts = self.find_patt_info_from_side(patt_info, patt_info_other)
    for patt in patts:
      if not patt: continue
      if patt.is_bridge:
        self.create_bridge_patt(patt, patterns)
      else:
        self.create_a_single_seg_patt(patt, patterns)

  def create_self_patt(self, patt_info_r, patt_info_l, patterns):
    patt_info = PattInfo(
      num_tokens=1, # myself in the middle of the line
      empty_ends=[0.0, 0.0],
      is_self=True,
      empties_at_pos=1,    
      bridge_inner_pos=False,      
    )
    if patt_info_l.is_self:
      patt_info.num_tokens += patt_info_l.num_tokens
      patt_info.empty_ends[0] = patt_info_l.empty_ends[0]
    elif patt_info_l.num_tokens <= 0:
      patt_info.empty_ends[0] = patt_info_l.empty_ends[0]
    if patt_info_l.num_tokens <= 0:
      patt_info.empties_at_pos += patt_info_l.empty_ends[0]

    if patt_info_r.is_self:
      patt_info.num_tokens += patt_info_r.num_tokens
      patt_info.empty_ends[1] = patt_info_r.empty_ends[0]
    elif patt_info_r.num_tokens <= 0:
      patt_info.empty_ends[1] += patt_info_r.empty_ends[0]
    if patt_info_r.num_tokens <= 0:
      patt_info.empties_at_pos += patt_info_l.empty_ends[0]

    self.create_a_single_seg_patt(patt_info, patterns)

    if patt_info_l.ext_tokens > 0 and patt_info_l.is_self:
      self.create_bridge_patt(
        PattInfo(
          patt_info.num_tokens + patt_info_l.ext_tokens, 
          [patt_info_l.ext_empties, patt_info.empty_ends[1]], 
          is_self=True,
          is_bridge=True,
          bridge_empties=1,
          bridge_inner_pos=(patt_info_l.num_tokens <= 0),
          empties_at_pos=patt_info.empties_at_pos,
          block_dist=(1 if patt_info_l.num_tokens <= 0 else 0),
        ),
        patterns,
      )

    if patt_info_r.ext_tokens > 0 and patt_info_r.is_self:
      self.create_bridge_patt(
        PattInfo(
          patt_info.num_tokens + patt_info_r.ext_tokens, 
          [patt_info.empty_ends[0], patt_info_r.ext_empties], 
          is_self=True,
          is_bridge=True,
          bridge_empties=1,
          bridge_inner_pos=(patt_info_r.num_tokens <= 0),
          empties_at_pos=patt_info.empties_at_pos,
          block_dist=(1 if patt_info_r.num_tokens <= 0 else 0),
        ),
        patterns,
      )

    return patt_info

  # side of a cross like
  # 1      1
  #   1  1
  #     0
  # assume we have not put token at the current pos
  # (TODO) bridge on one side.
  def cross_candidate_info(self, patt_info_r, patt_info_l, cross_cands):
    cross_cand_map = {}
    l_tokens = patt_info_l.num_tokens + patt_info_l.ext_tokens
    r_tokens = patt_info_r.num_tokens + patt_info_r.ext_tokens
    if l_tokens > 0 and r_tokens > 0 and \
      patt_info_l.is_self == patt_info_r.is_self:
      bridge_empties = 1 + \
        (1 if patt_info_l.num_tokens <= 0 else 0) + \
        (1 if patt_info_r.num_tokens <= 0 else 0)
      # it is bridge
      if bridge_empties <= 2:
        cand = PattInfo(
            patt_info_l.get_inner_tokens() + patt_info_r.get_inner_tokens(), 
            [patt_info_l.get_inner_empties(), patt_info_r.get_inner_empties()], 
            patt_info_l.is_self,
            is_bridge=True,
            bridge_empties=bridge_empties,
            bridge_inner_pos=True,
            empties_at_pos=bridge_empties,
        )
        if CrossPat.is_good_cand(cand, self.m):
          cross_cand_map[cand.is_self] = cand

    side_cands = self.find_patt_info_from_side(patt_info_l, patt_info_r) + \
      self.find_patt_info_from_side(patt_info_r, patt_info_l)
    for cand in side_cands:
      if not cand: continue
      if cand.is_self in cross_cand_map:
        continue
      if CrossPat.is_good_cand(cand, self.m):
        cross_cand_map[cand.is_self] = cand
    
    for k, v in cross_cand_map.items():
      cross_cands.append(v)

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

    self.create_opponent_side_patt(patt_info_r, patt_info_l, patterns)
    self.create_opponent_side_patt(patt_info_l, patt_info_r, patterns)
    
    # look at the seg of itself
    patt_info = self.create_self_patt(patt_info_r, patt_info_l, patterns)

    self.create_opponent_bridge_patt(patt_info_r, patt_info_l, patterns)

    self.cross_candidate_info(patt_info_r, patt_info_l, cross_cands)
    return patt_info.num_tokens >= self.m

  def find_patts_from_4_lines(self, lines, patterns):
    cross_cands = []
    win = False
    for full_line in lines:
      line_win = self.find_patts_from_one_line(full_line, patterns, cross_cands)
      if line_win:
        win = True
    
    self_cands, opp_cands = self.split_cross_candidates(cross_cands)
    self.create_cross_patt(self_cands, True, patterns)
    self.create_cross_patt(opp_cands, False, patterns)
    return win