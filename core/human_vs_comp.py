from core.game_base import GameBase
from core.board import Board
from scorers.scorer_base import ScorerBase
import traceback


class HumanVsComputer(GameBase):

  def __init__(
    self,
    grid_size,
    N,
    m,
    scorer_cls,
    who_first="computer",
    human_desc="human",
    computer_desc="computer",
  ):
    self.who_first = who_first
    if who_first == "computer":
      self.player1_scorer_cls = scorer_cls
      self.player2_scorer_cls = ScorerBase
      self.player1_desc = computer_desc
      self.player2_desc = human_desc
    else:
      self.player1_scorer_cls = ScorerBase
      self.player2_scorer_cls = scorer_cls
      self.player1_desc = human_desc
      self.player2_desc = computer_desc

    super(HumanVsComputer, self).__init__(
      grid_size,
      N,
      m,
      player1_scorer_cls=self.player1_scorer_cls,
      player2_scorer_cls=self.player2_scorer_cls,
    )
    self.start()

  def start(self):
    super().start()
    self.board = Board(
      self.grid_size,
      self.N,
      player1_desc=self.player1_desc,
      player2_desc=self.player2_desc,
    )

    if self.who_first == "computer":
      self.init_step(self.scorer1, self.player1)
      self.human = self.player2
      self.computer = self.player1
      self.board.draw_turn(self.human)
    else:
      self.human = self.player1
      self.computer = self.player2
    self.in_click = False

  def regret_two_steps(self):
    if len(self.steps) < 2:
      return
    self.regret_step()
    last_step = self.steps[-1]
    if last_step[0] == self.human:
      self.regret_step()

  def handle_butts(self, x, y):
    butt_clicked = False
    if self.board.in_steps_butt(x, y):
      self.print_steps()
      butt_clicked = True
    elif self.board.in_regret_butt(x, y):
      self.regret_two_steps()
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
    step_valid, win = self.step(i, j, self.human)

    if step_valid and not self.game_over():
      self.board.draw_turn(self.computer)
      try:
        i, j = self.player_best_grid(self.computer)
        step_valid, win = self.step(i, j, self.computer)
        if not step_valid:
          print("Computer cannot get valid step. Human player win!")
          self.winner = self.human
        self.board.draw_turn(self.human)
      except Exception as e:
        self.crashed_player = self.computer
        traceback.print_exc()

    if self.game_over():
      print(self.game_over_text())
      self.draw_game_over_text()

    self.in_click = False
