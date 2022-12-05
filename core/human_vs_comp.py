from core.game_base import GameBase
from core.board import Board
from scorers.scorer_base import ScorerBase


class HumanVsComputer(GameBase):

  def __init__(
    self,
    grid_size,
    N,
    m,
    scorer_cls,
    who_first="computer",
  ):
    if who_first == "computer":
      player1_scorer_cls = scorer_cls
      player2_scorer_cls = ScorerBase
    else:
      player1_scorer_cls = ScorerBase
      player2_scorer_cls = scorer_cls

    super(HumanVsComputer, self).__init__(
      grid_size,
      N,
      m,
      player1_scorer_cls=player1_scorer_cls,
      player2_scorer_cls=player2_scorer_cls,
    )

    self.board = Board(grid_size, N)
    if who_first == "computer":
      self.init_step(self.scorer1, self.player1)
      self.human = self.player2
      self.computer = self.player1
    else:
      self.human = self.player1
      self.computer = self.player2

  def onclick(self, x, y):
    if self.game_over():
      return

    i, j = self.board.mouse_point_to_grid_index(x, y)
    step_valid, win = self.step(i, j, self.human)

    if step_valid and not self.game_over():
      i, j = self.player_best_grid(self.computer)
      step_valid, win = self.step(i, j, self.computer)
      if not step_valid:
        print("Computer cannot get valid step. Human player win!")
        self.winner = self.human

    if self.game_over():
      print(self.game_over_text())
      self.draw_game_over_text()
