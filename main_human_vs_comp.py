import turtle
from core.human_vs_comp import HumanVsComputer
from scorers.half_line_scorer import HalfLineScorer
from scorers.half_line_scorer2 import HalfLineScorer2
from scorers.opponent_scorer import HLOpponentScorer


def run():
  N = 15
  m = 5
  grid_size = 25

  turtle.speed(100)
  game = HumanVsComputer(
    grid_size,
    N,
    m,
    scorer_cls=HalfLineScorer2,
    who_first="computer",  # computer or human
  )
  screen = turtle.Screen()
  screen.onclick(game.onclick)
  screen.mainloop()
