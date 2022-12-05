from core.comp_vs_comp import ComputerVsComputer
from scorers.scorer_base import StupidScorer, RandomScorer
from scorers.half_line_scorer import HalfLineScorer
from scorers.half_line_scorer2 import HalfLineScorer2


def Evaluate(N, m, num_races=1):
  scorers_cls = [HalfLineScorer, HalfLineScorer2]
  evaluator = Evaluator(N, m, scorers_cls, num_races)
  evaluator.evaluate()
  evaluator.display_stats()


class ScorerStats:

  def __init__(self, name):
    self.name = name
    self.rounds = 0
    self.win = 0
    self.lose = 0
    self.tie = 0
    self.crash = 0


class Evaluator:

  def __init__(
    self,
    N,
    m,
    scorers_cls,
    num_races=1,
  ):
    self.N = N
    self.m = m
    self.scorers_cls = scorers_cls
    self.num_races = num_races
    self.stats = {}

  def evaluate(self):
    n = len(self.scorers_cls)
    for i in range(n):
      for j in range(n):
        if i == j: continue
        for _ in range(self.num_races):
          self.evaluate_pair(self.scorers_cls[i], self.scorers_cls[j])

  def evaluate_pair(self, scorer_cls1, scorer_cls2):
    game = ComputerVsComputer(
      20,
      self.N,
      self.m,
      draw=False,
      player1_scorer_cls=scorer_cls1,
      player2_scorer_cls=scorer_cls2,
    )
    print("Race: player 1 ({}) vs player 2 ({})...".format(
      game.scorer1.name, game.scorer2.name))
    game.play()
    self.set_scorer_stats(game, game.player1)
    self.set_scorer_stats(game, game.player2)

  def opponent_player(self, player):
    if player == 0:
      return 0
    return 2 if player == 1 else 1

  def set_scorer_stats(self, game, player):
    scorer = game.scorer1 if player == game.player1 else game.scorer2
    if scorer.name not in self.stats.keys():
      self.stats[scorer.name] = ScorerStats(scorer.name)
    scorer_stats = self.stats[scorer.name]

    scorer_stats.rounds += 1
    if game.crashed_player != 0:
      if game.crashed_player == player:
        scorer_stats.crash += 1
      else:
        scorer_stats.win += 1
      return
    if game.winner == player:
      scorer_stats.win += 1
      return
    if game.winner == 0:
      scorer_stats.tie += 1
      return
    scorer_stats.lose += 1

  def display_stats(self):
    stats_list = [s for s in self.stats.values()]
    stats_list.sort(key=lambda x: x.win)
    print("-------------------------------------------------")
    print("Leading board")
    for s in stats_list:
      print("{}: win {}, tie {}, lose {}, crash {}, rounds {}".format(
        s.name, s.win, s.tie, s.lose, s.crash, s.rounds))
