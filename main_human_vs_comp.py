import turtle
from core.human_vs_comp import HumanVsComputer
from scorers.half_line_scorer import HalfLineScorer


def run():
  N = 15
  m = 5
  grid_size = 30

  turtle.speed(100)
  game = HumanVsComputer(
    grid_size,
    N,
    m,
    scorer_cls=HalfLineScorer,
    who_first="computer",  # computer or human
  )
  screen = turtle.Screen()
  screen.onclick(game.onclick)
  screen.mainloop()
