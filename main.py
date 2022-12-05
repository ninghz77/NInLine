import turtle
from core.comp_vs_comp import ComputerVsComputer
from core.human_vs_comp import HumanVsComputer
import scorers.evaluator as evaluator
from scorers.scorer_base import StupidScorer, RandomScorer
from scorers.half_line_scorer import HalfLineScorer
from scorers.half_line_scorer2 import HalfLineScorer2

N = 15
m = 15
grid_size = 30
mode = "comp_vs_comp"
#mode = "human_vs_comp"
#mode = "eval"

if mode == "comp_vs_comp":
  turtle.speed(100)
  game = ComputerVsComputer(
    grid_size,
    N,
    m,
    draw=True,
    player1_scorer_cls=StupidScorer,
    player2_scorer_cls=StupidScorer,
  )
  game.play()
elif mode == "human_vs_comp":
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
elif mode == "eval":
  evaluator.Evaluate(N, m, num_races=3)
