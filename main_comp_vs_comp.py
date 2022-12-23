import turtle
from core.comp_vs_comp import ComputerVsComputer
from scorers.simple_scorers import StupidScorer, RandomScorer
from scorers.half_line_scorer import HalfLineScorer
from scorers.n_step_scorer import FLNStepScorer


def run():
  N = 15
  m = 5
  grid_size = 30

  turtle.speed(100)
  game = ComputerVsComputer(
    grid_size,
    N,
    m,
    draw=True,
    player1_scorer_cls=HalfLineScorer,
    player2_scorer_cls=FLNStepScorer,
  )
  game.play()
