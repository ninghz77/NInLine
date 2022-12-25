from core.game_base import GameBase
from core.board import Board


class HumanVsHuman(GameBase):

  def __init__(
    self,
    grid_size,
    N,
    m,
    player1_desc="human",
    player2_desc="human",
  ):

    super(HumanVsHuman, self).__init__(grid_size, N, m)
    self.board = Board(
      grid_size,
      N,
      player1_desc=player1_desc,
      player2_desc=player2_desc,
    )
    self.current_player = self.player1
    self.in_click = False

  def onclick(self, x, y):
    if self.game_over() or self.in_click:
      return

    self.in_click = True
    i, j = self.board.mouse_point_to_grid_index(x, y)
    step_valid, win = self.step(i, j, self.current_player)
    if step_valid:
      self.current_player = self.opponent_player(self.current_player)
    self.board.draw_turn(self.current_player)

    if self.game_over():
      print(self.game_over_text())
      self.draw_game_over_text()

    self.in_click = False
