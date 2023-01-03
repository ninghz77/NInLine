import copy
import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.half_line_scorer import HalfLineScorer
from scorers.scorer_base import ScorerBase, ScoredGrid

class ScoredPath:
  def __init__(self, scored_grid=None) -> None:
    self.win = False
    self.score = 0
    self.scored_grids: list[ScoredGrid] = [] if not scored_grid else [scored_grid]

  def print_path(self):
    print("Aggregated score: ", self.score)
    for sg in self.scored_grids:
      print("P{} {}: a{} / b{} / {}, {}".format(
        sg.player, sg.grid, 
        sg.attack_score, sg.score - sg.attack_score, 
        sg.score, sg.win))

class NStepScorer(ScorerBase):

  def __init__(
    self, 
    grids, 
    m, 
    player, 
    internal_scorer_cls,
    top_n_steps=[5, 3],
    weight=0.8,
  ):
    super(NStepScorer, self).__init__(grids, m, player)
    self.internal_scorer_cls = internal_scorer_cls
    self.weight = weight
    self.top_n_steps = top_n_steps

  def init_grid(self):
    return self.rand_init_grid()

  def score_paths(self, grids, player, top_n_s):
    if not top_n_s:
      return [ScoredPath()]

    scorer = self.internal_scorer_cls(grids, self.m, player)
    top_n_grids = scorer.top_n_grids(top_n_s[0])
    if not top_n_grids:
      return [ScoredPath()]

    paths = []

    for scored_grid in top_n_grids:
      # already win, don't look further
      if scored_grid.win:
        paths.append(ScoredPath(scored_grid))
        continue

      grids_loc = copy.deepcopy(grids)
      g = scored_grid.grid
      grids_loc[g[0], g[1]] = player
      paths_loc = self.score_paths(
        grids_loc, 
        self.opponent_player(player),
        top_n_s[1:],
      )
      for p in paths_loc:
        p.scored_grids.insert(0, scored_grid)
        paths.append(p)
      
    return paths #if paths else [ScoredPath()]

  def aggregate_score_for_a_path(self, scored_path:ScoredPath):
    first_grid = scored_path.scored_grids[0]
    if first_grid.win:  # Already win, set score to max
      scored_path.score = len(self.top_n_steps) * self.max_num
      scored_path.win = True
      return scored_path

    score = 0
    scale = 1
    k = 0
    for g in scored_path.scored_grids:
      s = g.score if k == 0 else g.attack_score
      score += scale * s
      scale *= -self.weight
      k += 1
    scored_path.score = score
    scored_path.win = False
    return score

  def aggregate_score_for_paths(self, scored_paths):
    for p in scored_paths:
      self.aggregate_score_for_a_path(p)

  def best_grid(self):
    scored_paths = self.score_paths(
      self.grids, self.player, self.top_n_steps)
    self.aggregate_score_for_paths(scored_paths)
    scored_paths.sort(key=lambda x:x.score, reverse=True)
    print("---------")
    for sp in scored_paths:
      sp.print_path()
    grid = scored_paths[0].scored_grids[0]
    return grid

class HLNStepScorer(NStepScorer):

  def __init__(self, grids, m, player):
    super(HLNStepScorer, self).__init__(
      grids, m, player, HalfLineScorer, top_n_steps=[5, 1, 3, 1], weight=0.8)
    self.name = "HLNStepScorer"
    self.author = "ninghz"

class FLNStepScorer(NStepScorer):

  def __init__(self, grids, m, player):
    super(FLNStepScorer, self).__init__(
      grids, m, player, FullLineScorer, top_n_steps=[5, 1, 3, 1], weight=0.8)
    self.name = "FLNStepScorer"
    self.author = "ninghz"

