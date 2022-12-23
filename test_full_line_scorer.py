import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.n_step_scorer import FLNStepScorer
import unittest as ut

class TestFullLineScorer(ut.TestCase):
  
  def _test_full_line_score_line(self, full_line, player, expected_scores):
    grids = np.zeros((8, 8), dtype=np.int32)
    m = 5
    full_line[m] = player
    scorer = FullLineScorer(grids, m, player)
    patterns = []
    win = scorer.find_single_seg_patts(full_line, patterns)
    scores = [pat.score() for pat in patterns]
    self.assertEqual(len(scores), len(expected_scores))
    np.testing.assert_almost_equal(scores, expected_scores)

  def test_full_line_score_line(self):
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      1, 
      [3333333.333333333],
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      2, 
      [2500, 10],
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 1, 1, 1, 2, 2, 0, 0, 0], 
      1, 
      [20, 500],
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, 0], 
      2, 
      [0, 100],
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, -1], 
      1, 
      [20, 0],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], 
      1, 
      [20],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 1, 0, 0, 0, 0, 1, -1], 
      1, 
      [40],
    )
    self._test_full_line_score_line(
      [-1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1], 
      2, 
      [5000000, 10],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 1, 2, 2, 2, 2, -1], 
      1, 
      [5000000, 10],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 0, 1, 2, 2, 2, 0, -1], 
      1, 
      [2500, 10],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 2, 1, 2, 2, 2, 0, -1], 
      1, 
      [50, 10, 0, 5000000],
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 2, 1, 2, 2, 1, 0, -1], 
      1, 
      [0, 10, 0, 50],
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

if __name__ == '__main__':
    ut.main()
