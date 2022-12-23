import numpy as np
from scorers.full_line_scorer import FullLineScorer
from scorers.n_step_scorer import FLNStepScorer


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