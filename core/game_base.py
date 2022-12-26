import numpy as np
from scorers.scorer_base import ScorerBase

class PlayerLog:
  def __init__(self, player):
    self.player = player
    self.used_time = 0
    self.num_steps = 0

  def print_log(self):
    print("Player {}: avg time {}, used time {}, num_steps {}".format(
      self.player, self.used_time / max(1, self.num_steps), self.used_time, self.num_steps
    ))
    
class GameBase:

  def __init__(
    self,
    grid_size,
    N,
    m,
    player1_scorer_cls=ScorerBase,
    player2_scorer_cls=ScorerBase,
  ):
    self.grid_size = grid_size
    self.N = N
    self.m = m
    self.player1 = 1
    self.player2 = 2
    self.winner = 0
    self.crashed_player = 0
    self.board = None
    self.player1_scorer_cls = player1_scorer_cls
    self.player2_scorer_cls = player2_scorer_cls
    
  def start(self):
    self.grids = np.zeros((self.N, self.N), dtype=np.int32)
    self.scorer1 = self.player1_scorer_cls(self.grids, self.m, self.player1)
    self.scorer2 = self.player2_scorer_cls(self.grids, self.m, self.player2)
    self.player_logs = [PlayerLog(self.player1), PlayerLog(self.player2)]
    self.steps = []

  def grid_valid(self, i, j):
    sz = self.grids.shape
    return i >= 0 and i < sz[0] and j >= 0 and j < sz[1] \
      and self.grids[i, j] == 0

  def get_player_log(self, player):
    return self.player_logs[player-1]
    
  def total_steps(self):
    return self.get_player_log(self.player1).num_steps + self.get_player_log(self.player2).num_steps
    
  def grids_full(self):
    return self.grids.size <= self.total_steps()

  def game_over(self):
    return self.winner != 0 or self.crashed_player != 0 or self.grids_full()

  def game_over_text(self):
    if self.crashed_player != 0:
      txt = "Player {} crashed!".format(self.crashed_player)
    else:
      txt = "Player {} win!".format(self.winner) \
        if self.winner != 0 else "Game is a tie"
    return txt

  def draw_game_over_text(self):
    if self.board:
      self.board.draw_game_over_text(
        self.game_over_text(),
        self.crashed_player if self.crashed_player != 0 else self.winner,
      )

  def opponent_player(self, player):
    if player == 0:
      return 0
    elif player == self.player1:
      return self.player2
    else:
      return self.player1

  def init_step(self, scorer, player):
    i, j = scorer.init_grid()
    step_valid, win = self.step(i, j, self.player1)
    if self.board and step_valid:
      self.board.draw_mark(i, j, self.player1)

  # return step_valid, win
  def step(self, i, j, player):
    if self.grid_valid(i, j):
      self.grids[i, j] = player
      self.steps.append((player, i, j))
      if self.board:
        self.board.draw_mark(i, j, player)

      self.get_player_log(player).num_steps += 1
      win = self.check_winner(player)
      if win:
        self.winner = player
      return True, win
    else:
      return False, False

  def player_best_grid(self, player):
    if self.grids_full():
      return -1, -1
    if player == self.player1:
      best_grid = self.scorer1.best_grid()
      return best_grid.grid
    elif player == self.player2:
      best_grid = self.scorer2.best_grid()
      return best_grid.grid
    else:
      raise ValueError("Invalid player id")

  def check_winner(self, player):
    sz = self.grids.shape

    for i in range(sz[0]):
      for j in range(sz[1]):
        if self.grids[i, j] != player:
          continue
        win = self.check_winner_at_grid(i, j, player)
        if win:
          return True
    return False

  def check_winner_at_grid(self, i, j, player):
    sz = self.grids.shape
    if i + self.m <= sz[0]:  # check column
      if self.check_line(self.grids[i:i + self.m, j], player):
        return True
    if j + self.m <= sz[1]:  # check row
      if self.check_line(self.grids[i, j:j + self.m], player):
        return True
    if i + self.m <= sz[0] and j + self.m <= sz[1]:  # check \
      line = [self.grids[i + k, j + k] for k in range(self.m)]
      if self.check_line(line, player):
        return True
    if i + self.m <= sz[0] and j + 1 >= self.m:  # check /
      line = [self.grids[i + k, j - k] for k in range(self.m)]
      if self.check_line(line, player):
        return True
    return False

  def check_line(self, line, player):
    for item in line:
      if item != player:
        return False
    return True

  def print_grids(self):
    sz = self.grids.shape
    for i in range(sz[0]):
      for j in range(sz[1]):
        print(self.grids[i, j], end='|')
      print()
    print()

  def print_logs(self):
    self.get_player_log(self.player1).print_log()    
    self.get_player_log(self.player2).print_log()
  
  def set_winner(self):
    if self.check_winner(self.player1):
      self.winner = self.player1
    elif self.check_winner(self.player2):
      self.winner = self.player2
    else:
      self.winner = 0

  def regret_step(self):
    if len(self.steps) < 1:
      return
    step = self.steps[-1]
    print("Regret: ", step)
    self.grids[step[1], step[2]] = 0
    if self.board:
      self.board.erase_mark(step[1], step[2])
    self.steps.pop()
    self.set_winner()

  def print_steps(self):
    print("Past steps:")
    print(self.steps)
