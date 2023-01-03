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
      [40, 5000],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, 0], 
      2, 
      [0, 250],
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
      [125, 10, 0, 5000000],
      False,
    )
    self._test_full_line_score_line(
      [-1, 0, 0, 0, 2, 1, 2, 2, 1, 0, -1], 
      1, 
      [0, 10, 0, 100],
      False,
    )
    self._test_full_line_score_line( # side bridge
      [-1, 0, 0, 0, 1, 1, 1, 0, 1, 0, -1], 
      1, 
      [5000, 4000],
      False,
    )
    self._test_full_line_score_line( # two side bridges
      [-1, 0, 1, 0, 1, 1, 1, 0, 1, 0, -1], 
      1, 
      [250, 4000, 4000],
      False,
    )
    self._test_full_line_score_line( # one side bridges
      [-1, 0, 0, 1, 0, 1, 1, 0, 1, 0, -1], 
      1, 
      [0, 4000, 4000],
      False,
    )
    self._test_full_line_score_line( # one side bridges
      [-1, 0, 1, 0, 0, 1, 1, 0, 1, 0, -1], 
      1, 
      [80, 4000],
      False,
    )
    self._test_full_line_score_line( # other player one side bridges
      [-1, 0, 1, 0, 0, 2, 1, 0, 1, 0, -1], 
      2, 
      [10, 20, 0],
      False,
    )
    self._test_full_line_score_line( # other player one side bridges
      [-1, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0], 
      2, 
      [10, 20, 0],
      False,
    )
    self._test_full_line_score_line( # other player one side bridges
      [-1, 0, 1, 1, 0, 2, 0, 0, 0, 0, 0], 
      2, 
      [0, 20],
      False,
    )
    self._test_full_line_score_line( # other player one side bridges
      [-1, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0], 
      2, 
      [40, 10],
      False,
    )
    self._test_full_line_score_line( # at side of missing one
      [1, 1, 1, 0, 1, 2, 0, 0, 0, 0, 0], 
      2, 
      [10, 0, 10],
      False,
    )
    self._test_full_line_score_line( # fill hole of bridge
      [-1, 0, 1, 1, 1, 2, 1, 0, 0, 0, 0], 
      2, 
      [10, 125, 0, 5000000],
      False,
    )
    self._test_full_line_score_line( # block missing two
      [-1, 0, 1, 1, 1, 2, 0, 0, 0, 0, 0], 
      2, 
      [500000, 10],
      False,
    )
    self._test_full_line_score_line( # block missing two
      [0, 1, 1, 1, 0, 2, 0, 0, 0, 0, 0], 
      2, 
      [0, 20],
      False,
    )
    self._test_full_line_score_line( # missing one
      [-1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0], 
      1, 
      [5000],
      False,
    )
    self._test_full_line_score_line( # single token
      [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], 
      1, 
      [20],
      False,
    )
    self._test_full_line_score_line( # single token
      [0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0], 
      1, 
      [10, 10],
      False,
    )
    self._test_full_line_score_line( # single token
      [0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0], 
      1, 
      [250],
      False,
    )
    self._test_full_line_score_line( # single token
      [0, 2, 1, 1, 0, 1, 0, 0, 0, 0, 0], 
      1, 
      [20, 200],
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

  #@ut.skip
  def test_score_grid_normal(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 2:5] = 1
    grids[7, 2:4] = 2
    self._test_score_grid(grids, 5, 5, 2, 500110, False)
    self._test_score_grid(grids, 7, 4, 2, 5060, False)

  #@ut.skip
  def test_score_grid_win(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 1:5] = 1
    grids[7, 1:5] = 2
    self._test_score_grid(grids, 5, 0, 1, 10000030, True)
    self._test_score_grid(grids, 5, 5, 1, 10000060, True)
    self._test_score_grid(grids, 5, 0, 2, 5000050, False)

  #@ut.skip
  def test_score_grid_simple(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 5] = 1
    self._test_score_grid(grids, 5, 7, 1, 120, False)

  #@ut.skip
  def test_score_grid_simple2(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 5] = 1
    self._test_score_grid(grids, 5, 6, 1, 140, False)

  @ut.skip
  def test_score_grid_missing_one_bridge(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 2:5] = 1
    grids[5, 6] = 1
    grids[5, 7] = 2
    print(grids)
    self._test_score_grid(grids, 5, 7, 2, 0, False)

  @ut.skip
  def test_score_grid_missing_one_bridge2(self):
    grids = np.zeros((15, 15), dtype=np.int32)
    grids[5, 2:5] = 1
    grids[5, 6] = 1
    print(grids)
    self._test_score_grid(grids, 5, 4, 2, 500007.0, False)

  def _test_cross_patt_on_line(
    self, 
    full_line, 
    player, 
    num_good_cand,
  ):
    grids = np.zeros((15, 15), dtype=np.int32)
    m = 5
    full_line[m] = player
    scorer = FullLineScorer(grids, m, player)
    cross_cands = []
    # look at right side seg
    patt_info_r = scorer.one_side_patt_info(full_line[m+1:])
    # look at left side seg
    patt_info_l = scorer.one_side_patt_info(full_line[:m][::-1])
    scorer.cross_candidate_info(patt_info_r, patt_info_l, cross_cands)
    self.assertEqual(len(cross_cands), num_good_cand)

  def test_cross_patt_on_line(self):
    self._test_cross_patt_on_line( # not good-cand, empty not enough
      [0, 0, -1, 0, 1, 2, 1, 0, -1, 0, 0], 
      2, 0,
    )
    self._test_cross_patt_on_line( # not good-cand, too short
      [0, 0, 0, 0, 1, 2, 0, 0, -1, 0, 0], 
      2, 0,
    )
    self._test_cross_patt_on_line( # not good-cand, other side blocked
      [0, 0, 0, 1, 1, 2, 2, 0, 0, 0, 0], 
      2, 0,
    )
    self._test_cross_patt_on_line( # good-cand on other side empty
      [0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # good-cand on other side empty
      [0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0], 
      1, 1,
    )
    self._test_cross_patt_on_line( # good-cand on other side empty
      [0, 0, 1, 0, 1, 2, 0, 0, 0, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # good-cand on other side empty
      [0, -1, 1, 1, 1, 2, 0, 0, 0, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # good-cand cross both sides
      [0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # two good-cand from opponent, dedup to 1
      [0, 0, 1, 0, 1, 2, 1, 0, 0, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # current pos is blocked by player 1, not good for 2
      [0, 0, 1, 0, 1, 2, 0, 2, 2, 0, 0], 
      2, 1,
    )
    self._test_cross_patt_on_line( # good cand from two sides
      [0, 0, 1, 1, 0, 2, 0, 2, 2, 0, 0], 
      2, 2,
    )
    self._test_cross_patt_on_line( # not good-cand, other side blocked
      [0, 0, 1, 1, 0, 2, 0, 0, 0, 0, 0], 
      2, 1,
    )

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
    # self.assertEqual(len(scores), len(expected_scores))
    np.testing.assert_almost_equal(scores, expected_scores)

  #@ut.skip
  def test_cross_patt_normal(self):
    grids = np.zeros((8, 8), dtype=np.int32)
    grids[2, 1:3] = 1
    grids[4, 1] = 1
    grids[3, 2] = 1
    self._test_cross_patt(
      grids, 2, 3, 1, 
      [20, 5000, 20, 5000, 2500000],
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
      [20, 5000, 20, 80, 0],
      False,
    )
    grids[4, 1] = 1
    grids[5, 0] = 2
    self._test_cross_patt(
      grids, 2, 3, 1, 
      [20, 5000, 20, 250, 0],
      False,
    )

  #@ut.skip
  def test_cross_patt_missing_one(self):
    grids = np.zeros((8, 8), dtype=np.int32)
    grids[2, 1:4] = 1
    grids[4, 2] = 1
    grids[3, 3] = 1
    self._test_cross_patt(
      grids, 2, 4, 1,
      [20, 10e6/3, 20, 5000, 2500000],
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
      [20, 10e6/3, 20, 5000, 2500000],
      False,
    )

  #@ut.skip
  def test_cross_patt_side_bridge(self):
    grids = np.zeros((8, 8), dtype=np.int32)
    grids[2, 2:4] = 1
    grids[4, 2] = 1
    grids[1, 5] = 1
    self._test_cross_patt(
      grids, 2, 4, 1,
      [20, 5000, 20, 0, 4000, 2500000],
      False,
    )
    self._test_cross_patt(
      grids, 2, 4, 2,
      [20, 40, 0, 20, 0, 0, 0, 1250000],
      False,
    )
    # bridge
    grids[3, 3] = 1
    grids[1, 5] = 1
    self._test_cross_patt(
      grids, 2, 4, 1,
      [20, 5000, 20, 10e6/3, 2500000],
      False,
    )

if __name__ == '__main__':
    ut.main()
