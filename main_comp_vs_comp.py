import turtle
from core.comp_vs_comp import ComputerVsComputer
from scorers.simple_scorers import StupidScorer, RandomScorer
from scorers.half_line_scorer import HalfLineScorer
from scorers.n_step_scorer import FLNStepScorer
from scorers.full_line_scorer import FullLineScorer
from scorers.alpha_beta_scorer import AlphaBetaScorer


def run():
  N = 15
  m = 5
  grid_size = 30
  draw = True

  turtle.speed(100)
  game = ComputerVsComputer(
    grid_size,
    N,
    m,
    draw=draw,
    player1_scorer_cls=AlphaBetaScorer,
    player2_scorer_cls=FLNStepScorer,
  )

  game.play()
  
  if draw:
    screen = turtle.Screen()
    screen.mainloop()
