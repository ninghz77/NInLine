import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.n_step_scorer import FLNStepScorer
import unittest as ut

class TestFullLineNStepScorer(ut.TestCase):

  def _test_score_paths(
    self,
    grids,
    player,
    top_n_s,
    expected_scores,
    expected_wins,
  ):
    m = 5
    scorer = FLNStepScorer(grids, m, player)
    scored_paths = scorer.score_paths(grids, player, top_n_s)
    scorer.aggregate_score_for_paths(scored_paths)
    scored_paths.sort(key=lambda x:x.score, reverse=True)
    print("---------")
    for sp in scored_paths:
      sp.print_path()
    wins = [p.win for p in scored_paths]
    np.testing.assert_equal(wins, expected_wins)
    scores = [p.score for p in scored_paths]
    np.testing.assert_almost_equal(scores, expected_scores)

  def test_score_paths_normal(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 2:4] = 1
    grids[7, 2:4] = 2
    self._test_score_paths(
      grids, 
      1, 
      [2, 1, 2, 1], 
      [ -397420.32,  -397455.68,  -397509.44, -2954345.76],
      [False] * 4,
    )

  def test_score_paths_win(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 1:5] = 1
    grids[7, 1:5] = 2
    self._test_score_paths(
      grids, 
      1, 
      [2, 1, 2, 1], 
      [4 * 10e6, 4 * 10e6],
      [True, True]
    )


if __name__ == '__main__':
    ut.main()
