from core.game_base import GameBase
from core.board import Board


class HumanVsHuman(GameBase):

  def __init__(self, grid_size, N, m):

    super(HumanVsHuman, self).__init__(grid_size, N, m)
    self.board = Board(grid_size, N)
    self.current_player = self.player1

  def onclick(self, x, y):
    if self.game_over():
      return

    i, j = self.board.mouse_point_to_grid_index(x, y)
    step_valid, win = self.step(i, j, self.current_player)
    if step_valid:
      self.current_player = self.opponent_player(self.current_player)

    if self.game_over():
      print(self.game_over_text())
      self.draw_game_over_text()
