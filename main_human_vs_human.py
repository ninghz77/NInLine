import turtle
from core.human_vs_human import HumanVsHuman


def run():
  N = 15
  m = 5
  grid_size = 30

  turtle.speed(100)
  game = HumanVsHuman(grid_size, N, m)
  screen = turtle.Screen()
  screen.onclick(game.onclick)
  screen.mainloop()
