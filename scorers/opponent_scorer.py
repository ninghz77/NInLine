import numpy as np
from scorers.half_line_scorer import HalfLineScorer
from scorers.scorer_base import ScorerBase


class OpponentScorer(ScorerBase):

  def __init__(self, grids, m, player, internal_scorer_cls, opponent_weight=0.8):
    super(OpponentScorer, self).__init__(grids, m, player)
    self.internal_scorer_cls = internal_scorer_cls
    self.opponent_weight = opponent_weight

  def best_grid(self):
    player_scorer = self.internal_scorer_cls(self.grids, self.m, self.player)
    opponent_scorer = self.internal_scorer_cls(self.grids, self.m, self.opponent_player(self.player))
    player_grid, player_score = player_scorer.best_grid()
    opponent_grid, opponent_score = opponent_scorer.best_grid()
    if player_score >= self.opponent_weight * opponent_score:
      return player_grid, player_score
    else:
      return opponent_grid, opponent_score


class HLOpponentScorer(OpponentScorer):

  def __init__(self, grids, m, player):
    super(HLOpponentScorer, self).__init__(grids, m, player, HalfLineScorer, opponent_weight=0.9,)
    self.name = "HLOpponentScorer"
    self.author = "ninghz"

    
    
