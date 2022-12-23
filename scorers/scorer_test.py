import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.n_step_scorer import FLNStepScorer

def test_full_line_score_line(full_line, player, expected_scores):
  print("Test test_full_line_score_line...")
  grids = np.zeros((8, 8), dtype=np.int32)
  m = 5
  full_line[m] = player
  scorer = FullLineScorer(grids, m, player)
  patterns = []
  win = scorer.find_single_seg_patts(full_line, patterns)
  for pat, score in zip(patterns, expected_scores):
    print("pattern score: {}, expected score: {}".format(pat.score(), score))

#test_full_line_score_line([-1, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1], 1, [3333333.33])
#test_full_line_score_line([-1, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1], 2, [0, 10])
#test_full_line_score_line([-1, 0, 1, 1, 1, 1, 2, 2, 0, 0, 0], 1, [20, 0])
#test_full_line_score_line([-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, 0], 2, [0, 100])
#test_full_line_score_line([-1, 0, 1, 2, 1, 1, 2, 2, 0, 0, -1], 1, [0, 0])
#test_full_line_score_line([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], 1, [20])
#test_full_line_score_line([-1, 0, 0, 0, 1, 0, 0, 0, 0, 1, -1], 1, [40])
#test_full_line_score_line([-1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1], 2, [500000, 10])
#test_full_line_score_line([-1, 0, 0, 0, 0, 1, 2, 2, 2, 2, -1], 1, [500000, 10])
#test_full_line_score_line([-1, 0, 0, 0, 0, 1, 2, 2, 2, 0, -1], 1, [2500, 10])
#test_full_line_score_line([-1, 0, 0, 0, 2, 1, 2, 2, 2, 0, -1], 1, [0, 10, 0, 500000])
#test_full_line_score_line([-1, 0, 0, 0, 2, 1, 2, 2, 1, 0, -1], 1, [0, 10, 0, 50])
#quit()

def test_make_full_lines(i, j, player, expected_lines):
  print("Test test_make_full_lines...")
  grids = np.zeros((8, 8), dtype=np.int32)
  m = 5
  grids[3:5, 1:4] = 1
  scorer = FullLineScorer(grids, m, player)
  full_lines = scorer.make_full_lines(i, j)
  print("grids: ")
  print(grids)
  print("full lines:")
  for line in full_lines:
    print(line[:])
  print("expected_lines: ")
  for line in expected_lines:
    print(line[:])

test_make_full_lines(2, 2, 1, [
  [-1, -1, -1, 0, 0, 1, 1, 1, 0, 0, 0],
  [-1, -1, -1, 0, 0, 1, 0, 0, 0, 0, 0],
  [-1, -1, -1, 0, 0, 1, 1, 0, 0, 0, 0],
  [-1, -1, -1, 0, 0, 1, 1, 0, -1, -1, -1]
])

test_make_full_lines(2, 2, 2, [
  [-1, -1, -1, 0, 0, 2, 1, 1, 0, 0, 0],
  [-1, -1, -1, 0, 0, 2, 0, 0, 0, 0, 0],
  [-1, -1, -1, 0, 0, 2, 1, 0, 0, 0, 0],
  [-1, -1, -1, 0, 0, 2, 1, 0, -1, -1, -1]
])

test_make_full_lines(6, 3, 1, [
  [0, 0, 1, 1, 0, 1, 0, -1, -1, -1, -1],
  [-1, -1, 0, 0, 0, 1, 0, 0, 0, 0, -1],
  [-1, -1, 0, 1, 0, 1, 0, -1, -1, -1, -1],
  [-1, 0, 0, 0, 0, 1, 0, -1, -1, -1, -1],
])

def test_FLNStepScorer():
  print("Test test_FLNStepScorer...")
  grids = np.zeros((15, 15), dtype=np.int32)
  m = 5
  grids[6, 7] = 2
  grids[7, 3] = 2
  grids[7, 4:8] = 1
  grids[7, 8] = 2
  grids[8, 9] = 2
  scorer = FLNStepScorer(grids, m, 1)
  scored_grid = scorer.best_grid()
  print(grids)
  print("grid score: ", scored_grid.score)
  print("grid: ", scored_grid.grid)

test_FLNStepScorer()