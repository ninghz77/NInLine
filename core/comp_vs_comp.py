from core.board import Board
from core.game_base import GameBase
from scorers.scorer_base import ScorerBase
import time
import traceback

# player1 always steps first
class ComputerVsComputer(GameBase):

  def __init__(
    self,
    grid_size,
    N,
    m,
    draw=False,
    player1_scorer_cls=ScorerBase,
    player2_scorer_cls=ScorerBase,
  ):
    super(ComputerVsComputer, self).__init__(
      grid_size,
      N,
      m,
      player1_scorer_cls=player1_scorer_cls,
      player2_scorer_cls=player2_scorer_cls,
    )

    self.start()
    self.board = Board(
      grid_size,
      N,
      player1_desc=self.scorer1.name,
      player2_desc=self.scorer2.name,
    ) if draw else None
    self.init_step(self.scorer1, self.player1)

  def player_iterate(self, player):
    t0 = time.time()
    if self.game_over():
      return
    i, j = self.player_best_grid(player)
    step_valid, win = self.step(i, j, player)
    if not step_valid:
      self.winner = self.opponent_player(player)
      print("Player {} cannot get valid step.".format(player))
    self.get_player_log(player).used_time += time.time() - t0
    return step_valid

  def play(self):
    while not self.game_over():
      try:
        step_valid = self.player_iterate(self.player2)
        if not step_valid: break
      except Exception as e:
        self.crashed_player = self.player2
        traceback.print_exc()
        break

      try:
        self.player_iterate(self.player1)
        if not step_valid: break
      except Exception as e:
        self.crashed_player = self.player1
        traceback.print_exc()
        break

    if self.game_over():
      print(self.game_over_text())
      self.print_logs()
      self.draw_game_over_text()
