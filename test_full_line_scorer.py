import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.n_step_scorer import FLNStepScorer
import unittest as ut

class TestFullLineScorer(ut.TestCase):
  
  def _test_full_line_score_line(
    self, 
    full_line, 
    player, 
    expected_scores,
    expected_win,
  ):
    grids = np.zeros((8, 8), dtype=np.int32)
    m = 5
    full_line[m] = player
    scorer = FullLineScorer(grids, m, player)
    patterns = []
    cross_cands = []
    win = scorer.find_patts_from_one_line(
      full_line, patterns, cross_cands)
    self.assertEqual(win, expected_win)
    scores = [pat.score() for pat in patterns]
    self.assertEqual(len(scores), len(expected_scores))
    np.testing.assert_almost_equal(scores, expected_scores)

  def test_full_line_score_line(self):
    self._test_full_line_score_line(
      [-1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      1, 
      [10000000],
      True,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      1, 
      [3333333.333333333],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 0, 0, 0, 0, 0, -1], 
      2, 
      [500000, 10],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 1, 2, 2, 0, 0, 0], 
      1, 
      [40, 1000],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, 0], 
      2, 
      [0, 200],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, -1], 
      1, 
      [40, 0],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], 
      1, 
      [20],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 1, 0, 0, 0, 0, 1, -1], 
      1, 
      [80],
      False,
    )
    self._test_full_line_score_line(
      [-1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      2, 
      [5000000, 10],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 1, 2, 2, 2, 2, -1], 
      1, 
      [5000000, 10],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 1, 2, 2, 2, 0, -1], 
      1, 
      [500000, 10],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 2, 1, 2, 2, 2, 0, -1], 
      1, 
      [100, 10, 0, 5000000],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 2, 1, 2, 2, 1, 0, -1], 
      1, 
      [0, 10, 0, 100],
      False,
    )

  def _test_make_full_lines(self, i, j, player, expected_lines):
    grids = np.zeros((8, 8), dtype=np.int32)
    m = 5
    grids[3:5, 1:4] = 1
    scorer = FullLineScorer(grids, m, player)
    full_lines = scorer.make_full_lines(i, j)
    self.assertEqual(len(full_lines), len(expected_lines))
    for fl, efl in zip(full_lines, expected_lines):
      np.testing.assert_equal(fl, efl)

  def test_make_full_lines(self):
    self._test_make_full_lines(2, 2, 1, [
      [-1, -1, -1, 0, 0, 1, 1, 1, 0, 0, 0],
      [-1, -1, -1, 0, 0, 1, 0, 0, 0, 0, 0],
      [-1, -1, -1, 0, 0, 1, 1, 0, 0, 0, 0],
      [-1, -1, -1, 0, 0, 1, 1, 0, -1, -1, -1]
    ])

    self._test_make_full_lines(2, 2, 2, [
      [-1, -1, -1, 0, 0, 2, 1, 1, 0, 0, 0],
      [-1, -1, -1, 0, 0, 2, 0, 0, 0, 0, 0],
      [-1, -1, -1, 0, 0, 2, 1, 0, 0, 0, 0],
      [-1, -1, -1, 0, 0, 2, 1, 0, -1, -1, -1]
    ])

    self._test_make_full_lines(6, 3, 1, [
      [0, 0, 1, 1, 0, 1, 0, -1, -1, -1, -1],
      [-1, -1, 0, 0, 0, 1, 0, 0, 0, 0, -1],
      [-1, -1, 0, 1, 0, 1, 0, -1, -1, -1, -1],
      [-1, 0, 0, 0, 0, 1, 0, -1, -1, -1, -1],
    ])

  def _test_score_grid(
    self, 
    grids,
    i, 
    j, 
    player,     
    expected_score,
    expected_win,
  ):
    m = 5
    scorer = FullLineScorer(grids, m, player)
    sg = scorer.score_grid(i, j)
    self.assertAlmostEqual(sg.score, expected_score)
    self.assertEqual(sg.win, expected_win)

  def test_score_grid_normal(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 2:5] = 1
    grids[7, 2:4] = 2
    self._test_score_grid(grids, 5, 5, 2, 500070, False)
    self._test_score_grid(grids, 7, 4, 2, 5060, False)

  def test_score_grid_win(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 1:5] = 1
    grids[7, 1:5] = 2
    self._test_score_grid(grids, 5, 0, 1, 10000030, True)
    self._test_score_grid(grids, 5, 5, 1, 10000060, True)
    self._test_score_grid(grids, 5, 0, 2, 5000030, False)
    
  def _test_cross_patt(
    self, 
    grids,
    i, 
    j, 
    player,     
    expected_scores,
    expected_win,
  ):
    m = 5
    scorer = FullLineScorer(grids, m, player)
    full_lines = scorer.make_full_lines(i, j)
    patterns = []
    win = scorer.find_patts_from_4_lines(full_lines, patterns)
    self.assertEqual(win, expected_win)
    scores = [pat.score() for pat in patterns]
    self.assertEqual(len(scores), len(expected_scores))
    np.testing.assert_almost_equal(scores, expected_scores)

  def test_cross_patt_normal(self):
    grids = np.zeros((8, 8), dtype=np.int32)
    grids[2, 1:3] = 1
    grids[4, 1] = 1
    grids[3, 2] = 1
    self._test_cross_patt(
      grids, 2, 3, 1, 
      [20, 5000, 20, 5000, 2500000, 0],
      False,
    )
    self._test_cross_patt(
      grids, 2, 3, 2, 
      [20, 40, 10, 20, 40, 0, 1250000],
      False,
    )
    grids[4, 1] = 0
    self._test_cross_patt(
      grids, 2, 3, 1, 
      [20, 5000, 20, 80, 0, 0],
      False,
    )
    grids[4, 1] = 1
    grids[5, 0] = 2
    self._test_cross_patt(
      grids, 2, 3, 1, 
      [20, 5000, 20, 200, 0, 0],
      False,
    )

  def test_cross_patt_missing_one(self):
    grids = np.zeros((8, 8), dtype=np.int32)
    grids[2, 1:4] = 1
    grids[4, 2] = 1
    grids[3, 3] = 1
    self._test_cross_patt(
      grids, 2, 4, 1,
      [20, 10e6/3, 20, 5000, 2500000, 0],
      False,
    )
    self._test_cross_patt(
      grids, 2, 4, 2,
      [20, 500000, 0, 20, 40, 0, 1250000],
      False,
    )
    # bridge
    grids[4, 2] = 0
    grids[1, 5] = 1
    self._test_cross_patt(
      grids, 2, 4, 1,
      [20, 10e6/3, 20, 5000, 2500000, 0],
      False,
    )


if __name__ == '__main__':
    ut.main()
