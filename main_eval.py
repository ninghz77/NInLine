import scorers.evaluator as evaluator


def run():
  N = 15
  m = 5

  evaluator.Evaluate(N, m, num_races=3)
