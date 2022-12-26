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
    self.player1_desc = player1_desc
    self.player2_desc = player2_desc
    self.start()

  def start(self):
    super().start()
    self.board = Board(
      self.grid_size,
      self.N,
      player1_desc=self.player1_desc,
      player2_desc=self.player2_desc,
    )
    self.current_player = self.player1
    self.in_click = False

  def regret_one_step(self):
    if len(self.steps) < 1:
      return
    self.regret_step()
    self.current_player = self.opponent_player(self.current_player)
    self.board.draw_turn(self.current_player)

  def handle_butts(self, x, y):
    butt_clicked = False
    if self.board.in_steps_butt(x, y):
      self.print_steps()
      butt_clicked = True
    elif self.board.in_regret_butt(x, y):
      self.regret_one_step()
      butt_clicked = True
    elif self.board.in_restart_butt(x, y):
      self.start()
      butt_clicked = True
    return butt_clicked

  def onclick(self, x, y):
    if self.in_click:
      return
    if (self.handle_butts(x, y)):
      return
    if self.game_over():
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
